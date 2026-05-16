import pandas as pd

df = pd.read_parquet("raw/yellow_tripdata_2026-01.parquet")
print(df)
# Check the range of every numeric column
print(df[["VendorID", "passenger_count", "payment_type", "PULocationID", "DOLocationID"]].describe())