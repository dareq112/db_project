

with flight_data as (
    select * from `db-project-456518`.`db_project_dataset`.`stg_flights`
),
airports_data as (
    select * from `db-project-456518`.`db_project_dataset`.`airports`
)

select 
    flight_data.id,
    flight_data.flight_date,
    flight_data.dep_time,
    flight_data.arr_time,
    flight_data.flight_num,
    flight_data.actual_elapsed_time,
    flight_data.dep_delay,
    flight_data.arr_delay,
    flight_data.origin,
    departure_airport.airport as dep_airport,
    departure_airport.city as dep_city,
    departure_airport.state as dep_state,
    departure_airport.country as dep_country,
    flight_data.destination,
    arrival_airport.airport as arr_airport,
    arrival_airport.city as arr_city,
    arrival_airport.state as arr_state,
    arrival_airport.country as arr_country,
    flight_data.carrier_code,
    flight_data.carrier_desc,
    flight_data.delay_status
from flight_data
inner join airports_data as departure_airport
on flight_data.origin = departure_airport.iata
inner join airports_data as arrival_airport
on flight_data.destination = arrival_airport.iata