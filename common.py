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


def load_events() -> pd.DataFrame:
    if not SAMPLE.exists():
        raise FileNotFoundError("Run `python data/get_data.py` first (see its docstring).")
    return pd.read_parquet(SAMPLE)


def connect(events: pd.DataFrame | None = None) -> sqlite3.Connection:
    """Load the raw events into SQLite and create the semantic-layer views."""
    e = load_events() if events is None else events
    con = sqlite3.connect(":memory:")
    raw = e.assign(event_time=e["event_time"].dt.strftime("%Y-%m-%d %H:%M:%S"),
                   event_type=e["event_type"].astype(str))
    raw.to_sql("events", con, index=False)
    con.executescript((LAYER / "views.sql").read_text())
    return con


def build_sqlite(path: Path = ROOT / "data" / "processed" / "playbook.sqlite") -> Path:
    """Write the database to a file for a SQL editor (e.g. VS Code's SQLite extension).

    The semantic-layer views are stored as real tables there, so queries run fast
    and GUI clients show results reliably. Rebuild it after changing views.sql.
    """
    mem = connect()
    path.unlink(missing_ok=True)
    disk = sqlite3.connect(path)
    mem.backup(disk)
    views = [r[0] for r in disk.execute("SELECT name FROM sqlite_master WHERE type = 'view'")]
    for v in views:  # copy all first: the views depend on each other
        disk.execute(f"CREATE TABLE {v}_t AS SELECT * FROM {v}")
    for v in views:
        disk.execute(f"DROP VIEW {v}")
    for v in views:
        disk.execute(f"ALTER TABLE {v}_t RENAME TO {v}")
    for table in ["events", "events_clean"]:
        disk.execute(f"CREATE INDEX idx_{table}_type_date ON {table} (event_type, event_time)")
    disk.commit()
    for v in views:
        assert disk.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0] == mem.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0], v
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


def show(df: pd.DataFrame, index: bool = False) -> None:
    """Print a table with text columns left-aligned and numeric columns right-aligned."""
    import re
    if index:
        df = df.reset_index()
    numeric = re.compile(r"^[-+−]?[\d,]*\.?\d+%?$")
    cols = [str(c) for c in df.columns]
    cells = [[str(v) for v in df[c]] for c in df.columns]
    is_text = [not all(numeric.match(v) for v in col) for col in cells]
    widths = [max([len(h)] + [len(v) for v in col]) for h, col in zip(cols, cells)]
    pad = lambda s, w, left: s.ljust(w) if left else s.rjust(w)
    print("  ".join(pad(h, w, t) for h, w, t in zip(cols, widths, is_text)).rstrip())
    for r in range(len(df)):
        print("  ".join(pad(col[r], w, t) for col, w, t in zip(cells, widths, is_text)).rstrip())
