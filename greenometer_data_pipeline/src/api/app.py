import json
import os
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse

from ..common.airflow_client import trigger_airflow_dag
from ..common.config import DATA_DIR, OUTPUT_DIR, ensure_directories
from .models import DataItem, DataResponse, FileListResponse

app = FastAPI(
    title="Data Processing API",
    description="API for processing and transforming data",
    version="0.1.0",
)

# Ensure directories exist
ensure_directories()


@app.get("/")
def read_root() -> dict[str, str]:
    """Basic endpoint to check API functionality"""
    return {"message": "Data Processing API", "status": "running"}


@app.post("/data", response_model=DataResponse)
def receive_data(items: List[DataItem]) -> DataResponse:
    """
    Receives data in JSON format, saves it to a file
    and triggers Airflow DAG for processing

    In production deployment this would trigger an Airflow DAG.
    For testing and development purposes, we can process the data directly here.
    """
    # Save data to JSON file and get timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Ensure directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # Save input data to JSON file
    file_path = os.path.join(DATA_DIR, f"input_{timestamp}.json")
    with open(file_path, "w") as f:
        json.dump([item.model_dump() for item in items], f)

    # Trigger Airflow DAG
    dag_response = trigger_airflow_dag(timestamp)
    return DataResponse(
        status="success",
        timestamp=timestamp,
        message=f"Data received. Processing started with Airflow DAG. Response: {dag_response}",
    )

    # For development and testing purposes we can process data directly:
    # try:
    #     with open(file_path, "r") as f:
    #         data = json.load(f)
    #
    #     # Process and save data
    #     output_files = process_and_save_data(data, timestamp, OUTPUT_DIR)
    #
    #     return DataResponse(
    #         status="success",
    #         timestamp=timestamp,
    #         message=f"Data received and processed. Files created: {output_files}",
    #     )
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")


@app.get("/download/{file_type}")
def download_latest(file_type: str) -> FileResponse:
    """
    Endpoint to download the latest generated file (Excel or PDF)
    """
    if file_type not in ["excel", "pdf"]:
        raise HTTPException(status_code=400, detail="File type must be 'excel' or 'pdf'")

    extension = "xlsx" if file_type == "excel" else "pdf"

    # Ensure directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(f".{extension}")]
    if not files:
        raise HTTPException(status_code=404, detail=f"No files of type {file_type} found")

    latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)))
    file_path = os.path.join(OUTPUT_DIR, latest_file)

    return FileResponse(
        path=file_path,
        filename=latest_file,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if file_type == "excel"
            else "application/pdf"
        ),
    )


@app.get("/files", response_model=FileListResponse)
def list_files() -> FileListResponse:
    """
    Returns a list of all available generated files
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    excel_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".xlsx")]
    pdf_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".pdf")]

    return FileListResponse(excel_files=excel_files, pdf_files=pdf_files)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handling"""
    return JSONResponse(status_code=500, content={"message": f"Unexpected error: {str(exc)}"})
