
  
    

    create or replace table `db-project-456518`.`db_project_dataset`.`fact_delays_by_flight_num`
      
    
    

    OPTIONS()
    as (
      

with flight_data as (
    select *
    from `db-project-456518`.`db_project_dataset`.`core_flights`
    where arr_delay > 0 or dep_delay > 0
)

select 
    flight_num,
    count(*) as total_flights_with_delays,
    sum(dep_delay) as total_dep_delay,
    sum(arr_delay) as total_arr_delay,
    avg(dep_delay) as avg_dep_delay,
    avg(arr_delay) as avg_arr_delay,
    min(dep_delay) as min_dep_delay,
    min(arr_delay) as min_arr_delay,
    max(dep_delay) as max_dep_delay,
    max(arr_delay) as max_arr_delay
from flight_data
group by flight_num
    );
  