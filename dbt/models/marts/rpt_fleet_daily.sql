-- Fleet size and failures per day and drive type.
select
    drive_date,
    drive_type,
    count(*)                                    as drives_in_service,
    count(*) filter (where is_failure)          as failures
from {{ ref('fct_drive_day') }}
group by 1, 2
