"""Load Backblaze Drive Stats daily CSVs into DuckDB `bronze.drive_days`.

Backblaze publishes one CSV per day with a row per drive in service: date, serial number, model,
capacity, a failure flag (1 on the drive's last day if it failed) and SMART statistics.
Source: https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data

Only the columns this project uses are loaded. Among the SMART stats, those are the five Backblaze
tracks as failure predictors (5, 187, 188, 197, 198) and power-on hours (9) as the drive's age.

Usage
    python ingestion/load_backblaze.py --db warehouse/fleet.duckdb --zip data/raw/data_Q1_2026.zip
    python ingestion/load_backblaze.py --db warehouse/fixture.duckdb --dir data/fixture
"""
from __future__ import annotations

import argparse
import time
import zipfile
from pathlib import Path

import duckdb

COLUMNS = {
    "date": "DATE", "serial_number": "VARCHAR", "model": "VARCHAR", "capacity_bytes": "BIGINT",
    "failure": "INTEGER", "datacenter": "VARCHAR", "cluster_id": "VARCHAR", "vault_id": "VARCHAR",
    "pod_id": "VARCHAR", "smart_9_raw": "DOUBLE", "smart_5_raw": "DOUBLE", "smart_187_raw": "DOUBLE",
    "smart_188_raw": "DOUBLE", "smart_197_raw": "DOUBLE", "smart_198_raw": "DOUBLE",
}


def extract(zip_path: Path) -> Path:
    out = zip_path.with_suffix("")
    if out.exists() and any(out.rglob("*.csv")):
        return out
    print(f"extracting {zip_path.name} -> {out}")
    with zipfile.ZipFile(zip_path) as z:
        members = [m for m in z.namelist() if m.endswith(".csv") and "__MACOSX" not in m]
        for m in members:
            z.extract(m, out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default="warehouse/fleet.duckdb")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--zip", type=Path)
    src.add_argument("--dir", type=Path)
    args = ap.parse_args()

    folder = extract(args.zip) if args.zip else args.dir
    files = sorted(p.as_posix() for p in folder.rglob("*.csv"))
    if not files:
        raise SystemExit(f"no CSV files under {folder}")

    t0 = time.perf_counter()
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    select = ",\n".join(f"    try_cast({c} as {t}) as {c}" for c, t in COLUMNS.items())
    with duckdb.connect(args.db) as con:
        con.execute("create schema if not exists bronze")
        con.execute(f"""
            create or replace table bronze.drive_days as
            select
{select},
                parse_filename(filename) as source_file
            from read_csv({files!r}, header = true, union_by_name = true, filename = true,
                          all_varchar = true)
        """)
        rows, days, drives, fails = con.execute("""
            select count(*), count(distinct date), count(distinct serial_number), sum(failure)
            from bronze.drive_days""").fetchone()
    print(f"bronze.drive_days {rows:,} rows | {len(files)} files, {days} days, {drives:,} drives, "
          f"{fails:,} failures | {time.perf_counter() - t0:.0f}s")


if __name__ == "__main__":
    main()
