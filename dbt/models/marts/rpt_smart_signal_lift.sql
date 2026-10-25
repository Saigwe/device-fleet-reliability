-- Which SMART statistics warn of failure? For each one: the share of failed drives showing a non-zero
-- value on their last day, vs the share of surviving drives on their last observed day, and the lift.
{% set stats = {'reallocated_sectors': 'SMART 5', 'reported_uncorrectable': 'SMART 187',
                'command_timeouts': 'SMART 188', 'pending_sectors': 'SMART 197',
                'offline_uncorrectable': 'SMART 198'} %}
with last_day as (
    select d.*
    from {{ ref('stg_backblaze__drive_days') }} d
    join {{ ref('dim_drive_model') }} m on m.model = d.model and m.drive_type = 'hdd'
    qualify row_number() over (partition by d.serial_number order by d.drive_date desc) = 1
),

shares as (
    {% for col, label in stats.items() %}
    select
        '{{ label }}'                                                       as smart_stat,
        '{{ col }}'                                                         as column_name,
        avg(case when {{ col }} > 0 then 1.0 else 0 end) filter (where is_failure)     as share_failed,
        avg(case when {{ col }} > 0 then 1.0 else 0 end) filter (where not is_failure) as share_surviving
    from last_day
    {% if not loop.last %}union all{% endif %}
    {% endfor %}
)

select
    *,
    share_failed / nullif(share_surviving, 0) as lift
from shares
