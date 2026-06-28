import json
import os
from datetime import datetime
from confluent_kafka import Consumer, KafkaError

KAFKA_BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER", "localhost:9092")
TOPIC_NAME = "taxi.trips.raw"
CONSUMER_GROUP = "taxi-validation-final-group"

# Offsets committed manually only after successful validation loops
consumer_config = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER,
    'group.id': CONSUMER_GROUP,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
}

consumer = Consumer(consumer_config)
consumer.subscribe([TOPIC_NAME])

print(f"Validation consumer live. Actively monitoring '{TOPIC_NAME}'...")
print("Safe mode: Offsets are committed manually only AFTER processing validation.\n")

valid_count = 0
invalid_count = 0

def validate_trip(data):
    """
    Validates a taxi event.
    Returns (is_valid, reason)
    """
    fare = data.get("fare_amount")
    if fare is None or fare < 0:
        return False, f"Invalid fare_amount: {fare}"

    pickup_str = data.get("tpep_pickup_datetime")
    dropoff_str = data.get("tpep_dropoff_datetime")

    if not pickup_str or not dropoff_str:
        return False, "Missing timestamps"

    try:
        fmt = "%Y-%m-%d %H:%M:%S"
        if datetime.strptime(dropoff_str, fmt) <= datetime.strptime(pickup_str, fmt):
            return False, f"Dropoff occurs before or at Pickup (Pickup: {pickup_str} | Dropoff: {dropoff_str})"
    except ValueError:
        return False, "Timestamp parsing failed (Expected YYYY-MM-DD HH:MM:SS)"

    return True, "Valid"

try:
    while True:
        # First poll automatically triggers partition allocation and group registration
        msg = consumer.poll(2.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Kafka Error: {msg.error()}")
                break

        raw_payload = msg.value().decode('utf-8')
        message_key = msg.key().decode('utf-8') if msg.key() else "No Key"

        try:
            trip_data = json.loads(raw_payload)
            is_valid, reason = validate_trip(trip_data)

            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                # Critical signal: Alert immediately if a record fails validation bounds
                print(f"[REJECTED] Key: {message_key} | Reason: {reason}")

        except json.JSONDecodeError:
            invalid_count += 1
            print(f"[MALFORMED JSON] Key: {message_key} | Could not decode string value.")

        # --- BATCHED RUNNING LOG ENGINE ---
        total = valid_count + invalid_count
        if total % 100 == 0:
            print(f"Processed: {total:,} | Valid: {valid_count:,} | Invalid: {invalid_count:,}")

        # The Safe Guardrail: Commit offset pointer position only after handling
        consumer.commit(asynchronous=False)

except KeyboardInterrupt:
    print("\nConsumer stopped manually.")
finally:
    print(f"\n--- Final Session Summary ---")
    print(f"Total Valid: {valid_count:,} | Total Invalid: {invalid_count:,}")
    consumer.close()
    print("Consumer connection securely closed.")
