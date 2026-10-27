-- Some orders have several reviews. Keep the most recently answered one, so
-- review metrics count each order once.
with reviews as (
    select * from {{ ref('stg_olist__order_reviews') }}
),

final as (
    select
        review_id,
        order_id,
        review_score,
        comment_title is not null or comment_message is not null as has_comment,
        created_date,
        answered_at
    from reviews
    qualify row_number() over (
        partition by order_id
        order by answered_at desc nulls last, review_id
    ) = 1
)

select * from final
