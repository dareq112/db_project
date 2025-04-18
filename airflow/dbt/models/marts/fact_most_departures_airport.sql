{{
    config(
        materialized='table'
    )
}}

select
    a.name as airport_name,
    a.city,
    a.state,
    COUNT(*) as num_departures
from {{ ref('core_flights') }} f
join {{ ref('dim_airports') }} a on f.origin_airport_id = a.airport_id
group by airport_name, a.city, a.state
order by num_departures desc