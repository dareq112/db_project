

with delayed_departures as (
    select 
        dep_airport, 
        delay_status
    from `db-project-456518`.`db_project_dataset`.`core_flights`
    where dep_delay is not null
)

select 
    dep_airport,
    delay_status, 
    count(*) AS delay_count
from delayed_departures
group by dep_airport, delay_status
order by delay_count desc