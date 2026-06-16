{{ config(materialized='table') }}

with daily_snapshots as (
    -- Reference the staging layer to build proper data lineage
    select 
        coin_id,
        date_trunc('day', date_time) as daily_date,
        price,
        market_cap,
        total_volume,
        ingestion_timestamp
    from {{ ref('stg_crypto_price') }}
    qualify row_number() over (
        partition by coin_id, date_trunc('day', date_time)
        order by date_time ASC, ingestion_timestamp DESC
    ) = 1
)

-- Calculate the 7-day moving average price for Bitcoin price trend analysis
select
    coin_id,
    daily_date as date_time, 
    price,
    market_cap,
    total_volume,
    avg(price) over (
        partition by coin_id
        order by daily_date
        rows between 6 preceding and current row
    ) as moving_avg_price_7d
from daily_snapshots