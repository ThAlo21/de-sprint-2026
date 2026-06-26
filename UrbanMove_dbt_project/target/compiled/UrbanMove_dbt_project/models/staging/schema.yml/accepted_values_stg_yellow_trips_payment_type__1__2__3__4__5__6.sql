
    
    

with all_values as (

    select
        payment_type as value_field,
        count(*) as n_records

    from "taxi_db"."dbt_dev"."stg_yellow_trips"
    group by payment_type

)

select *
from all_values
where value_field not in (
    '1','2','3','4','5','6'
)


