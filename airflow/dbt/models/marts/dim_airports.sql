{{
    config(
        materialized='table'
    )
}}

select
    airport_code,
    airport_name,
    city,
    state,
    country,
    iata,
    icao
from {{ ref('airports') }}