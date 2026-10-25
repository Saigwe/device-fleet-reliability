-- Failures can't exceed devices, and AFR must be a valid percentage.
select *
from {{ ref('rpt_failure_rate_by_model') }}
where failures > devices or afr_pct < 0 or afr_pct > 100
