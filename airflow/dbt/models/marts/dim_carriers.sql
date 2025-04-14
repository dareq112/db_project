{{
    config(
        materialized='table'
    )
}}

select distinct 
    carrier_code,
    carrier_desc
from {{ ref('core_flights') }}