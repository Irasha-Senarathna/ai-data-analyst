with source as (
    select * from {{ source('open_meteo', 'open_meteo_weather_daily') }}
),

renamed as (
    select
        state || '-' || strftime(weather_date, '%Y-%m-%d') as weather_key,
        state,
        weather_date,
        temperature_2m_max as temp_max_c,
        temperature_2m_min as temp_min_c,
        precipitation_sum as precipitation_mm
    from source
),

final as (
    select * from renamed
)

select * from final
