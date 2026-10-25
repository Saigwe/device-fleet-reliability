-- The confidence interval must contain the point estimate, and rates can't be negative.
select model, afr_ci_low_pct, afr_pct, afr_ci_high_pct
from {{ ref('rpt_afr_by_model') }}
where afr_pct < 0 or afr_ci_low_pct > afr_pct or afr_ci_high_pct < afr_pct
