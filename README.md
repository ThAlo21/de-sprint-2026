# # de-sprint-2026

## Overview
Automated analytics infrastructure for the UrbanMove data platform. This project bridges raw ingestion pipelines with a tested, production-grade data modeling layer to establish a single source of truth for corporate reporting.

* **Sprint 1 (Ticket DE-2024-047)**: Raw ingestion engine for NYC Yellow Taxi trip records.
* **Sprint 2 (Ticket DE-2024-061 - High Priority)**: Analytics engineering transformation layer built to resolve a critical $400K reporting variance between Finance ($4.2M) and Operations ($3.8M).
* **Sprint 3 (Ticket DE-2024-089)- Critical)**: Diagnose and fix a broken PySpark ingestion job that is crashing production and blocking the Q3 data freeze .
### The Business Context
The revenue discrepancy was traced back to decentralized analysts query-building from mismatched source tables, applying conflicting filters, and using disjointed definitions. This dbt layer enforces **one consistent calculation layout, one verified metric, and one unified truth** to protect future CFO financial audits.
The previous engineer left a PySpark script at ingestion/spark_ingest.py. It has multiple performance and correctness issues deliberately introduced. Your job is to find them, fix them, and explain each one.
---

## Tech Stack
- **Python 3.13** — Raw data ingestion engine
- **PostgreSQL 15** — Core data warehouse engine
- **Docker** — Containerized local infrastructure
- **pandas + pyarrow** — Automated data parsing and cleaning
- **dbt Core 1.8.0** — Data transformation, dependency lineage, and testing
- **java 17 + spark version 4.1.2  **- for running spark .

---

## Data Profile

### 1. Ingestion Metrics (Sprint 1)
- **Source**: NYC TLC Trip Record Data — Yellow Taxi (January 2026)
- **Raw Volume**: 3,724,889 rows
- **Post-Cleaning Volume**: 2,154,399 rows
- **Ingestion Filters**: Strict deduplication, positive fare bounds (`fare_amount > 0`), calendar boundary checks, and null row handling.

### 2. Core Business Entities (Sprint 2)
* **`stg_yellow_trips`**: Cleaned structural view mapping directly to raw infrastructure, handling atomic type casting and column renaming without altering business logic.
* **`fct_revenue_by_zone`**: Final materialized analytics table aggregating revenue records by **day**, **hour of day**, and **pickup zone**.

### 3. Code Issues & Optimization Summary
- **Critical Bug Fixes **: Removed .collect(), bumped memory to 1g, and set shuffle partitions to 8 to utilize hardware and eliminate Out-Of-Memory (OOM) crashes.
- **Why .collect() is an OOM Killer **: It pulls the entire distributed dataset into the driver's local memory, completely breaking Spark's parallel architecture.
- **Operation Order Matters **: Filtering and deduplicating rows first minimizes data volume early, preventing down-stream row mismatches and speeding up transformations.
- **Partitioning Strategy **: Partitioning data by day limits individual file sizes below the 1 GB best-practice threshold, resulting in roughly 31 optimized, business-ready files.
---

## How To Run

### 1. Start the Local Infrastructure
Spin up the containerized PostgreSQL data warehouse:
```bash
docker compose -f docker/docker-compose.yml --env-file .env up -d
```

### 2. Execute Data Ingestion (Legacy Python Engine)
Load, clean, and stream the raw trip files into the staging area:
```bash
source venv/bin/activate
python ingestion/ingest.py
```

### 3. Execute Optimized Spark Ingestion Engine (Sprint 3)
Run the corrected, high-performance PySpark cleaning and partitioning pipeline:

```bash
# 1. Verify Java 17 is active in your terminal session
java -version

# 2. Configure paths and set standard flags for macOS/Java 17 compatibility
export PARQUET_PATH="../data/raw/yellow_tripdata_2026-01.parquet"
export JAVA_TOOL_OPTIONS="--add-opens=java.base/sun.nio.ch=ALL-UNNAMED"

# 3. Execute the high-volume ingestion pipeline
python ingestion/spark_ingest.py
```
*(Note: If you run into broader module isolation errors on modern macOS environments, append the required internal memory flags to `SPARK_SUBMIT_OPTS` to safely open boundaries for NIO, IO, and internal utilities).*

### 4. Run and Test the dbt Transformation Pipeline
Download the required utility packages, compile the modular SQL logic, build production tables, and run all automated data contract tests:
```bash
# Fetch required macro extensions (dbt_utils)
dbt deps

# Build tables and instantly execute all data quality audits
dbt build
```
*(To refresh and verify only the financial summary table, run: `dbt build --select fct_revenue_by_zone`)*

---

## Discovered Data Issues & Engineering Decisions

### 1. Ingestion & Staging Anomalies
* **Unknown Payment Types**: Missing payment fields default to a sentinel value of `-1`. These rows exhibit an anomalous average trip distance of 11.6 miles and must be treated with caution downstream.
* **Storage Flags**: Empty or unpopulated items in the transmission data code (`store_and_fwd_flag`) are mapped onto the `is_stored_locally` property using a standard `'X'` sentinel string value.

### 2. Core Financial Transformation Decisions
* **The Revenue Formula**: Following core alignment with Ahmed Khalil (Finance Rep), gross revenue is strictly defined as:  
  `Revenue = fare_amount + tip_amount + tolls_amount + airport_fee`
* **Airport Fee Mapping**: Structural verification confirmed that `airport_fee` exists as a **single, dedicated column** inside our database warehouse and is added to the sum calculation directly.
* **Unrealized Revenue Filters**: To eliminate data noise causing discrepancies, we apply a hard exclusion filter on payment codes **`3` (No Charge)** and **`4` (Dispute)**. This isolates realized company earnings.
* **Congestion Surcharge Treatment (Engineering Judgment)**: Corporate consensus regarding regulatory congestion components (`congestion_surcharge` and `cbd_congestion_fee`) is pending business sign-off. **Decision**: These elements have been omitted from the current revenue calculation. Excluding pass-through regulatory fees prevents the artificial inflation of core operational earnings.
* **Time Fragmentation Fix**: To stop independent analysts from grouping metrics by random timeline intervals, timestamps are cast to a clean calendar date (`pickup_date`) and isolated hourly blocks (`pickup_hour` from `0` to `23`).

---

## Data Contract Testing and Quality Controls

To ensure our tables comply with strict CFO audit expectations, `dbt build` executes the following validation tests during the execution process before allowing queries into BI reporting:

* **Primary Key Integrity**: Strict `unique` and `not_null` guarantees enforced on trip identifiers.
* **Categorical Boundaries**: An `accepted_values` block restricts `payment_type` arrays to valid parameters.
* **The Zero-Floor Rule**: An automated mathematical test (`>= 0`) monitors the final `revenue` column. If a negative balance or computational glitch attempts to pass through, the build fails instantly, blocking corrupt figures from reaching corporate dashboards.
