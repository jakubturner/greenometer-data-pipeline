from logging import getLogger
from typing import Any, Dict

import requests

from .config import AIRFLOW_API_URL, AIRFLOW_PASSWORD, AIRFLOW_USERNAME

LOGGER = getLogger(__name__)


def trigger_airflow_dag(
    timestamp: str,
    dag_id: str = "data_processing_dag_test",
    airflow_api_url: str = AIRFLOW_API_URL,
    airflow_username: str = AIRFLOW_USERNAME,
    airflow_password: str = AIRFLOW_PASSWORD,
) -> Dict[str, Any]:
    """
    Triggers Airflow DAG using Airflow REST API

    Args:
        timestamp: Timestamp for identifying the DAG run
        dag_id: ID of the DAG to trigger
        airflow_api_url: Airflow REST API URL
        airflow_username: Username for Airflow API
        airflow_password: Password for Airflow API

    Returns:
        Response from Airflow API or error information
    """
    url = f"{airflow_api_url}/dags/{dag_id}/dagRuns"
    payload = {"conf": {"timestamp": timestamp}, "dag_run_id": f"api_triggered_{timestamp}"}

    auth = requests.auth.HTTPBasicAuth(airflow_username, airflow_password)
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, auth=auth)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        LOGGER.error(f"Error triggering Airflow DAG: {e}")
        return {"status": "error", "message": str(e)}
