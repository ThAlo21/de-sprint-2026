select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      



select
    1
from "taxi_db"."dbt_dev"."stg_yellow_trips"

where not(trip_distance >= 0)


      
    ) dbt_internal_test