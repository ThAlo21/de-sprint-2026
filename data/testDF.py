import os
import duckdb as db
import pyarrow.parquet as pq
from pyarrow import parquet
import pandas as pd


parquet_file = pq.ParquetFile("raw/yellow_tripdata_2026-01.parquet")
Parquet = "raw/yellow_tripdata_2026-01.parquet"


# 1. Run a standard SELECT query to preview the data rows
print("--- Data Preview ---")
preview = db.query(f"SELECT * FROM '{Parquet}'").df()
print(preview)


# 2. Check the actual data profile (Min, Max, Null counts) to verify your types
print("\n--- Column Value Summary : store_and_fwd_flag :  ---")
summary = db.query(f"""
    SELECT 
        extra,
        COUNT(extra) AS Code_Count, max(extra)
    FROM '{Parquet}'
    GROUP BY extra
""").df()
print(summary)


df = pd.read_parquet(Parquet)
print("*************** Here is Nullssss of each column ***************")
see_col = ["mta_tax", "extra"]
specific_null_counts = df[see_col].isnull().sum()
print(specific_null_counts)
print("*************** Here is datatypes of each column ***************")
specific_col_dtypes = df[see_col].dtypes
print(specific_col_dtypes)



# oversized = df[df['RatecodeID'].astype(str).str.len() > 1]
#
#
# if not oversized.empty:
#     print("Found values longer than 1 character:")
#     print(oversized['RatecodeID'].unique().tolist())
#     # Display with repr() to expose hidden spaces or newlines
#     print("Exact representaiotn:", [repr(x) for x in oversized['RatecodeID'].unique()])
# else:
#     print("All string lengths are exactly 1.")
#
#
#
# print("\n--- Data Check valid use of fillna with (X) ---")
# s = pd.Series([float('nan'), 'Y', 'N'])
# s2 = s.astype(str)
# print(s2)
# print(s2.isnull().sum())
# for col in range(len(schema)):
#     column = schema.column(col)
#     print(f"column: {column.name:.<25} Type: {column.physical_type}")




# Function to map PyArrow types to PostgreSQL data types
def map_to_postgres_type(col_schema):
    p_type = str(col_schema.physical_type).upper()
    l_type = str(col_schema.logical_type).upper() if col_schema.logical_type else ""

    # 1. Handle Timestamps (Common in TLC Yellow Taxi data)
    if "TIMESTAMP" in l_type:
        return "TIMESTAMP"

    # 2. Handle Integers
    if "INT32" in p_type:
        return "    "
    elif "INT64" in p_type:
        return "BIGINT"

    # 3. Handle Floats / Decimals
    elif "FLOAT" in p_type:
        return "REAL"
    elif "DOUBLE" in p_type:
        return "DOUBLE PRECISION"

    # 4. Handle Booleans
    elif "BOOLEAN" in p_type:
        return "BOOLEAN"

    # 5. Handle Strings and Text
    elif "BYTE_ARRAY" in p_type or "FIXED_LEN_BYTE_ARRAY" in p_type:
        return "TEXT"

    else:
        return "TEXT"


# Build the PostgreSQL DDL string
"""
ddl_columns = []
for col in range(len(schema)):
    column = schema.column(col)
    pg_type = map_to_postgres_type(column)

    # Wrap column names in double quotes to preserve case-sensitivity in PostgreSQL
    ddl_columns.append(f'    "{column.name}" {pg_type}')

table_name = "yellow_tripdata_2026_01"
ddl_content = f"CREATE TABLE IF NOT EXISTS {table_name} (\n" + ",\n".join(ddl_columns) + "\n);"

# Save the DDL to a .sql file in the same path as this Python script
script_dir = os.path.dirname(os.path.realpath(__file__)) if '__file__' in locals() else '.'
sql_file_path = os.path.join(script_dir, "postgres_schema.sql")

with open(sql_file_path, "w") as sql_file:
    sql_file.write(ddl_content)

print(f"\n[SUCCESS] PostgreSQL DDL successfully saved to: {sql_file_path}")"""