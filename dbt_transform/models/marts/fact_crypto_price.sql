{{ config(materialized='table') }} -- Materialize as a table to persist data and optimize compute performance

with staging_data as (
    -- Reference the staging layer to build proper data lineage
    select * from {{ ref('stg_crypto_price') }}
),

daily_snapshots as (
    -- Filter to keep only daily midnight data, ignoring intraday high-frequency noise
    select * from staging_data
    where date_time::time = '00:00:00'::time
),

deduplicated as (
    -- Assign row numbers to detect duplicates within the same day. Order by cleaned_at desc to ensure the latest record gets row_num = 1
    select
        coin_id,
        date_time,
        price,
        market_cap,
        total_volume,
        cleaned_at,
        row_number() over (
            partition by coin_id, date_time 
            order by cleaned_at desc
        ) as row_num
    from daily_snapshots
),

filtered_unique as (
    -- Filter out duplicate records, keeping only the most recent entry per day
    select
        coin_id,
        date_time,
        price,
        market_cap,
        total_volume
    from deduplicated
    where row_num = 1
)

-- Calculate the 7-day moving average price for Bitcoin price trend analysis
select
    coin_id,
    date_time,
    price,
    market_cap,
    total_volume,
    avg(price) over (
        partition by coin_id
        order by date_time
        rows between 6 preceding and current row
    ) as moving_avg_price_7d
from filtered_unique