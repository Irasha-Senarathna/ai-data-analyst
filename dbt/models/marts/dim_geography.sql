with states as (
    select * from {{ ref('brazil_states') }}
),

final as (
    select
        state,
        state_name,
        region,
        capital,
        latitude as capital_latitude,
        longitude as capital_longitude
    from states
)

select * from final
