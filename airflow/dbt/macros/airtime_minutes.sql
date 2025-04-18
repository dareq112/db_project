{% macro airtime_minutes(departure_time, arrival_time) %}
    case
        when {{ arrival_time }} >= {{ departure_time }} then 
            TIMESTAMP_DIFF({{ arrival_time }}, {{ departure_time }}, MINUTE)
        else 
            TIMESTAMP_DIFF({{ arrival_time }}, {{ departure_time }}, MINUTE) + 1440
    end
{% endmacro %}