# Ingestion (roadmap)

Loaders for the real data go here and write to the same `bronze` tables as the fixture.

Real data: [Backblaze hard-drive test data](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data), with daily status for 300k+ drives and a failure flag. Load part into Postgres and part into MongoDB to mirror mixed sources. CI uses a small synthetic fleet with the same shape.
