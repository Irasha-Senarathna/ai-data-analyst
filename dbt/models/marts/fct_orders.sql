-- One row per order. Order value comes from items (price + freight); the paid
-- amount comes from payments. They differ for some orders in the source, so
-- the two are kept as separate columns and never mixed.
with orders as (
    select * from {{ ref('int_orders_with_customer') }}
),

items as (
    select * from {{ ref('int_order_items_by_order') }}
),

payments as (
    select * from {{ ref('int_payments_by_order') }}
),

reviews as (
    select * from {{ ref('int_reviews_latest_per_order') }}
),

final as (
    select
        orders.order_id,
        orders.customer_unique_id,
        orders.customer_state,
        orders.region,
        orders.order_status,
        orders.is_canceled,
        orders.order_status = 'delivered' as is_delivered,
        orders.purchased_at,
        orders.purchase_date,
        orders.approved_at,
        orders.delivered_to_carrier_at,
        orders.delivered_to_customer_at,
        orders.estimated_delivery_date,
        coalesce(items.item_count, 0) as item_count,
        coalesce(items.distinct_sellers, 0) as seller_count,
        coalesce(items.items_value, 0) as items_value,
        coalesce(items.freight_value, 0) as freight_value,
        coalesce(items.items_value, 0) + coalesce(items.freight_value, 0) as order_value,
        payments.payment_value,
        payments.payment_count,
        payments.max_installments,
        payments.primary_payment_type,
        case
            when orders.order_status = 'delivered'
                and orders.delivered_to_customer_at
                    >= coalesce(orders.delivered_to_carrier_at, orders.purchased_at)
                and orders.delivered_to_customer_at >= orders.purchased_at
                then round(epoch(orders.delivered_to_customer_at - orders.purchased_at) / 86400, 1)
        end as delivery_days,
        case
            when orders.order_status = 'delivered' and orders.delivered_to_customer_at is not null
                then cast(orders.delivered_to_customer_at as date) > orders.estimated_delivery_date
        end as is_late,
        reviews.review_score
    from orders
    left join items
        on orders.order_id = items.order_id
    left join payments
        on orders.order_id = payments.order_id
    left join reviews
        on orders.order_id = reviews.order_id
)

select * from final
