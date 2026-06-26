
  
    

  create  table "taxi_db"."dbt_dev"."fct_revenue_by_zone__dbt_tmp"
  
  
    as
  
  (
    






-- . Final transformation and output block
SELECT
    ROUND(SUM(fare_amount + tip_amount + tolls_amount + airport_fee)::numeric, 2) AS revenue,
    cast(pickup_datetime as date) AS pickup_date,
    extract(hour from pickup_datetime) AS pickup_hour,
    count(*) as trip_count,
    pickup_location_id as pickup_location_id
FROM "taxi_db"."dbt_dev"."stg_yellow_trips"
WHERE payment_type NOT IN (3, 4)
GROUP BY pickup_date, pickup_hour, pickup_location_id
ORDER BY revenue DESC
  );
  