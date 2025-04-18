{{
    config(
        materialized='table'
    )
}}

select
    a.airport_name,
    a.city,
    a.state,
    COUNT(*) as num_departures
from {{ ref('core_flights') }} f
join {{ ref('dim_airports') }} a on f.dep_airport = a.airport_name
group by airport_name, a.city, a.state
order by num_departures desc