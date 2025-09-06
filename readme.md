# ETL BanVic Pipeline - Complete Documentation

## 🏗️ Architecture Overview

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Source DB     │    │   Apache        │    │  Data Warehouse │
│  (PostgreSQL)   │───▶│   Airflow       │───▶│  (PostgreSQL)   │
│                 │    │                 │    │                 │
└─────────────────┘    │                 │    └─────────────────┘
┌─────────────────┐    │                 │
│   CSV Files     │───▶│                 │
│                 │    │                 │
└─────────────────┘    └─────────────────┘
```

**3 Database Architecture:**
- **source-db**: Original BanVic operational data (6 tables, 4,201 records)
- **data-warehouse**: ETL destination with staging schema (8 tables, 73,927 records)
- **airflow-db**: Airflow metadata and orchestration logs

## 🧠 Execution Logic

**ETL pipeline orchestrated by Airflow that extracts data from CSV and PostgreSQL in parallel, loads into Data Warehouse, and validates data quality.**

**Flow:** `Parallel Extractions → Synchronization → Parallel Loads → Validation`

## 📁 Project Structure

```
etl_challenge_v1/
├── dags/
│   └── banvic_etl_dag.py          # Main DAG - orchestration logic
├── plugins/
│   └── etl_utils.py               # ETL utilities - extraction/loading
├── config/
│   └── dw_init.sql                # Data Warehouse schema initialization
├── sources/
│   ├── banvic.sql                 # Source database data
│   └── transacoes.csv             # Transaction data (CSV)
├── data/YYYY-MM-DD/               # Runtime: extracted data by date
│   ├── csv/                       # CSV extractions
│   └── sql/                       # SQL table extractions
├── logs/                          # Runtime: Airflow execution logs
├── dbdata-*/                      # Runtime: Database volumes
├── docker-compose.yml             # Container orchestration
├── Dockerfile                     # Custom Airflow image
└── requirements.txt               # Python dependencies
```

## ⚡ Pipeline Tasks

| Task | Function | Input | Output |
|------|----------|-------|--------|
| **extract_csv_data** | Extract CSV transactions | `sources/transacoes.csv` | `/data/YYYY-MM-DD/csv/transacoes.csv` |
| **extract_sql_data** | Extract 6 PostgreSQL tables | Source DB tables | `/data/YYYY-MM-DD/sql/*.csv` |
| **sync_extractions** | Synchronize parallel extractions | - | Task coordination |
| **load_csv_data** | Load CSV to warehouse | Extracted CSV | `staging.transacoes` |
| **load_sql_data** | Load SQL tables to warehouse | Extracted SQL files | `staging.*` tables |
| **validate_data_quality** | Verify data loading | All staging tables | Success/Failure status |

## 🚀 Key Features

- **🔄 Parallelism**: Extractions and loads execute simultaneously
- **🔁 Idempotency**: Re-executions overwrite data (no duplicates)
- **📅 Time Organization**: Data organized by date `YYYY-MM-DD/source/`
- **🏥 Health Checks**: Containers wait for dependencies to be ready
- **✅ Data Validation**: Ensures all tables contain data after loading
- **🐳 Full Containerization**: Docker Compose orchestration
- **⏰ Automated Scheduling**: Daily execution at 04:35 AM

## ✅ Requirements Coverage

| Requirement | Implementation | Location |
|-------------|----------------|----------|
| **Airflow as orchestrator** | Complete Airflow setup with scheduler | `docker-compose.yml:54-79` |
| **Idempotent extractions** | File overwrite with `to_csv(..., index=False)` | `etl_utils.py:28` |
| **Extract all data** | 6 SQL tables + 1 CSV file extraction | `etl_utils.py:33-43` |
| **Date-based naming** | Directory structure `/data/YYYY-MM-DD/source/` | `etl_utils.py:12-14` |
| **Parallel execution** | Simultaneous task execution | `banvic_etl_dag.py:107` |
| **Conditional loading** | Sync point between extraction and loading | `banvic_etl_dag.py:107` |
| **Daily schedule 04:35** | Cron expression configuration | `banvic_etl_dag.py:26` |
| **Reproducible project** | Complete Docker setup + configurations | All config files included |

## 🔧 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Minimum 4GB RAM available
- Ports 54322 and 55432 available

### Execution Commands

```bash
# 1. Build and start containers
docker-compose up -d --build

# 2. Wait ~30s for initialization, then check status
docker-compose ps

# 3. Trigger ETL pipeline manually
docker-compose exec airflow-scheduler airflow dags trigger banvic_etl

# 4. Monitor execution
docker-compose logs -f airflow-scheduler
```

## 🔍 Data Verification

### Check Source Data (Original):
```bash
docker-compose exec source-db psql -U data_engineer -d banvic -c "SELECT COUNT(*) FROM clientes;"
```

### Check Data Warehouse (ETL Results):
```bash
docker-compose exec data-warehouse psql -U dw_user -d dw_banvic -c "SELECT COUNT(*) FROM staging.transacoes;"
```

### Check Pipeline Status:
```bash
docker-compose exec airflow-db psql -U airflow_user -d airflow_db -c "SELECT dag_id, state, execution_date FROM dag_run WHERE dag_id='banvic_etl' ORDER BY execution_date DESC LIMIT 3;"
```

## 🛑 Cleanup Commands

```bash
# Stop containers
docker-compose down

# Complete cleanup (including volumes)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## 📊 Data Summary

| Database | Tables | Records | Purpose |
|----------|--------|---------|---------|
| **source-db** | 6 tables | 4,201 | Original business data |
| **data-warehouse** | 8 tables | 73,927 | Processed ETL data |
| **airflow-db** | System tables | Metadata | Pipeline orchestration |

---
**Pipeline Status**: ✅ All requirements implemented and tested  
**Execution**: Fully automated with Docker Compose  
**Schedule**: Daily at 04:35 AM