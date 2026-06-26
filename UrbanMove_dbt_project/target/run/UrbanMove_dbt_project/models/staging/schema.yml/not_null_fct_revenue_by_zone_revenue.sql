select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select revenue
from "taxi_db"."dbt_dev"."fct_revenue_by_zone"
where revenue is null



      
    ) dbt_internal_test