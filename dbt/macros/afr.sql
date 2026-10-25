{# Annualised failure rate (%), Backblaze's definition: failures / (drive days / 365) x 100.
   ci_low / ci_high: approximate 95% interval treating failures as Poisson (normal approximation). #}
{% macro afr(failures, drive_days) -%}
    100.0 * {{ failures }} / nullif({{ drive_days }} / 365.0, 0)
{%- endmacro %}

{% macro afr_ci(failures, drive_days, side) -%}
    greatest(0, 100.0 * ({{ failures }} {{ '-' if side == 'low' else '+' }} 1.96 * sqrt({{ failures }}))
                / nullif({{ drive_days }} / 365.0, 0))
{%- endmacro %}
