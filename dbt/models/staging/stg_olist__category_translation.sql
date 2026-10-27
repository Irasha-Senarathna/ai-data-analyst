with source as (
    select * from {{ source('olist', 'olist_category_translation') }}
),

renamed as (
    select
        trim(product_category_name) as category_name,
        trim(product_category_name_english) as category_name_english
    from source
),

final as (
    select * from renamed
)

select * from final
