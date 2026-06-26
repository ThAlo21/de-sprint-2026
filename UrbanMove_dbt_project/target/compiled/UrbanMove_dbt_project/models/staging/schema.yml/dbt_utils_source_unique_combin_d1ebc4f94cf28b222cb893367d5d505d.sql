





with validation_errors as (

    select
        vendor_id, pickup_datetime
    from "taxi_db"."public"."yellow_trips"
    group by vendor_id, pickup_datetime
    having count(*) > 1

)

select *
from validation_errors


