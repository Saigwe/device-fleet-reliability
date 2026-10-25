-- One row per device per day, with model, site and age; days after a device's first failure are excluded.
with days as (
    select
        d.device_id,
        d.status_date,
        d.failed,
        min(case when d.failed then d.status_date end) over (partition by d.device_id) as first_failure_date
    from {{ ref('stg_bronze__device_days') }} d
)

select
    days.device_id,
    days.status_date,
    dev.model,
    dev.site_id,
    {{ dbt.datediff('dev.install_date', 'days.status_date', 'day') }} / 365.25 as age_years,
    days.failed and days.status_date = days.first_failure_date as is_failure
from days
join {{ ref('stg_bronze__devices') }} dev on dev.device_id = days.device_id
where days.first_failure_date is null or days.status_date <= days.first_failure_date
