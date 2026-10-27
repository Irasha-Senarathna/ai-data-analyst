# Data quality report

Warehouse: `warehouse.duckdb`

## Marts

| Table | Rows | Columns with nulls (% null) |
|---|---:|---|
| dim_customers | 96,096 | latitude (0.3%), longitude (0.3%) |
| dim_date | 791 | holiday_name (96.7%), holiday_type (96.7%) |
| dim_geography | 27 | — |
| dim_products | 32,951 | photos_count (1.9%), weight_g (0.0%), length_cm (0.0%), height_cm (0.0%), width_cm (0.0%), volume_cm3 (0.0%) |
| dim_sellers | 3,095 | latitude (0.2%), longitude (0.2%) |
| fct_daily_weather | 21,357 | — |
| fct_order_items | 112,650 | — |
| fct_orders | 99,441 | approved_at (0.2%), delivered_to_carrier_at (1.8%), delivered_to_customer_at (3.0%), delivery_days (3.0%), is_late (3.0%), review_score (0.8%) |
| fct_payments | 103,886 | — |
| fct_reviews | 98,673 | — |

## dbt tests

pass: 142, warn: 3

### Warnings

| Test | Rows |
|---|---:|
| `warn_source_delivery_timestamps_out_of_order` | 189 |
| `relationships_stg_olist__products_category_name__category_name__ref_stg_olist__category_translation_` | 13 |
| `relationships_stg_olist__customers_zip_code_prefix__zip_code_prefix__ref_stg_olist__geolocation_` | 279 |
