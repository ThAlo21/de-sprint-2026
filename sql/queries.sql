""""






 CREATE TABLE yellow_trips (
            vendor_id INTEGER,
            pickup_datetime TIMESTAMP,
            dropoff_datetime TIMESTAMP,
            passenger_count INTEGER,
            trip_distance FLOAT,
            fare_amount FLOAT,
            tip_amount FLOAT,
            total_amount FLOAT,
            payment_type INTEGER,
            pu_location_id INTEGER,
            do_location_id BIGINT
        );


""""



---Top 10 pickup zones by total trips on weekday mornings (6am–10am)

 SELECT pu_location_id, count(*) as trip_count  FROM yellow_trips
 where EXTRACT(hour FROM pickup_datetime) >=6 AND EXTRACT(hour FROM pickup_datetime) < 10
  AND EXTRACT(dow FROM pickup_datetime) BETWEEN 1 AND 5
 GROUP BY pu_location_id ORDER BY trip_count DESC LIMIT 10;









---Average fare and tip amount by hour of day

 SELECT EXTRACT(hour FROM pickup_datetime) as pickup_hours, avg(fare_amount) as average_fare, avg(tip_amount) as average_tips ,count(*) as trip_count FROM yellow_trips
 GROUP BY pickup_hours ORDER BY pickup_hours ASC ;









---Payment type breakdown — does avg trip distance differ between them?
-- Note: 'Unknown' category includes null payment records (sentinel -1)
-- avg_trip_distance for Unknown is anomalous (11.6mi) — treat with caution


SELECT
CASE payment_type
    WHEN 1 THEN 'Credit card'
    WHEN 2 THEN 'Cash'
    WHEN 3 THEN 'No charge'
    WHEN 4 THEN 'Dispute'
    ELSE 'Unknown'
END AS payment_type_name,
count(*) as total_trips, avg(trip_distance) average_trip_distance from yellow_trips GROUP BY payment_type_name
ORDER BY total_trips DESC;






