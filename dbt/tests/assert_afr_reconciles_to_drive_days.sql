-- The model, age and manufacturer reports must each add up to the same hard-drive totals as the fact.
-- (Age excludes rows without power-on hours, so it is compared with the same filter.)
with fact as (
    select
        count(*)                                                    as drive_days,
        count(*) filter (where is_failure)                          as failures,
        count(*) filter (where age_year is not null)                as aged_days,
        count(*) filter (where is_failure and age_year is not null) as aged_failures
    from {{ ref('fct_drive_day') }}
    where drive_type = 'hdd'
),

by_model as (select sum(drive_days) as d, sum(failures) as f from {{ ref('rpt_afr_by_model') }}),
by_mfr as (select sum(drive_days) as d, sum(failures) as f from {{ ref('rpt_afr_by_manufacturer') }}),
by_age as (select sum(drive_days) as d, sum(failures) as f from {{ ref('rpt_afr_by_age') }})

select 'by model' as report from fact, by_model where by_model.d <> fact.drive_days or by_model.f <> fact.failures
union all
select 'by manufacturer' from fact, by_mfr where by_mfr.d <> fact.drive_days or by_mfr.f <> fact.failures
union all
select 'by age' from fact, by_age where by_age.d <> fact.aged_days or by_age.f <> fact.aged_failures
