# Greenometer Data Pipeline

A simple data pipeline that receives data via API, transforms it, and stores it in Excel and PDF formats.

## Project Description

This project implements a data pipeline that:
1. Provides an API endpoint to receive data in JSON format
2. Transforms the data into a structured format
3. Stores the transformed data as Excel (.xlsx) and PDF files
4. Uses Apache Airflow for data processing orchestration

## Project Structure

```
greenometer-data-pipeline/
│
├── greenometer_data_pipeline/
│   ├── api/                    # FastAPI app (entrypoint, routes, models)
│   │   ├── app.py
│   │   ├── main.py
│   │   └── models.py
│   │
│   ├── airflow/                # Airflow DAG definitions
│   │   └── dags/
│   │       └── data_processing_dag.py
│   │
│   ├── common/                 # Shared logic
│   │   ├── __init__.py
│   │   ├── airflow_client.py   # DAG trigger helper
│   │   ├── config.py
│   │   └── data_transformer.py
│   │
│   ├── data/                   # Directory for incoming JSON files
│   └── output/                 # Directory for generated Excel and PDF files
│
├── tests/                     # Unit and integration tests
│
├── docker-compose.yml        # Compose file for local development
├── Dockerfile.api            # Dockerfile for FastAPI service
├── Dockerfile.airflow        # Dockerfile for Airflow service
├── pyproject.toml            # Poetry configuration
└── README.md
```

## Technologies

- Python 3.12
- FastAPI - REST API framework
- Apache Airflow - workflow orchestration
- Pandas - data processing
- openpyxl - Excel file generation
- FPDF - PDF file generation
- Poetry - dependency management

## Installation and Running

### Local Development with Poetry

```bash
# Install dependencies
poetry install

# Run API server
poetry run greeno_api
```

### Running with Docker Compose

```bash
# Build and run containers
docker-compose up --build

# Just run (after previous build)
docker-compose up
```

After starting, the following services will be available:
* API: http://localhost:8000
* Airflow web interface: http://localhost:8080 (login credentials: admin/admin)

## API Documentation

### Endpoints

#### POST /data
Accepts data in JSON format:

```json
[
  { "dataPoint": "e-5-3", "value": 134 },
  { "dataPoint": "e-5-1", "value": 233 },
  { "dataPoint": "e-2-3", "value": "text string" }
]
```

#### GET /download/{file_type}
Downloads the latest generated file of the specified type (excel or pdf).

#### GET /files
Gets a list of all generated files.

### Swagger Documentation
After starting the API, Swagger documentation is available at: http://localhost:8000/docs

## Data Processing Workflow

1. Data is received via the API endpoint and stored as a JSON file
2. Airflow DAG is triggered with a timestamp parameter
3. Data is loaded and transformed:
  * `dataPoint` is split into entity, category, and subcategory
  * A `value_type` field is added with a value of "numeric" or "text"
4. Transformed data is saved as Excel and PDF files

## Project Extensions

For production deployment, it would be worth considering:
* Adding authentication for the API
* Replacing the SQLite database (in Airflow) with PostgreSQL or MySQL
* Implementing a retry mechanism for data processing
* Expanding monitoring and logging
* Adding tests for individual components