-- Annualised failure rate and failures per 1,000 drives by model, for hard drives (boot SSDs excluded,
-- as in Backblaze's own HDD reports). meets_reporting_threshold mirrors Backblaze's publication rule.
with agg as (
    select
        model,
        count(distinct serial_number)                       as drives,
        count(*)                                            as drive_days,
        count(*) filter (where is_failure)                  as failures
    from {{ ref('fct_drive_day') }}
    where drive_type = 'hdd'
    group by 1
)

select
    a.model,
    m.manufacturer,
    m.capacity_tb,
    a.drives,
    a.drive_days,
    a.failures,
    {{ afr('a.failures', 'a.drive_days') }}                 as afr_pct,
    {{ afr_ci('a.failures', 'a.drive_days', 'low') }}       as afr_ci_low_pct,
    {{ afr_ci('a.failures', 'a.drive_days', 'high') }}      as afr_ci_high_pct,
    1000.0 * a.failures / a.drives                          as failures_per_1000_drives,
    a.drives >= {{ var('min_drives_for_reporting') }}
        and a.drive_days >= {{ var('min_drive_days_for_reporting') }} as meets_reporting_threshold
from agg a
join {{ ref('dim_drive_model') }} m on m.model = a.model
