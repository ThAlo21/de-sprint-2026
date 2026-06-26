
    
    



select dropoff_datetime
from "taxi_db"."dbt_dev"."stg_yellow_trips"
where dropoff_datetime is null


