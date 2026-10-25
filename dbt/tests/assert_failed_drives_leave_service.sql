-- Source data quality (warn, not fail): Backblaze removes a drive after it fails, so a drive should not
-- report again after its failure date. Any that do are listed for follow-up rather than silently counted.
{{ config(severity='warn') }}
select l.serial_number, l.failure_date, l.last_date
from {{ ref('int_drive_lifecycle') }} l
where l.failed and l.last_date > l.failure_date
