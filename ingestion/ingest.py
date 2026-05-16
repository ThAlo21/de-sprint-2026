import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from pyarrow.compute import fill_null

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

    print("Inserting rows — this will take a few minutes...")
    for _, row in df.iterrows():
        cursor.execute("""            INSERT INTO yellow_trips VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            row.get("VendorID"),
            row.get("tpep_pickup_datetime"),
            row.get("tpep_dropoff_datetime"),
            row.get("passenger_count"),
            row.get("trip_distance"),
            row.get("fare_amount"),
            row.get("tip_amount"),
            row.get("total_amount"),
            row.get("payment_type"),
            row.get("PULocationID"),
            row.get("DOLocationID"),
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("Done. Data loaded into yellow_trips table.")

if __name__ == "__main__":
    df = load_data(PARQUET_PATH)
    df = clean_data(df)
    ingest_to_postgres(df)

