select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select pickup_location_id
from "taxi_db"."dbt_dev"."fct_revenue_by_zone"
where pickup_location_id is null



      
    ) dbt_internal_test