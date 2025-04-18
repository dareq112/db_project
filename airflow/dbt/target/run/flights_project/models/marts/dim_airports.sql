
  
    

    create or replace table `db-project-456518`.`db_project_dataset`.`dim_airports`
      
    
    

    OPTIONS()
    as (
      

select
    iata as airport_code,
    airport as airport_name,
    city,
    state,
    country,
from `db-project-456518`.`db_project_dataset`.`airports`
    );
  