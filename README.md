# Matrix Oracle DB + Insights API

This project sets up an Oracle XE database with synthetic "Matrix-verse" data, a Python data generator, and a FastAPI service exposing live insights.

## Architecture

- **Oracle XE**  
  Oracle XE 21c runs in a Docker container. Data is persisted in the `oracle-data/` volume.

- **Data Generator**  
  A Python script (`generate.py`) populates the database with coherent Matrix-style data:
  - `RESISTANCE_SHIPS` (25 rows)
  - `AWAKENED_HUMANS` (400 rows)
  - `SLEEPERS` (3,000 rows)
  - `AGENTS` (30 rows)
  - `MATRIX_LOCATIONS` (150 rows)
  - `ORACLES` (5 rows)
  - `MISSIONS` (6,400 rows)  
  Total: ~10,000 rows.

- **Insights API**  
  A FastAPI service exposing:
  - `/`: HTML dashboard (tables rendered via Jinja2)
  - `/insights`: JSON with results of four main queries
  - `/stats`: JSON with row counts for all tables

## Features


- Idempotent data generator with `RESET_DATA=1` option (clears tables before inserting)
- Insights include:
  1. Busiest ships (by mission count)
  2. Agent hotspots (locations with agent encounters)
  3. Training and belief metrics by ship
  4. Oracle guidance vs. mission success rate
  5.Notable humans (top jack-ins)
  6.Recent oracle-guided missions
  7.Top agents (by termination_count)
## Requirements

- Docker and Docker Compose
- At least 2 GB of free memory for the Oracle XE container

## Usage

### 1. Build and Start
Run the following to build and start all services:
```bash
docker compose up -d --build
```

### 2. Check Logs
Verify that services are running correctly:

- Oracle database initialization:
  ```bash
  docker logs -f matrix_oracle_xe
  ```

- Data generator table population:
  ```bash
  docker logs -f matrix_data_generator
  ```

- FastAPI service on port 8088:
  ```bash
  docker logs -f matrix_insights_api
  ```

 - confirm data loaded: 
 ```bash
docker exec -it matrix_oracle_xe sqlplus MATRIX_USER/Neo2025@oracle-xe:1521/xepdb1


SQL*Plus: Release 21.0.0.0.0 - Production on Mon Sep 29 19:16:13 2025
Version 21.3.0.0.0

Copyright (c) 1982, 2021, Oracle.  All rights reserved.

Last Successful login time: Mon Sep 29 2025 19:14:11 +00:00

Connected to:
Oracle Database 21c Express Edition Release 21.0.0.0.0 - Production
Version 21.3.0.0.0

SQL> SET PAGESIZE 100
SET LINESIZE 200SQL>
SQL> COLUMN table_name FORMAT A25
COLUMN row_count FORMAT 999999SQL>
SQL> SELECT 'RESISTANCE_SHIPS' AS table_name, COUNT(*) AS row_count FROM RESISTANCE_SHIPS
  2  UNION ALL
  3  SELECT 'AWAKENED_HUMANS', COUNT(*) FROM AWAKENED_HUMANS
  4  UNION ALL
  5  SELECT 'SLEEPERS', COUNT(*) FROM SLEEPERS
  6  UNION ALL
SELECT 'AGENTS', COUNT(*) FROM AGENTS
  7    8  UNION ALL
SELECT 'MATRIX_LOCATIONS', COUNT(*) FROM MATRIX_LOCATIONS
  9   10  UNION ALL
 11  SELECT 'ORACLES', COUNT(*) FROM ORACLES
 12  UNION ALL
 13  SELECT 'MISSIONS', COUNT(*) FROM MISSIONS;

TABLE_NAME                ROW_COUNT
------------------------- ---------
RESISTANCE_SHIPS                 25
AWAKENED_HUMANS                 400
SLEEPERS                       3000
AGENTS                           30
MATRIX_LOCATIONS                150
ORACLES                           5
MISSIONS                       6400

7 rows selected.
```


### 3. Access Services
- Web UI: [http://localhost:8088/](http://localhost:8088/)
- JSON insights: [http://localhost:8088/insights](http://localhost:8088/insights)
- Stats: [http://localhost:8088/stats](http://localhost:8088/stats)

### 4. Development (Hot Reload)
Code and templates are mounted into the container. Changes saved locally will trigger FastAPI auto-reload. For network shares (e.g., NFS/SMB), hot reload uses polling:
```bash
WATCHFILES_FORCE_POLLING=true
```

### 5. Reset Data (Optional)
To wipe and re-seed all tables, update the `docker-compose.yml`:
```yaml
services:
  data-generator:
    environment:
      - RESET_DATA=1
```
Then rebuild and restart the data-generator service:
```bash
docker compose up -d --build data-generator
```

### 6. Manual Database Validation
To verify the database contents, exec into the Oracle container:
```bash
docker exec -it matrix_oracle_xe sqlplus MATRIX_USER/Neo2025@oracle-xe:1521/xepdb1
```
Run the validation script included in the repository:
```sql
@/tmp/check_matrix.sql
```

The script (`check_matrix.sql`) validates the data in the tables and is located in the repository's root directory.

## Troubleshooting

- **Empty dashboard tables but `/insights` JSON has data**: Ensure `run_query()` lowercases column names and the Jinja template uses matching key casing.

## Next Steps

- Add charting to the dashboard (e.g., Chart.js or Recharts)
- Include more relationships and sample queries
- Extend the data generator to simulate time series or mission outcomes
- Secure the API with authentication middleware