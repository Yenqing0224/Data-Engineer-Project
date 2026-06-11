{{ config(materialized='table') }} -- Materialize as a table to persist data and optimize compute performance

with staging_data as (
    -- Reference the staging layer to build proper data lineage
    select * from {{ ref('stage_bitcoin') }}
),

daily_snapshots as (
    -- Filter to keep only daily midnight data, ignoring intraday high-frequency noise
    select * from staging_data
    where price_timestamp::time = '00:00:00'::time
),

deduplicated as (
    -- Assign row numbers to detect duplicates within the same day. Order by cleaned_at desc to ensure the latest record gets row_num = 1
    select
        price_timestamp,
        price_usd,
        row_number() over (
            partition by price_timestamp 
            order by cleaned_at desc
        ) as row_num
    from daily_snapshots
),

filtered_unique as (
    -- Filter out duplicate records, keeping only the most recent entry per day
    select
        price_timestamp,
        price_usd
    from deduplicated
    where row_num = 1
)

-- Calculate the 7-day moving average price for Bitcoin price trend analysis
select
    price_timestamp,
    price_usd,
    avg(price_usd) over (
        order by price_timestamp
        rows between 6 preceding and current row
    ) as moving_avg_price_7d
from filtered_unique