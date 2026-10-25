select
    device_id,
    site_id,
    model,
    cast(install_date as date)           as install_date
from {{ source('bronze', 'devices') }}
