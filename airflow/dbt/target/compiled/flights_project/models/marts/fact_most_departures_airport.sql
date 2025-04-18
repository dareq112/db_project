

select
    a.airport_name,
    a.city,
    a.state,
    COUNT(*) as num_departures
from `db-project-456518`.`db_project_dataset`.`core_flights` f
join `db-project-456518`.`db_project_dataset`.`dim_airports` a on f.dep_airport = a.airport_name
group by airport_name, a.city, a.state
order by num_departures desc