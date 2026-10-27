-- fct_orders must keep every source order: no row lost to a join, none duplicated.
with marts as (
    select count(*) as orders from {{ ref('fct_orders') }}
),

staging as (
    select count(*) as orders from {{ ref('stg_olist__orders') }}
)

select marts.orders as marts_orders, staging.orders as staging_orders
from marts cross join staging
where marts.orders != staging.orders
