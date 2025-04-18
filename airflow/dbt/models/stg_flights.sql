{{
    config(
        materialized='view'
    )
}}

with raw_data as (
    select * from {{ source('raw_data', 'flights_data') }}
)
select
    {{ dbt_utils.generate_surrogate_key(['FlightDate', 'FlightNum', 'Origin']) }} as id,
    cast(FlightDate as date) as flight_date,
    cast(FlightMonth as date) as flight_month,
    cast(concat(cast(FlightDate as String), ' ', DepTimeFormatted, ':00') as datetime) as dep_time,
    cast(concat(cast(FlightDate as String), ' ', ArrTimeFormatted, ':00') as datetime) as arr_time,
    cast(FlightNum as integer) as flight_num,
    cast(ActualElapsedTime as integer) as actual_elapsed_time,
    cast(DepDelay as integer) as dep_delay,
    cast(ArrDelay as integer) as arr_delay,
    cast(Origin as String) as origin,
    cast(Dest as String) as destination,
    cast(CarrierCode as String) as carrier_code,
    cast(CarrierDescription as String) as carrier_desc,
    {{ flag_flight_delay_status('DepDelay', 'ArrDelay') }} as delay_status
from raw_data
where DepTimeFormatted is not null
    and ArrTimeFormatted is not null
    and cast(split(DepTimeFormatted, ':')[SAFE_OFFSET(0)] as integer) < 24
    and cast(split(DepTimeFormatted, ':')[SAFE_OFFSET(1)] as integer) < 60
    and cast(split(ArrTimeFormatted, ':')[SAFE_OFFSET(0)] as integer) < 24
    and cast(split(ArrTimeFormatted, ':')[SAFE_OFFSET(1)] as integer) < 60
