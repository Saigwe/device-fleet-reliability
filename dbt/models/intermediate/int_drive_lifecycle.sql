-- One row per drive (serial number): when it was observed, its age at entry and exit (power-on hours),
-- and whether and when it failed. This is the input to the survival analysis.
select
    serial_number,
    arg_max(model, drive_date)                                  as model,
    min(drive_date)                                             as first_date,
    max(drive_date)                                             as last_date,
    count(*)                                                    as days_observed,
    bool_or(is_failure)                                         as failed,
    min(case when is_failure then drive_date end)               as failure_date,
    min(power_on_hours) / 24.0                                  as age_at_entry_days,
    max(power_on_hours) / 24.0                                  as age_at_exit_days
from {{ ref('stg_backblaze__drive_days') }}
group by 1
