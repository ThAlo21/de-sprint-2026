





SELECT
            -- Generate a completely unique ID for every single row
            cast(vendor_id as varchar) || '-' || cast(pickup_datetime as varchar) as trip_id,
            vendor_id AS vendor_id,
            pickup_datetime AS pickup_datetime,
            dropoff_datetime AS dropoff_datetime,
            passenger_count AS passenger_count,
            trip_distance AS trip_distance,
            cast(ratecode_id as INTEGER) AS ratecode_id,
            case
                when is_stored_locally = 'Y' then true
                when is_stored_locally = 'N' then false
                else null
            end as is_stored_locally,
            fare_amount AS fare_amount,
            tip_amount AS tip_amount,
            total_amount AS total_amount,
            payment_type AS payment_type,
            pu_location_id AS pickup_location_id,
            do_location_id AS dropoff_location_id,
            tolls_amount AS tolls_amount,
            improvement_surcharge AS improvement_surcharge,
            congestion_surcharge AS congestion_surcharge,
            airport_fee AS airport_fee,
            cbd_congestion_fee AS cbd_congestion_fee,
            extra AS extra_surcharge,
            mta_tax AS regional_tax
FROM "taxi_db"."public"."yellow_trips"