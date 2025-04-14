{{
    config(
        materialized='table'
    )
}}

with flights_data as (
    select *
    from {{ ref('core_flights') }}
)  

select 
    origin as airport_code,
    count(*) as num_departures
from flights_data
group by origin



