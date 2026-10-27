-- One row per person (customer_unique_id). Location is taken from the
-- person's latest order (ties broken by order_id), because a few people
-- bought from several states.
with orders as (
    select * from {{ ref('int_orders_with_customer') }}
),

geolocation as (
    select * from {{ ref('stg_olist__geolocation') }}
),

latest_order as (
    select
        customer_unique_id,
        customer_zip_code_prefix as zip_code_prefix,
        customer_city as city,
        customer_state as state,
        region
    from orders
    qualify row_number() over (
        partition by customer_unique_id
        order by purchased_at desc, order_id
    ) = 1
),

order_stats as (
    select
        customer_unique_id,
        min(purchased_at) as first_order_at,
        max(purchased_at) as last_order_at,
        count(*) as order_count
    from orders
    group by customer_unique_id
),

final as (
    select
        latest_order.customer_unique_id,
        latest_order.city,
        latest_order.state,
        latest_order.region,
        latest_order.zip_code_prefix,
        geolocation.latitude,
        geolocation.longitude,
        order_stats.first_order_at,
        order_stats.last_order_at,
        order_stats.order_count,
        order_stats.order_count > 1 as is_repeat_customer
    from latest_order
    inner join order_stats
        on latest_order.customer_unique_id = order_stats.customer_unique_id
    left join geolocation
        on latest_order.zip_code_prefix = geolocation.zip_code_prefix
)

select * from final
