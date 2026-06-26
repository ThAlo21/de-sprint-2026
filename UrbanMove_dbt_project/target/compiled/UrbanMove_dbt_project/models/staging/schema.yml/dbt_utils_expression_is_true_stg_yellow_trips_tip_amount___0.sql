



select
    1
from "taxi_db"."dbt_dev"."stg_yellow_trips"

where not(tip_amount >= 0)

