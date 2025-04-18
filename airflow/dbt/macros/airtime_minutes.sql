{% macro airtime_minutes(departure_time, arrival_time) %}
case
    when arrival_time >= departure_time then 
      TIMEDIFF(minute, departure_time, arrival_time)
    else 
      TIMEDIFF(minute, departure_time, arrival_time) + 1440  -- +24hrs if next day
  end as airtime_minutes,
{% endmacro %}