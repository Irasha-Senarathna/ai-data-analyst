with sellers as (
    select * from {{ ref('stg_olist__sellers') }}
),

states as (
    select * from {{ ref('brazil_states') }}
),

geolocation as (
    select * from {{ ref('stg_olist__geolocation') }}
),

sales as (
    select
        items.seller_id,
        min(orders.purchased_at) as first_sale_at,
        max(orders.purchased_at) as last_sale_at,
        count(*) as items_sold
    from {{ ref('stg_olist__order_items') }} as items
    inner join {{ ref('stg_olist__orders') }} as orders
        on items.order_id = orders.order_id
    group by items.seller_id
),

final as (
    select
        sellers.seller_id,
        sellers.city,
        sellers.state,
        states.region,
        sellers.zip_code_prefix,
        geolocation.latitude,
        geolocation.longitude,
        sales.first_sale_at,
        sales.last_sale_at,
        coalesce(sales.items_sold, 0) as items_sold
    from sellers
    left join states
        on sellers.state = states.state
    left join geolocation
        on sellers.zip_code_prefix = geolocation.zip_code_prefix
    left join sales
        on sellers.seller_id = sales.seller_id
)

select * from final
