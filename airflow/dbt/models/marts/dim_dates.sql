{{
    config(
        materialized='table'
    )
}}

with flight_data as (
    select distinct flight_date
    from {{ ref('core_flights') }}
)

select 
    flight_date,
    extract(year from flight_date) as year,
    extract(quarter from flight_date) as quarter,
    extract(month from flight_date) as month,
    extract(day from flight_date) as day,
    extract(week from flight_date) as week,
    extract(dayofweek from flight_date) as day_of_week,
    case 
    when extract(dayofweek from flight_date) in (1, 7) then 'Weekend' 
    else 'Weekday' 
    end as day_type
from flight_data