{{ config(materialized='view') }} -- View

with raw_source as (
    select * from {{ source('coingecko', 'coingecko_market_data') }}
),

flattened_prices as (
    select
        FILE_NAME,
        -- Cut out coin_id from S3 file path
        split_part(FILE_NAME, '/', 2) as coin_id,
        f.value[0]::number as raw_time_stamp,
        f.value[1]::float as price,
        INGESTION_TIMESTAMP as cleaned_at
    from raw_source,
    lateral flatten(input => RAW_DATA:prices) f
),

flattened_caps as (
    select
        FILE_NAME,
        split_part(FILE_NAME, '/', 2) as coin_id,
        f.value[0]::number as raw_time_stamp,
        f.value[1]::float as market_cap
    from raw_source,
    lateral flatten(input => RAW_DATA:market_caps) f
),

flattened_volumes as (
    select
        FILE_NAME,
        split_part(FILE_NAME, '/', 2) as coin_id,
        f.value[0]::number as raw_time_stamp,
        f.value[1]::float as total_volume
    from raw_source,
    lateral flatten(input => RAW_DATA:total_volumes) f
)

select
    p.coin_id,
    to_timestamp_ntz(p.raw_time_stamp / 1000) as date_time,
    p.price,
    c.market_cap,
    v.total_volume,
    p.cleaned_at
from flattened_prices p
join flattened_caps c 
    on p.coin_id = c.coin_id 
    and p.raw_time_stamp = c.raw_time_stamp 
    and p.FILE_NAME = c.FILE_NAME
join flattened_volumes v 
    on p.coin_id = v.coin_id 
    and p.raw_time_stamp = v.raw_time_stamp
    and p.FILE_NAME = v.FILE_NAME