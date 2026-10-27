with source as (
    select * from {{ source('olist', 'olist_orders') }}
),

renamed as (
    select
        order_id,
        customer_id,
        lower(trim(order_status)) as order_status,
        cast(order_purchase_timestamp as timestamp) as purchased_at,
        try_cast(order_approved_at as timestamp) as approved_at,
        try_cast(order_delivered_carrier_date as timestamp) as delivered_to_carrier_at,
        try_cast(order_delivered_customer_date as timestamp) as delivered_to_customer_at,
        cast(cast(order_estimated_delivery_date as timestamp) as date) as estimated_delivery_date
    from source
),

final as (
    select * from renamed
)

select * from final
