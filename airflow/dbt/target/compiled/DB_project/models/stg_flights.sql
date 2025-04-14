with raw_data as (
    select * from `db-project-456518`.`db_project_dataset`.`flights_data`
)
select
    to_hex(md5(cast(coalesce(cast(FlightDate as string), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(FlightNum as string), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(Origin as string), '_dbt_utils_surrogate_key_null_') as string))) AS id,
    cast(FlightDate as date) as flight_date,
    extract(year from cast(FlightDate as date)) as flight_year,
    extract(month from cast(FlightDate as date)) as flight_month,
    extract(day from cast(FlightDate as date)) as flight_day,
    DepTimeFormatted as dep_time,
    ArrTimeFormatted as arr_time,
    FlightNum as flight_num,
    ActualElapsedTime as actual_elapsed_time,
    ArrDelay as arr_delay,
    DepDelay as dep_delay,
    Origin as origin,
    Dest as destination,
    CarrierCode as carrier_code,
    CarrierDescription as carrier_desc
from raw_data
where DepTimeFormatted is not null
    and ArrTimeFormatted is not null