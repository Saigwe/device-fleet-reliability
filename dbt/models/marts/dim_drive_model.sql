-- One row per drive model: manufacturer and drive type from the longest matching model prefix (seed),
-- typical capacity, and fleet size.
with models as (
    select
        model,
        mode(capacity_tb)               as capacity_tb,
        count(distinct serial_number)   as drives,
        min(drive_date)                 as first_seen,
        max(drive_date)                 as last_seen
    from {{ ref('stg_backblaze__drive_days') }}
    group by 1
),

matched as (
    select
        m.*,
        p.manufacturer,
        p.drive_type,
        row_number() over (partition by m.model order by length(p.prefix) desc) as rn
    from models m
    left join {{ ref('model_prefixes') }} p on starts_with(m.model, p.prefix)
)

select
    model,
    coalesce(manufacturer, 'Other')     as manufacturer,
    coalesce(drive_type, 'hdd')         as drive_type,
    capacity_tb,
    drives,
    first_seen,
    last_seen
from matched
where rn = 1
