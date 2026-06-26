
    
    



select dropoff_location_id
from "taxi_db"."dbt_dev"."stg_yellow_trips"
where dropoff_location_id is null


