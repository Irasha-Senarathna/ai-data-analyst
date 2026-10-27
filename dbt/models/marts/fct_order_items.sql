-- One row per order item. region is the buyer's region (used for row-level
-- security); seller_region is where the item shipped from.
with items as (
    select * from {{ ref('stg_olist__order_items') }}
),

orders as (
    select * from {{ ref('int_orders_with_customer') }}
),

products as (
    select * from {{ ref('dim_products') }}
),

sellers as (
    select * from {{ ref('dim_sellers') }}
),

final as (
    select
        items.order_item_key,
        items.order_id,
        items.order_item_number,
        items.product_id,
        products.category as product_category,
        items.seller_id,
        sellers.state as seller_state,
        sellers.region as seller_region,
        orders.customer_unique_id,
        orders.customer_state,
        orders.region,
        orders.order_status,
        orders.is_canceled,
        orders.purchased_at,
        orders.purchase_date,
        items.price,
        items.freight_value,
        items.price + items.freight_value as item_value
    from items
    inner join orders
        on items.order_id = orders.order_id
    left join products
        on items.product_id = products.product_id
    left join sellers
        on items.seller_id = sellers.seller_id
)

select * from final
