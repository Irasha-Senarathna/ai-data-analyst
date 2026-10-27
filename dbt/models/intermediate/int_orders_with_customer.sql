-- One row per order with the buyer's identity and location at order time.
-- customer_id is per order in Olist, so its state is the state for that order.
with orders as (
    select * from {{ ref('stg_olist__orders') }}
),

customers as (
    select * from {{ ref('stg_olist__customers') }}
),

states as (
    select * from {{ ref('brazil_states') }}
),

final as (
    select
        orders.*,
        customers.customer_unique_id,
        customers.zip_code_prefix as customer_zip_code_prefix,
        customers.city as customer_city,
        customers.state as customer_state,
        states.region,
        cast(orders.purchased_at as date) as purchase_date,
        orders.order_status in ('canceled', 'unavailable') as is_canceled
    from orders
    left join customers
        on orders.customer_id = customers.customer_id
    left join states
        on customers.state = states.state
)

select * from final
