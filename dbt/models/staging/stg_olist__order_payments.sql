with source as (
    select * from {{ source('olist', 'olist_order_payments') }}
),

renamed as (
    select
        order_id || '-' || payment_sequential as payment_key,
        order_id,
        cast(payment_sequential as integer) as payment_sequence,
        lower(trim(payment_type)) as payment_type,
        nullif(cast(payment_installments as integer), 0) as installments,
        cast(payment_value as decimal(12, 2)) as payment_value
    from source
),

final as (
    select * from renamed
)

select * from final
