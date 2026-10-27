with weather as (
    select * from {{ ref('stg_open_meteo__weather_daily') }}
),

states as (
    select * from {{ ref('brazil_states') }}
),

final as (
    select
        weather.weather_key,
        weather.state,
        states.region,
        weather.weather_date,
        weather.temp_max_c,
        weather.temp_min_c,
        weather.precipitation_mm,
        weather.precipitation_mm >= 1.0 as is_rainy_day
    from weather
    left join states
        on weather.state = states.state
)

select * from final
