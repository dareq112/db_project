
  
    

    create or replace table `db-project-456518`.`db_project_dataset`.`dim_carriers`
      
    
    

    OPTIONS()
    as (
      

select distinct 
    carrier_code,
    carrier_desc
from `db-project-456518`.`db_project_dataset`.`core_flights`
    );
  