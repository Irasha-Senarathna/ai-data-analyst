with source as (
    select * from {{ source('olist', 'olist_sellers') }}
),

renamed as (
    select
        seller_id,
        seller_zip_code_prefix as zip_code_prefix,
        lower(strip_accents(trim(seller_city))) as city,
        upper(trim(seller_state)) as state
    from source
),

final as (
    select * from renamed
)

select * from final
