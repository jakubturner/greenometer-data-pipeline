import os
from typing import Any, Dict

# General path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_DIR = os.environ.get(
    "DATA_DIR", os.path.join(BASE_DIR, "greenometer_data_pipeline", "src", "data")
)
OUTPUT_DIR = os.environ.get(
    "OUTPUT_DIR", os.path.join(BASE_DIR, "greenometer_data_pipeline", "src", "output")
)

# Airflow configuration
AIRFLOW_API_URL = os.environ.get("AIRFLOW_API_URL", "http://localhost:8080/api/v1")
AIRFLOW_USERNAME = os.environ.get("AIRFLOW_USERNAME", "admin")
AIRFLOW_PASSWORD = os.environ.get("AIRFLOW_PASSWORD", "admin")

# Output formats
OUTPUT_FORMATS = ["xlsx", "pdf"]

# API configuration
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", 8000))


def get_config() -> Dict[str, Any]:
    """
    Returns current configuration as a dictionary
    """
    return {
        "data_dir": DATA_DIR,
        "output_dir": OUTPUT_DIR,
        "airflow_api_url": AIRFLOW_API_URL,
        "airflow_username": AIRFLOW_USERNAME,
        "api_host": API_HOST,
        "api_port": API_PORT,
    }


def ensure_directories() -> None:
    """
    Ensures required directories exist
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
