select
    site_id,
    region
from {{ source('bronze', 'sites') }}
