import json
import os
import time
import pandas as pd
from datetime import datetime
from confluent_kafka import Producer


# --- CONFIGURABLE SETTINGS ---
PARQUET_PATH = os.getenv("PARQUET_PATH", "../data/raw/yellow_tripdata_2026-01.parquet")
KAFKA_BOOTSTRAP_SERVER = "kafka-local:9092"
DELAY_SECONDS = float(os.getenv("PRODUCER_DELAY", "0.01"))
TOPIC_NAME = "taxi.trips.raw"
CHUNK_SIZE = 10000


def delivery_report(err, msg):
    """ Callback to confirm if the message safely hit the Kafka broker """
    # Muted success logging: Only output to terminal if a critical network error occurs
    if err is not None:
        print(f"Message delivery failed: {err}")


def json_serializer(obj):
    """ Custom serializer to handle Pandas/PyArrow timestamp objects """
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    return obj


# --- FIXED PRODUCER INITIALIZATION ---
producer_config = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER,
    'client.id': 'taxi-parquet-producer'
}
producer = Producer(producer_config)

print(f"Reading dataset via Pandas: {PARQUET_PATH}")
print(f"Streaming live feed to Kafka topic '{TOPIC_NAME}' with a {DELAY_SECONDS}s delay...")

try:
    # Read the file directly into a standard pandas dataframe
    df = pd.read_parquet(PARQUET_PATH)

    # Iterate through the DataFrame rows sequentially
    for index, row_data in df.iterrows():
        # Convert row pandas Series into a clean, native Python dictionary
        row = row_data.to_dict()

        # 1. Safely extract VendorID and Pickup Datetime values
        vendor_id = row.get("VendorID")
        pickup_dt = row.get("tpep_pickup_datetime")

        # Format datetime as a string if it exists and is clean
        pickup_str = None
        if isinstance(pickup_dt, (pd.Timestamp, datetime)):
            pickup_str = pickup_dt.strftime("%Y-%m-%d_%H:%M:%S")
        elif pickup_dt is not None and str(pickup_dt).strip() not in ["", "nan", "None"]:
            pickup_str = str(pickup_dt)

        # Convert VendorID to a string if it exists and is clean
        vendor_str = None
        if vendor_id is not None and str(vendor_id).strip() not in ["", "nan", "None"]:
            vendor_str = str(vendor_id)

        # 2. Compound Key Logic based on presence of variables
        if vendor_str is None and pickup_str is None:
            unique_key = f"fallback-key-{index}"
        elif vendor_str is not None and pickup_str is not None:
            unique_key = f"{vendor_str}-{pickup_str}"
        else:
            unique_key = vendor_str if vendor_str is not None else pickup_str

        # 3. Send row data serialized into a JSON string
        producer.produce(
            topic=TOPIC_NAME,
            key=str(unique_key),
            value=json.dumps(row, default=json_serializer),
            callback=delivery_report
        )

        # --- BATCHED RUNNING LOG ENGINE ---
        # Checks the execution row index loop every 1,000 messages
        if index > 0 and index % 1000 == 0:
            print(f"Messages sent: {index:,}")

        # Flush background delivery callbacks
        producer.poll(0)

        # Apply your streaming simulation delay
        time.sleep(DELAY_SECONDS)

except FileNotFoundError:
    print(f"\nError: Could not find the parquet file at '{PARQUET_PATH}'. Please verify your path setup.")
except KeyboardInterrupt:
    print("\nStreaming stopped manually by user.")
finally:
    print("Flushing final messages to broker...")
    producer.flush()
    print("Producer shutdown complete.")
