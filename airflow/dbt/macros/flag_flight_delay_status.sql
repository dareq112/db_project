{% macro flag_flight_delay_status(DepDelay, ArrDelay) %}
    case
        when {{ DepDelay }} > 0 and {{ ArrDelay }} > 0 then 'ddad'
        when {{ DepDelay }} > 0 then 'dd'
        when {{ ArrDelay }} > 0 then 'ad'
        else 'nd'
    end
{% endmacro %}