PY ?= python
DB ?= warehouse/fleet.duckdb
QUARTER ?= Q1_2026
ZIP = data/raw/data_$(QUARTER).zip
FIXTURE_DB ?= warehouse/fixture.duckdb
DBT = cd dbt && DUCKDB_PATH=../$(DB) dbt

.PHONY: all fixture-all download bronze bronze-fixture dbt survival profile docs clean

all: download bronze dbt survival profile docs           ## real Backblaze quarter (1.3 GB download)
fixture-all:                                             ## Backblaze-format fixture, no download (CI)
	$(PY) tests/fixtures/make_backblaze_fixture.py --out data/fixture
	$(PY) ingestion/load_backblaze.py --db $(FIXTURE_DB) --dir data/fixture
	$(MAKE) dbt docs DB=$(FIXTURE_DB)
	$(PY) analysis/survival.py --db $(FIXTURE_DB) --out warehouse/fixture_results
	$(PY) scripts/profile_source.py --db $(FIXTURE_DB) --out warehouse/fixture_profile.md

download:
	mkdir -p data/raw
	test -f $(ZIP) || curl -fL -o $(ZIP) https://f001.backblazeb2.com/file/Backblaze-Hard-Drive-Data/data_$(QUARTER).zip

bronze:
	$(PY) ingestion/load_backblaze.py --db $(DB) --zip $(ZIP)

dbt:
	$(DBT) build --profiles-dir .

survival:
	$(PY) analysis/survival.py --db $(DB)

profile:
	$(PY) scripts/profile_source.py --db $(DB)

docs:   # catalogue and lineage (open with: cd dbt && dbt docs serve)
	$(DBT) docs generate --profiles-dir .

clean:
	rm -rf warehouse dbt/target dbt/logs data/fixture
