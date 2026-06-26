select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select pickup_datetime
from "taxi_db"."dbt_dev"."stg_yellow_trips"
where pickup_datetime is null



      
    ) dbt_internal_test