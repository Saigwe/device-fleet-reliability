"""Kaplan-Meier survival curves and a next-quarter replacement forecast for the hard-drive fleet.

Age is power-on time (SMART 9), because the data has no install date. Drives enter the quarter already
aged, so the fit uses left truncation (`entry` = age when first seen): a drive only counts as at risk
from the age it was observed at. Without that, survival would be overstated (survivorship bias).

Outputs
- results/survival_by_manufacturer.png : survival curves by manufacturer
- results/survival.md                  : survival at 1-8 years, and the replacement forecast
- warehouse table analysis.eol_forecast : expected failures next quarter per model

Usage
    python analysis/survival.py --db warehouse/fleet.duckdb
"""
from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import matplotlib
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter
from lifelines.exceptions import StatError

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
HORIZON_DAYS = 90
MIN_FAILURES_FOR_MODEL_CURVE = 10


def fit(df: pd.DataFrame, label: str) -> KaplanMeierFitter:
    kmf = KaplanMeierFitter(label=label)
    kmf.fit(durations=df["exit"], event_observed=df["failed"], entry=df["entry"])
    return kmf


def conditional_failure(kmf: KaplanMeierFitter, age: np.ndarray, horizon: float) -> np.ndarray:
    """P(fail within `horizon` days | alive at `age`) = 1 - S(age + horizon) / S(age)."""
    s_now = kmf.survival_function_at_times(age).to_numpy()
    s_later = kmf.survival_function_at_times(age + horizon).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        p = 1 - np.where(s_now > 0, s_later / s_now, 1.0)
    return np.clip(np.nan_to_num(p), 0, 1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default="warehouse/fleet.duckdb")
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(args.db, read_only=True) as con:
        drives = con.execute("""
            select l.serial_number, l.model, m.manufacturer, l.failed, l.last_date,
                   l.age_at_entry_days as entry, l.age_at_exit_days + 1 as exit
            from silver.int_drive_lifecycle l
            join gold.dim_drive_model m on m.model = l.model
            where m.drive_type = 'hdd' and l.age_at_entry_days is not null and l.age_at_exit_days is not null
        """).df()
        quarter_end = con.execute("select max(drive_date) from gold.fct_drive_day").fetchone()[0]
    drives["failed"] = drives["failed"].astype(bool)
    drives = drives[drives["exit"] > drives["entry"]]

    fleet = fit(drives, "All hard drives")
    years = np.arange(1, 9)
    table = {"All hard drives": fleet.survival_function_at_times(years * 365).to_numpy()}
    fig, ax = plt.subplots(figsize=(8, 5))
    curves = {}
    for mfr, grp in drives.groupby("manufacturer"):
        if grp["failed"].sum() < MIN_FAILURES_FOR_MODEL_CURVE:
            continue
        curves[mfr] = fit(grp, mfr)
        table[mfr] = curves[mfr].survival_function_at_times(years * 365).to_numpy()
        curves[mfr].plot_survival_function(ax=ax, ci_show=False)
    ax.set_xlabel("Age (days of power-on time)")
    ax.set_ylabel("Share of drives still working")
    ax.set_xlim(0, 8 * 365)
    ax.set_title("Hard-drive survival by manufacturer (Kaplan-Meier, left-truncated)")
    fig.tight_layout()
    fig.savefig(out / "survival_by_manufacturer.png", dpi=130)

    # Forecast: drives still in service at quarter end, each with its own conditional failure probability.
    alive = drives[(~drives["failed"]) & (pd.to_datetime(drives["last_date"]) == pd.Timestamp(quarter_end))].copy()
    alive["p_fail_next_q"] = 0.0
    alive["curve"] = ""
    for model, grp in alive.groupby("model"):
        hist = drives[drives["model"] == model]
        mfr = grp["manufacturer"].iloc[0]
        kmf, curve = curves.get(mfr, fleet), "manufacturer"
        if hist["failed"].sum() >= MIN_FAILURES_FOR_MODEL_CURVE:
            try:  # a model with too few young drives can't support its own left-truncated curve
                kmf, curve = fit(hist, model), "model"
            except StatError:
                pass
        alive.loc[grp.index, "p_fail_next_q"] = conditional_failure(kmf, grp["exit"].to_numpy(), HORIZON_DAYS)
        alive.loc[grp.index, "curve"] = curve

    forecast = (alive.groupby(["model", "manufacturer", "curve"])
                     .agg(drives_in_service=("serial_number", "size"),
                          median_age_years=("exit", lambda s: round(float(np.median(s)) / 365, 1)),
                          expected_failures_next_quarter=("p_fail_next_q", "sum"))
                     .reset_index()
                     .sort_values("expected_failures_next_quarter", ascending=False))
    forecast["expected_failures_next_quarter"] = forecast["expected_failures_next_quarter"].round(1)
    forecast["per_1000_drives"] = (1000 * forecast["expected_failures_next_quarter"]
                                   / forecast["drives_in_service"]).round(2)

    with duckdb.connect(args.db) as con:
        con.execute("create schema if not exists analysis")
        con.register("f", forecast)
        con.execute("create or replace table analysis.eol_forecast as select * from f")

    surv = pd.DataFrame(table, index=[f"{y} yr" for y in years]).T.round(3)
    observed = int(drives["failed"].sum())
    lines = [
        "# Survival and replacement forecast",
        "",
        f"Hard drives with power-on hours: {len(drives):,}; failures this quarter: {observed:,}. "
        f"Quarter ends {quarter_end}.",
        "",
        "## Share of drives still working at each age (Kaplan-Meier, left-truncated)",
        "",
        surv.to_markdown(),
        "",
        f"## Expected failures in the next {HORIZON_DAYS} days, by model (top 15)",
        "",
        f"Drives in service at quarter end: {len(alive):,}. "
        f"Expected failures next quarter, whole fleet: **{forecast['expected_failures_next_quarter'].sum():,.0f}**.",
        "",
        forecast.head(15).to_markdown(index=False),
    ]
    (out / "survival.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
