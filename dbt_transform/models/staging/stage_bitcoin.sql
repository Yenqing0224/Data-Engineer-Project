{{ config(materialized='view') }} -- View

with raw_source as (
    select * from {{ source('coingecko_raw', 'bitcoin_raw') }}
)

select
    -- Convert Time
    to_timestamp_ntz(raw_data[0]::number / 1000) as price_timestamp,
    
    -- Extract Price
    raw_data[1]::float as price_usd,
    
    -- Time
    current_timestamp() as cleaned_at

from raw_source