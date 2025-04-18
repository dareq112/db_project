{{
    config(
        materialized='table'
    )
}}

select
    extract(year from f.flight_date) as year,
    count(*) as num_departures
from {{ ref('core_flights') }} f
group by year
order by year