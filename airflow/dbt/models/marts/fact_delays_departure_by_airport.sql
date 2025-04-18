with delayed_departures as (
    select 
        dep_airport, 
        delay_status
    from {{ ref(core_flights) }}
    where DepDelay is not null
)

select 
    dep_airport,
    delay_status, 
    count(*) AS delay_count
from delayed_departures
group by OriginAirport, delay_status
order by delay_count desc
