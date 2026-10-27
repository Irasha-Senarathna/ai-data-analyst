-- The source has orders handed to the carrier before purchase, or delivered
-- before shipping. fct_orders leaves delivery_days null for these; this test
-- keeps them visible in the data-quality report.
{{ config(severity='warn') }}

select order_id, purchased_at, delivered_to_carrier_at, delivered_to_customer_at
from {{ ref('stg_olist__orders') }}
where delivered_to_carrier_at < purchased_at
   or delivered_to_customer_at < delivered_to_carrier_at
