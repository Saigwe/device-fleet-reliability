select
    manufacturer,
    count(distinct model)                                       as models,
    count(distinct serial_number)                               as drives,
    count(*)                                                    as drive_days,
    count(*) filter (where is_failure)                          as failures,
    {{ afr('count(*) filter (where is_failure)', 'count(*)') }} as afr_pct
from {{ ref('fct_drive_day') }}
where drive_type = 'hdd'
group by 1
