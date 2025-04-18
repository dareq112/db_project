{{
    config(
        materialized='view'
    )
}}

with raw_data as (
    select * from {{ source('db_project_dataset', 'flights_data') }}
)
select
    {{ dbt_utils.generate_surrogate_key(['FlightDate', 'FlightNum', 'Origin']) }} as id,
    cast(FlightDate as date) as flight_date,
    cast(FlightMonth as date) as flight_month,
    cast(concat(cast(FlightDate as varchar), ' ', DepTimeFormatted) as timestamp) as dep_time,
    cast(concat(cast(FlightDate as varchar), ' ', ArrTimeFormatted) as timestamp) as arr_time,
    cast(FlightNum as integer) as flight_num,
    cast(ActualElapsedTime as integer) as actual_elapsed_time,
    cast(DepDelay as integer) as dep_delay,
    cast(ArrDelay as integer) as arr_delay,
    cast(Origin as varchar) ar origin,
    cast(Dest as varchar) as destination,
    cast(CarrierCode as varchar) as carrier_code,
    cast(CarrierDescription as varchar) as carrier_desc,
    {{ flag_flight_delay_status('DepDelay', 'ArrDelay') }} as delay_status
from raw_data
where DepTimeFormatted is not null
    and ArrTimeFormatted is not null
