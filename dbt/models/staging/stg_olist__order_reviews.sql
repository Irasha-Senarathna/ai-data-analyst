-- review_id alone is not unique in the source: the same review can cover
-- several orders. The key is (review_id, order_id).
with source as (
    select * from {{ source('olist', 'olist_order_reviews') }}
),

renamed as (
    select
        review_id || '-' || order_id as review_key,
        review_id,
        order_id,
        cast(review_score as integer) as review_score,
        nullif(trim(review_comment_title), '') as comment_title,
        nullif(trim(review_comment_message), '') as comment_message,
        cast(cast(review_creation_date as timestamp) as date) as created_date,
        try_cast(review_answer_timestamp as timestamp) as answered_at
    from source
),

final as (
    select * from renamed
)

select * from final
