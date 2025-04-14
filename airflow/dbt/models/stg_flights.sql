{{
    config(
        materialized='view'
    )
}}

with raw_data as (
    select * from {{ source('db_project_dataset', 'flights_data') }}
)
select
    {{ dbt_utils.generate_surrogate_key(['FlightDate', 'FlightNum', 'Origin']) }} AS id,
    cast(FlightDate as date) as flight_date,
    CONCAT(CAST(FlightDate AS STRING), ' ', DepTimeFormatted) AS dep_time,
    CONCAT(CAST(FlightDate AS STRING), ' ', ArrTimeFormatted) AS arr_time,
    FlightNum as flight_num,
    cast(ActualElapsedTime as integer) as actual_elapsed_time,
    cast(DepDelay as integer) as dep_delay,
    cast(ArrDelay as integer) as arr_delay,
    Origin as origin,
    Dest as destination,
    CarrierCode as carrier_code,
    CarrierDescription as carrier_desc,
    {{ flag_flight_delay_status('DepDelay', 'ArrDelay') }} as delay_status
from raw_data
where DepTimeFormatted is not null
    and ArrTimeFormatted is not null
