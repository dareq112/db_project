
  
    

    create or replace table `db-project-456518`.`db_project_dataset`.`fact_departures_by_airport_year`
      
    
    

    OPTIONS()
    as (
      

with flights_data as (
    select *
    from `db-project-456518`.`db_project_dataset`.`core_flights`
)  

select 
    origin as airport_code,
    count(*) as num_departures
from flights_data
group by origin
    );
  