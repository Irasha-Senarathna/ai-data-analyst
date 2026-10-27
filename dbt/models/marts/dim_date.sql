-- One row per calendar day of the dataset, with Brazilian holidays and Black Friday.
with days as (
    select cast(day as date) as date_day
    from generate_series(date '2016-09-01', date '2018-10-31', interval 1 day) as t(day)
),

holidays as (
    select * from {{ ref('brazil_holidays') }}
),

final as (
    select
        days.date_day,
        year(days.date_day) as year,
        quarter(days.date_day) as quarter,
        month(days.date_day) as month,
        monthname(days.date_day) as month_name,
        strftime(days.date_day, '%Y-%m') as year_month,
        cast(date_trunc('week', days.date_day) as date) as week_start,
        isodow(days.date_day) as day_of_week,
        dayname(days.date_day) as day_name,
        isodow(days.date_day) in (6, 7) as is_weekend,
        holidays.holiday_date is not null as is_holiday,
        holidays.holiday_name,
        holidays.holiday_type,
        month(days.date_day) = 11
            and isodow(days.date_day) = 5
            and day(days.date_day) between 22 and 28 as is_black_friday
    from days
    left join holidays
        on days.date_day = holidays.holiday_date
)

select * from final
