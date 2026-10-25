-- AFR by drive age (whole years of power-on time) for hard drives: the "bathtub curve" view.
select
    least(age_year, 10)                                         as age_year,
    case when age_year >= 10 then '10+' else cast(age_year as varchar) end as age_label,
    count(distinct serial_number)                               as drives,
    count(*)                                                    as drive_days,
    count(*) filter (where is_failure)                          as failures,
    {{ afr('count(*) filter (where is_failure)', 'count(*)') }} as afr_pct
from {{ ref('fct_drive_day') }}
where drive_type = 'hdd' and age_year is not null
group by 1, 2
