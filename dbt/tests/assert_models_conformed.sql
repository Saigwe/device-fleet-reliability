-- Conformed model keys: no model name in silver may be a bare WDC part number (it must carry "WDC ").
select distinct model from {{ ref('stg_backblaze__drive_days') }} where model like 'WUH%'
