
  
    

    create or replace table `db-project-456518`.`db_project_dataset`.`fact_departure_delays_by_airport`
      
    
    

    OPTIONS()
    as (
      

with delayed_departures as (
    select 
        dep_airport, 
        dep_delay,
        arr_delay
    from `db-project-456518`.`db_project_dataset`.`core_flights`
    where dep_delay is not null
)

select 
    dep_airport,
    AVG(dep_delay) as average_dep_delay,
    AVG(arr_delay) as average_arr_delay,
    count(*) AS delay_count
from delayed_departures
group by dep_airport
order by delay_count desc
    );
  