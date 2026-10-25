-- Annualised failure rate (AFR) and failures per 1,000 units, by model.
select
    model,
    count(distinct device_id)                                                   as devices,
    count(*)                                                                    as device_days,
    sum(case when is_failure then 1 else 0 end)                                 as failures,
    100.0 * sum(case when is_failure then 1 else 0 end) / count(*) * 365        as afr_pct,
    1000.0 * sum(case when is_failure then 1 else 0 end) / count(distinct device_id) as failures_per_1000_units
from {{ ref('fct_device_day') }}
group by 1
