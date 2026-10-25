-- Typed, renamed drive-days. Capacity below zero (Backblaze's "unknown") becomes null.
-- Model names are conformed: some WDC drives report their model without the "WDC " prefix
-- (e.g. WUH721816ALE6L4), which would otherwise split one model in two. raw_model keeps the original.
select
    date                                                    as drive_date,
    serial_number,
    case when trim(model) like 'WUH%' then 'WDC ' || trim(model) else trim(model) end as model,
    model                                                   as raw_model,
    case when capacity_bytes > 0 then round(capacity_bytes / 1e12, 1) end as capacity_tb,
    failure = 1                                             as is_failure,
    datacenter,
    cluster_id,
    vault_id,
    pod_id,
    smart_9_raw                                             as power_on_hours,
    smart_9_raw / 8760.0                                    as age_years,
    coalesce(smart_5_raw, 0)                                as reallocated_sectors,        -- SMART 5
    coalesce(smart_187_raw, 0)                              as reported_uncorrectable,     -- SMART 187
    coalesce(smart_188_raw, 0)                              as command_timeouts,           -- SMART 188
    coalesce(smart_197_raw, 0)                              as pending_sectors,            -- SMART 197
    coalesce(smart_198_raw, 0)                              as offline_uncorrectable       -- SMART 198
from {{ source('bronze', 'drive_days') }}
where serial_number is not null and date is not null
