-- One row per reviewed order (its latest review). Free-text comments are not
-- exposed here: they are untrusted input and are not needed for metrics.
with reviews as (
    select * from {{ ref('int_reviews_latest_per_order') }}
),

orders as (
    select * from {{ ref('int_orders_with_customer') }}
),

final as (
    select
        reviews.order_id,
        reviews.review_id,
        reviews.review_score,
        reviews.has_comment,
        reviews.created_date,
        reviews.answered_at,
        orders.customer_unique_id,
        orders.customer_state,
        orders.region,
        orders.order_status,
        orders.purchase_date
    from reviews
    inner join orders
        on reviews.order_id = orders.order_id
)

select * from final
