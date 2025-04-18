import json
import os
from datetime import datetime, timedelta
import pandas as pd
from fpdf import FPDF

from airflow import DAG
from airflow.operators.python import PythonOperator

from logging import getLogger

LOGGER = getLogger(__name__)

DATA_DIR = os.environ.get("DATA_DIR", "/app/greenometer_data_pipeline/src/data")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/app/greenometer_data_pipeline/src/output")

# DAG Configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "data_processing_dag_test",
    default_args=default_args,
    description="Test data processing DAG",
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False,
)

def get_timestamp_from_context(context):
    dag_run = context.get("dag_run")
    conf = getattr(dag_run, "conf", {}) or {}
    timestamp = conf.get("timestamp", datetime.now().strftime("%Y%m%d%H%M%S"))
    LOGGER.info(f"[get_timestamp_from_context] Using timestamp: {timestamp}")
    return timestamp

def load_data(**context):
    LOGGER.info("Starting load_data function")
    timestamp = get_timestamp_from_context(context)
    input_file = os.path.join(DATA_DIR, f"input_{timestamp}.json")
    LOGGER.info(f"Looking for file: {input_file}")

    # For testing, create a sample file if it doesn't exist
    if not os.path.exists(input_file):
        LOGGER.info(f"File not found, creating sample data")
        sample_data = [
            {"dataPoint": "e-5-3", "value": 134},
            {"dataPoint": "e-5-1", "value": 233}
        ]
        os.makedirs(os.path.dirname(input_file), exist_ok=True)
        with open(input_file, "w") as f:
            json.dump(sample_data, f)

    with open(input_file, "r") as f:
        data = json.load(f)

    LOGGER.info(f"Loaded data: {data}")
    return data

def transform_data(**context):
    LOGGER.info("Starting transform_data function")
    data = context["ti"].xcom_pull(task_ids="load_data")

    transformed_data = []
    for item in data:
        parts = item["dataPoint"].split("-")
        entity, category, subcategory = parts

        value_type = "numeric" if isinstance(item["value"], (int, float)) else "text"

        transformed_data.append({
            "entity": entity,
            "category": category,
            "subcategory": subcategory,
            "value": item["value"],
            "value_type": value_type
        })

    LOGGER.info(f"Transformed data: {transformed_data}")
    return transformed_data

def save_excel(**context):
    LOGGER.info("Starting save_excel function")

    data = context["ti"].xcom_pull(task_ids="transform_data")
    timestamp = get_timestamp_from_context(context)

    excel_path = os.path.join(OUTPUT_DIR, f"output_{timestamp}.xlsx")
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)

    df = pd.DataFrame(data)
    df.to_excel(excel_path, index=False)

    LOGGER.info(f"Saved Excel to: {excel_path}")
    return excel_path

def save_pdf(**context):
    LOGGER.info("Starting save_pdf function")


    data = context["ti"].xcom_pull(task_ids="transform_data")
    timestamp = get_timestamp_from_context(context)

    pdf_path = os.path.join(OUTPUT_DIR, f"output_{timestamp}.pdf")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Data Processing Results", ln=True, align='C')

    for item in data:
        line = f"{item['entity']}-{item['category']}-{item['subcategory']}: {item['value']} ({item['value_type']})"
        pdf.cell(200, 10, txt=line, ln=True)

    pdf.output(pdf_path)
    LOGGER.info(f"Saved PDF to: {pdf_path}")
    return pdf_path

# Task definitions
load_task = PythonOperator(
    task_id="load_data",
    python_callable=load_data,
    provide_context=True,
    dag=dag,
)

transform_task = PythonOperator(
    task_id="transform_data",
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

excel_task = PythonOperator(
    task_id="save_excel",
    python_callable=save_excel,
    provide_context=True,
    dag=dag,
)

pdf_task = PythonOperator(
    task_id="save_pdf",
    python_callable=save_pdf,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
load_task >> transform_task >> [excel_task, pdf_task]