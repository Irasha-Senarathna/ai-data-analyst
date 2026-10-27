with payments as (
    select * from {{ ref('stg_olist__order_payments') }}
),

orders as (
    select * from {{ ref('int_orders_with_customer') }}
),

final as (
    select
        payments.payment_key,
        payments.order_id,
        payments.payment_sequence,
        payments.payment_type,
        payments.installments,
        payments.payment_value,
        orders.customer_unique_id,
        orders.customer_state,
        orders.region,
        orders.order_status,
        orders.purchase_date
    from payments
    inner join orders
        on payments.order_id = orders.order_id
)

select * from final
