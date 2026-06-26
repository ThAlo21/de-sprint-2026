select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select dropoff_location_id
from "taxi_db"."dbt_dev"."stg_yellow_trips"
where dropoff_location_id is null



      
    ) dbt_internal_test