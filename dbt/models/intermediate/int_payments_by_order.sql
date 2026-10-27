-- One row per order that has payments. The primary payment type is the one
-- that paid the largest share of the order (ties: the earliest payment).
with payments as (
    select * from {{ ref('stg_olist__order_payments') }}
),

final as (
    select
        order_id,
        count(*) as payment_count,
        sum(payment_value) as payment_value,
        max(installments) as max_installments,
        first(payment_type order by payment_value desc, payment_sequence) as primary_payment_type
    from payments
    group by order_id
)

select * from final
