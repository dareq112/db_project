
  
    

    create or replace table `db-project-456518`.`db_project_dataset`.`fact_departures.by_year`
      
    
    

    OPTIONS()
    as (
      

select
    extract(year from f.flight_date) as year,
    count(*) as num_departures
from `db-project-456518`.`db_project_dataset`.`core_flights` f
group by year
order by year
    );
  