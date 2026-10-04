"""Verify the raw REES46 event files and build the playbook's user sample.

The source data is "eCommerce Events History in Cosmetics Shop" (Michael
Kechinov, REES46 Marketing Platform), published on Kaggle under "Data files ©
Original Authors". That is not an open licence, so the files are never
committed. To reproduce:

1. Download the five monthly CSVs (2019-Oct ... 2020-Feb) from
   https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop
   (a free Kaggle account is needed).
2. Put them in data/raw/.
3. Run: python data/get_data.py

The script checks each file's SHA-256, keeps a deterministic 10% sample of
users (all of their events), and writes data/processed/events_sample.parquet.
It does NOT clean anything: duplicates, missing values and odd prices are left
in on purpose, because Module 1 audits them.
"""
import hashlib
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE / "processed" / "events_sample.parquet"

FILES = {
    "2019-Oct.csv": "d87b1124a003151592e722996c6295aba2d286626c5db624c49d749877478c23",
    "2019-Nov.csv": "25b03eea9020a64f97659a4cbce9d801ca81872910ce72348bfa607817539755",
    "2019-Dec.csv": "ebf98f504e238109efa406d26a26a90e0d467faa938bf96b68e3fea663d2008e",
    "2020-Jan.csv": "c6d8d6bdcf0b6bccb61a14447afdca08e95683f34f279befb1ac580ddc214853",
    "2020-Feb.csv": "605c76fd75b01b9b60d1ae5f412d2a774158fdd18e0a95377b3c547a556f1c1b",
}

# Chosen sample size: 10% of users keeps every notebook fast on a laptop while
# leaving tens of thousands of buyers. Users are picked by a fixed
# multiplicative hash of user_id (Knuth's constant), so the sample is the same
# on every machine and does not depend on how user ids were assigned.
SAMPLE_PCT = 10
HASH_MULT = 2654435761


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def in_sample(user_id: pd.Series) -> pd.Series:
    return (user_id.astype("uint64") * HASH_MULT) % (2**32) % 100 < SAMPLE_PCT


def main() -> None:
    parts = []
    for name, expected in FILES.items():
        path = RAW / name
        if not path.exists():
            raise FileNotFoundError(f"{path} missing; see the docstring for download steps")
        if sha256(path) != expected:
            raise ValueError(f"{name}: checksum mismatch, not the published file")
        d = pd.read_csv(path, dtype={"user_session": "string", "brand": "string",
                                     "category_code": "string", "event_type": "string"})
        kept = d[in_sample(d["user_id"])]
        print(f"{name}: {len(d):,} rows, kept {len(kept):,} ({len(kept)/len(d):.1%})")
        parts.append(kept)

    events = pd.concat(parts, ignore_index=True)
    events["event_time"] = pd.to_datetime(events["event_time"], format="%Y-%m-%d %H:%M:%S UTC")
    events["event_type"] = events["event_type"].astype("category")
    OUT.parent.mkdir(exist_ok=True)
    events.to_parquet(OUT, index=False)
    print(f"sample: {len(events):,} rows, {events['user_id'].nunique():,} users -> {OUT}")

    # Also write the SQLite file for running the SQL/ queries in an editor.
    import sys
    sys.path.insert(0, str(HERE.parent))
    from common import build_sqlite
    print(f"database -> {build_sqlite()}")


if __name__ == "__main__":
    main()
