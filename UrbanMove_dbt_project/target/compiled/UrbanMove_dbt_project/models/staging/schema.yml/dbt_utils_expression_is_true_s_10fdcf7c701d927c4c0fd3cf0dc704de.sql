



select
    1
from "taxi_db"."dbt_dev"."stg_yellow_trips"

where not(cbd_congestion_fee >= 0)

