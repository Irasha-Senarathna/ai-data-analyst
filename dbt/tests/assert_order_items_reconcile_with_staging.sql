-- Marts must not drop or duplicate order items: item revenue in fct_order_items
-- equals item revenue in staging. Returns a row (= failure) if they differ.
with marts as (
    select coalesce(sum(price), 0) as total from {{ ref('fct_order_items') }}
),

staging as (
    select coalesce(sum(price), 0) as total from {{ ref('stg_olist__order_items') }}
)

select marts.total as marts_total, staging.total as staging_total
from marts cross join staging
where marts.total != staging.total
