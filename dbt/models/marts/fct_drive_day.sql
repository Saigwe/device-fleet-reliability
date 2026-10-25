-- One row per drive per day (grain: serial_number, drive_date), slimmed to what reliability reporting needs.
select
    d.drive_date,
    d.serial_number,
    d.model,
    m.manufacturer,
    m.drive_type,
    d.datacenter,
    cast(floor(d.age_years) as integer)     as age_year,
    d.is_failure
from {{ ref('stg_backblaze__drive_days') }} d
join {{ ref('dim_drive_model') }} m on m.model = d.model
