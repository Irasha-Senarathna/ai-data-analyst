-- The source has ~1M rows with many duplicates per zip prefix, some points
-- outside Brazil and some mislabelled in another state. This model keeps one row
-- per zip prefix: it drops points outside Brazil's bounding box (Fernando de
-- Noronha included), keeps only rows in the prefix's most common state, and takes
-- the median so stray points do not pull the coordinates. A few prefixes are
-- labelled with one state but every point lies in another; their coordinates
-- are set to null (unknown is safer than wrong) and flagged.
with source as (
    select * from {{ source('olist', 'olist_geolocation') }}
),

renamed as (
    select
        geolocation_zip_code_prefix as zip_code_prefix,
        cast(geolocation_lat as double) as latitude,
        cast(geolocation_lng as double) as longitude,
        lower(strip_accents(trim(geolocation_city))) as city,
        upper(trim(geolocation_state)) as state
    from source
),

inside_brazil as (
    select *
    from renamed
    where latitude between -34 and 6
      and longitude between -74 and -28
),

main_state as (
    select
        zip_code_prefix,
        mode(state) as state
    from inside_brazil
    group by zip_code_prefix
),

per_prefix as (
    select
        points.zip_code_prefix,
        median(points.latitude) as latitude,
        median(points.longitude) as longitude,
        mode(points.city) as city,
        main_state.state
    from inside_brazil as points
    inner join main_state
        on points.zip_code_prefix = main_state.zip_code_prefix
        and points.state = main_state.state
    group by points.zip_code_prefix, main_state.state
),

checked as (
    select
        per_prefix.*,
        abs(per_prefix.latitude - states.latitude)
        + abs(per_prefix.longitude - states.longitude) > 15 as is_location_suspect
    from per_prefix
    left join {{ ref('brazil_states') }} as states
        on per_prefix.state = states.state
),

final as (
    select
        zip_code_prefix,
        case when is_location_suspect then null else latitude end as latitude,
        case when is_location_suspect then null else longitude end as longitude,
        city,
        state,
        is_location_suspect
    from checked
)

select * from final
