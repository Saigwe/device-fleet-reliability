"""Write small Backblaze-format daily CSVs so CI exercises the real loader without the 1.3 GB download.

Same header layout as Drive Stats (including SMART columns this project ignores). Drives fail with
model- and age-dependent rates; a failed drive reports failure=1 on its last day and then disappears,
as in the real data. Failed drives show raised SMART 5/187/197 counts before failing.

Usage
    python tests/fixtures/make_backblaze_fixture.py --out data/fixture
"""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

MODELS = {  # model: (capacity TB, daily failure probability, share of fleet)
    "ST16000NM001G": (16, 0.00006, 0.35),
    "TOSHIBA MG08ACA16TA": (16, 0.00003, 0.25),
    "WDC WUH721816ALE6L4": (16, 0.00002, 0.20),
    "ST4000DM000": (4, 0.00012, 0.20),
}
EXTRA = ["is_legacy_format", "smart_1_normalized", "smart_1_raw", "smart_9_normalized", "smart_194_raw"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("data/fixture"))
    ap.add_argument("--drives", type=int, default=3000)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--seed", type=int, default=505)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    names = list(MODELS)
    model = rng.choice(names, args.drives, p=[MODELS[m][2] for m in names])
    drives = pd.DataFrame({
        "serial_number": [f"FX{i:07d}" for i in range(args.drives)],
        "model": model,
        "capacity_bytes": [MODELS[m][0] * 10**12 for m in model],
        "datacenter": rng.choice(["sac1", "phx1", "ams5"], args.drives),
        "cluster_id": rng.integers(1, 5, args.drives).astype(str),
        "vault_id": rng.integers(1000, 1100, args.drives).astype(str),
        "pod_id": rng.integers(1, 60, args.drives).astype(str),
        "hours0": rng.integers(100, 70000, args.drives),
        "alive": True,
    })
    base = np.array([MODELS[m][1] for m in model])
    args.out.mkdir(parents=True, exist_ok=True)
    start = dt.date(2026, 1, 1)
    for d in range(args.days):
        day = start + dt.timedelta(days=d)
        live = drives[drives.alive].copy()
        age_years = (live.hours0 + 24 * d) / 8760
        # bathtub: higher early-life and late-life failure
        p = base[live.index] * (1 + 3 * (age_years < 0.5) + 2 * np.clip(age_years - 5, 0, None))
        failed = rng.random(len(live)) < p * 20  # amplified so a small fixture has failures
        warn = failed | (rng.random(len(live)) < 0.01)
        out = pd.DataFrame({
            "date": day.isoformat(), "serial_number": live.serial_number, "model": live.model,
            "capacity_bytes": live.capacity_bytes, "failure": failed.astype(int),
            "datacenter": live.datacenter, "cluster_id": live.cluster_id, "vault_id": live.vault_id,
            "pod_id": live.pod_id, "pod_slot_num": rng.integers(0, 60, len(live)),
            "smart_5_raw": np.where(warn, rng.integers(1, 200, len(live)), 0),
            "smart_9_raw": live.hours0 + 24 * d,
            "smart_187_raw": np.where(failed, rng.integers(1, 50, len(live)), 0),
            "smart_188_raw": 0,
            "smart_197_raw": np.where(failed & (rng.random(len(live)) < 0.5), rng.integers(1, 30, len(live)), 0),
            "smart_198_raw": 0,
        })
        for c in EXTRA:
            out[c] = 0
        out.to_csv(args.out / f"{day.isoformat()}.csv", index=False)
        drives.loc[live.index[failed], "alive"] = False
    print(f"wrote {args.days} daily files for {args.drives} drives to {args.out}")


if __name__ == "__main__":
    main()
