

  create or replace view `db-project-456518`.`db_project_dataset`.`stg_flights`
  OPTIONS()
  as 

with raw_data as (
    select * from `db-project-456518`.`db_project_dataset`.`flights_data`
)
select
    to_hex(md5(cast(coalesce(cast(FlightDate as string), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(FlightNum as string), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(Origin as string), '_dbt_utils_surrogate_key_null_') as string))) AS id,
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
    
    case
        when DepDelay > 0 and ArrDelay > 0 then 'ddad'
        when DepDelay > 0 then 'dd'
        when ArrDelay > 0 then 'ad'
        else 'nd'
    end
 as delay_status
from raw_data
where DepTimeFormatted is not null
    and ArrTimeFormatted is not null;

