



select
    1
from "taxi_db"."dbt_dev"."fct_revenue_by_zone"

where not(revenue >= 0)

