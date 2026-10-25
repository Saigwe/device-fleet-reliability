# Ingestion

`load_backblaze.py` loads [Backblaze Drive Stats](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data) daily CSVs into `bronze.drive_days`:
- it extracts the quarterly zip if needed
- it reads every daily file with DuckDB (`union_by_name`, so header differences across quarters are tolerated)
- it keeps only the 15 columns this project uses

`make download` fetches a quarter from Backblaze's public bucket (`QUARTER=Q1_2026` by default, 1.31 GB). The raw files are gitignored.

CI never downloads anything. It writes Backblaze-format CSVs with `tests/fixtures/make_backblaze_fixture.py` and runs the same loader on them.
