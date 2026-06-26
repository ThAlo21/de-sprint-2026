select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select trip_count
from "taxi_db"."dbt_dev"."fct_revenue_by_zone"
where trip_count is null



      
    ) dbt_internal_test