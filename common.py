"""Shared loaders and the semantic layer for every module.

load_events()   the sampled raw event log (built by data/get_data.py), uncleaned
connect()       an in-memory SQLite database: raw `events` table + the views in
                semantic_layer/views.sql
metric()        compute one metric from semantic_layer/metrics.json for a period
"""
import json
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT / "data" / "processed" / "events_sample.parquet"
LAYER = ROOT / "semantic_layer"

# Chart palette: reference categorical slots (same as the earlier playbooks).
BLUE, ORANGE, AQUA, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#888888"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.25, "figure.dpi": 110})

# Every chart image gets a thin black frame (shared with the other repos: chart_style.py).
import chart_style  # noqa: E402,F401


def load_events() -> pd.DataFrame:
    if not SAMPLE.exists():
        raise FileNotFoundError("Run `python data/get_data.py` first (see its docstring).")
    return pd.read_parquet(SAMPLE)


def _materialize(con: sqlite3.Connection) -> None:
    """Store every view as a real table (same name, same rows), then index the big tables.

    A view re-runs its query on every use; events_clean's DISTINCT over 2M rows made
    each query slow. Tables are computed once.
    """
    views = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'view'")]
    counts = {v: con.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0] for v in views}
    for v in views:  # copy all first: the views depend on each other
        con.execute(f"CREATE TABLE {v}_t AS SELECT * FROM {v}")
    for v in views:
        con.execute(f"DROP VIEW {v}")
    for v in views:
        con.execute(f"ALTER TABLE {v}_t RENAME TO {v}")
        assert con.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0] == counts[v], v
    for table in ["events", "events_clean"]:
        con.execute(f"CREATE INDEX idx_{table}_type_date ON {table} (event_type, event_time)")
        con.execute(f"CREATE INDEX idx_{table}_user ON {table} (user_id)")
    con.execute("CREATE INDEX idx_orders_user ON orders (user_id)")
    con.commit()


def connect(events: pd.DataFrame | None = None) -> sqlite3.Connection:
    """Load the raw events into SQLite and build the semantic-layer tables from views.sql."""
    e = load_events() if events is None else events
    con = sqlite3.connect(":memory:")
    raw = e.assign(event_time=e["event_time"].dt.strftime("%Y-%m-%d %H:%M:%S"),
                   event_type=e["event_type"].astype(str))
    raw.to_sql("events", con, index=False)
    con.executescript((LAYER / "views.sql").read_text())
    _materialize(con)
    return con


def build_sqlite(path: Path = ROOT / "data" / "processed" / "playbook.sqlite") -> Path:
    """Write the database to a file for a SQL editor (e.g. VS Code's SQLite extension).

    Rebuild it after changing views.sql.
    """
    mem = connect()
    path.unlink(missing_ok=True)
    disk = sqlite3.connect(path)
    mem.backup(disk)
    disk.close()
    return path


def metric_definitions() -> dict:
    return json.loads((LAYER / "metrics.json").read_text())["metrics"]


def metric(con: sqlite3.Connection, name: str, start: str = "2019-10-01", end: str = "2020-02-29") -> float:
    """One metric for event dates start..end inclusive (YYYY-MM-DD)."""
    where = f"event_date BETWEEN '{start}' AND '{end}'"
    sql = metric_definitions()[name]["sql"].format(where=where)
    return con.execute(sql).fetchone()[0]


def query(con: sqlite3.Connection, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, con)


def funnel_chart(stages: pd.Series, title: str, base: str, no_data: list | None = None) -> None:
    """Funnel in the playbook's style (first used in Module 2).

    stages: ordered counts, index = stage names. base: name of the first stage's unit,
    used in "% of <base>". no_data: extra stage names shown as "no data".
    """
    from matplotlib.patches import Polygon
    no_data = no_data or []
    n = len(stages) + len(no_data)
    fig = plt.figure(figsize=(7.5, 0.8 + 0.85 * n))
    ax = fig.add_axes([0.02, 0.05, 0.96, 0.85])
    ramp = ["#184f95", "#2a78d6", "#6da7ec", "#b7d3f6"]
    top = stages.iloc[0]
    widths = [max(v / top, 0.06) for v in stages.values]
    h, gap = 0.8, 0.35
    for k, ((name, v), w) in enumerate(zip(stages.items(), widths)):
        y0 = -k * (h + gap)
        ax.add_patch(plt.Rectangle((-w / 2, y0 - h), w, h, color=ramp[k % len(ramp)]))
        ax.text(-0.53, y0 - h / 2, name, ha="right", va="center", fontsize=9, color="#333333")
        prev = "" if k == 0 else f"\n{v / stages.iloc[k - 1]:.2%} of previous step"
        label = f"{v:,}\n{v / top:.2%} of {base}{prev}"
        if w >= 0.6:
            ax.text(0, y0 - h / 2, label, ha="center", va="center", fontsize=9, color="white", fontweight="bold")
        else:
            ax.text(w / 2 + 0.02, y0 - h / 2, label, ha="left", va="center", fontsize=9, color="#222222", fontweight="bold")
        if k < len(stages) - 1:
            wn = widths[k + 1]
            ax.add_patch(Polygon([(-w / 2, y0 - h), (w / 2, y0 - h), (wn / 2, y0 - h - gap), (-wn / 2, y0 - h - gap)],
                                 color="#e4e4e0"))
    for j, name in enumerate(no_data):
        y0 = -(len(stages) + j) * (h + gap)
        ax.text(-0.53, y0 - h / 2, name, ha="right", va="center", fontsize=9, color="#333333")
        ax.text(0, y0 - h / 2, "no data", ha="center", va="center", fontsize=9, color="#555555", style="italic")
    ax.set_xlim(-1.05, 0.55); ax.set_ylim(-n * (h + gap) + gap - 0.05, 0.05)
    ax.axis("off")
    ax.set_title(title, fontsize=10, loc="left")
    plt.show()


def show(df: pd.DataFrame, index: bool = False) -> None:
    """Print a table with text columns left-aligned and numeric columns right-aligned."""
    import re
    if index:
        df = df.reset_index()
    numeric = re.compile(r"^[-+−]?[\d,]*\.?\d+%?$")
    cols = [str(c) for c in df.columns]
    cells = [[str(v) for v in df[c]] for c in df.columns]
    blank = {"n/a", "no data", "—", ""}
    is_text = [not all(numeric.match(v) or v in blank for v in col) or all(v in blank for v in col) for col in cells]
    widths = [max([len(h)] + [len(v) for v in col]) for h, col in zip(cols, cells)]
    pad = lambda s, w, left: s.ljust(w) if left else s.rjust(w)
    print("  ".join(pad(h, w, t) for h, w, t in zip(cols, widths, is_text)).rstrip())
    for r in range(len(df)):
        print("  ".join(pad(col[r], w, t) for col, w, t in zip(cells, widths, is_text)).rstrip())
