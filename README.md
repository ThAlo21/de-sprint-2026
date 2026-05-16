# de-sprint-2026

## Overview
Raw ingestion pipeline for NYC Yellow Taxi trip data (January 2026), 
built to unblock the UrbanMove Analytics team from manual CSV workflows.
Ticket: DE-2024-047

## Tech stack
- Python 3.13 — ingestion script
- PostgreSQL 15 — data warehouse
- Docker — containerised database
- pandas + pyarrow — data loading and cleaning

## How to run

### 1. Start the database
```bash
docker compose -f docker/docker-compose.yml --env-file .env up -d
```

### 2. Run the ingestion
```bash
source venv/bin/activate
python ingestion/ingest.py
```

### 3. Run the queries
```bash
docker exec -it urbanmove_db psql -U urbanmove -d taxi_db -f sql/queries.sql
```

## Data
- Source: NYC TLC Trip Record Data — Yellow Taxi, January 2026
- Raw rows: 3,724,889
- Rows after cleaning: 2,154,399
- Cleaning applied: deduplication, fare > 0, valid timestamps, null handling

## Known issues
- Unknown payment type category includes null records (sentinel value -1)
- Average trip distance for Unknown category is anomalous (11.6 miles)
- Treat Unknown category with caution in downstream analysis