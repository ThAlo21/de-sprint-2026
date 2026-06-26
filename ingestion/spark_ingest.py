from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
import os

PARQUET_PATH = os.getenv("PARQUET_PATH", "../data/raw/yellow_tripdata_2026-01.parquet")
OUTPUT_PATH = "output/yellow_trips_clean"

spark = SparkSession.builder.appName("UrbanMove_Ingestion").config("spark.driver.memory", "1g").config("spark.sql.shuffle.partitions", "6").config("spark.sql.sources.partitionOverwriteMode", "dynamic").getOrCreate()

print("Loading data...")
df = spark.read.parquet(PARQUET_PATH)

print("Cleaning data...")

# 1. Subset Deduplication (Replaced global deduplication)
df_deduped = df.dropDuplicates(["VendorID", "tpep_pickup_datetime"])

# 2. Row Filters
df_clean = df_deduped \
    .filter(F.col("fare_amount") > 0) \
    .filter(F.col("tpep_pickup_datetime") < F.col("tpep_dropoff_datetime"))

# 3. Data Type Casts & Null Handling
df_transformed = df_clean.withColumn("payment_type", F.col("payment_type").cast(IntegerType())).fillna(-1, subset=["passenger_count"])

# 4. Handle 'store_and_fwd_flag' (Replaces pandas string replaces and fillna)
df_transformed = df_transformed.withColumn(
    "store_and_fwd_flag",
    F.when(F.col("store_and_fwd_flag").isNull(), "X")
     .when(F.col("store_and_fwd_flag").cast("string").isin("nan", "None", ""), "X")
     .otherwise(F.col("store_and_fwd_flag").cast("string"))
)

# 5. Row Count Logging
total_rows = df_transformed.count()
print(f"Rows after cleaning: {total_rows:,}")

# 6. Extract Date and Repartition (Ensuring 1 file per day folder layout)
df_with_day = df_transformed.withColumn("extracted_day", F.to_date("tpep_pickup_datetime"))
df_pushed = df_with_day.repartition("extracted_day")

# 7. Write to Output
print("Writing data to storage...")
df_pushed.write.mode("overwrite").partitionBy("extracted_day").parquet(OUTPUT_PATH)

spark.stop()
print("Pipeline complete!")
