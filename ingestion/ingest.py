import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import psycopg2.extras

load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

PARQUET_PATH = "data/raw/yellow_tripdata_2026-01.parquet"

def load_data(path: str) -> pd.DataFrame:
    print(f"Loading data from {path}...")
    df = pd.read_parquet(path)
    print(f"Loaded {len(df):,} rows and {len(df.columns)} columns")
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    print("Cleaning data...")
    df = df.drop_duplicates(
        subset=["VendorID", "tpep_pickup_datetime"]
    )
    df = df[df["fare_amount"] > 0]
    df = df[df["tpep_pickup_datetime"] < df["tpep_dropoff_datetime"]]
    df["payment_type"] = df["payment_type"].astype("int32")
    df["passenger_count"] = df["passenger_count"].fillna(-1)
    print(f"Rows after cleaning: {len(df):,}")
    return df

def ingest_to_postgres(df: pd.DataFrame):
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("Inserting rows — this will take just a few seconds...")
    cursor.execute("""
        DROP TABLE IF EXISTS yellow_trips;
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
            do_location_id INTEGER
        );
    """)
    # 1. Define the specific columns to extract in the correct order
    columns = [
        "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime",
        "passenger_count", "trip_distance", "fare_amount", "tip_amount",
        "total_amount", "payment_type", "PULocationID", "DOLocationID"
    ]

    # 2. Convert DataFrame rows into a list of tuples efficiently
    data_tuples = [tuple(x) for x in df[columns].to_numpy()]

    # 3. Perform bulk insertion
    query = "INSERT INTO yellow_trips VALUES %s"
    psycopg2.extras.execute_values(cursor, query, data_tuples)

    conn.commit()
    cursor.close()
    conn.close()
    print("Done. Data loaded into yellow_trips table.")

if __name__ == "__main__":
    df = load_data(PARQUET_PATH)
    df = clean_data(df)
    ingest_to_postgres(df)

