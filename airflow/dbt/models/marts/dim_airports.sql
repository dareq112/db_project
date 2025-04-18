{{
    config(
        materialized='table'
    )
}}

select
    iata as airport_code,
    airport as airport_name,
    city,
    state,
    country,
from {{ ref('airports') }}