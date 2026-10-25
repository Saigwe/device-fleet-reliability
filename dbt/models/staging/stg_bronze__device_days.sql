select
    device_id,
    cast(status_date as date)           as status_date,
    failed
from {{ source('bronze', 'device_days') }}
