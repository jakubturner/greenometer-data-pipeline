import os
from typing import Any, Dict, List

import pandas as pd
from fpdf import FPDF


def transform_data_point(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms a single data point according to requirements

    Args:
        item: Input data point in {"dataPoint": "e-5-3", "value": 134} format

    Returns:
        Transformed data point with split dimensions and determined value type
    """
    # Split dataPoint into three dimensions
    parts = item["dataPoint"].split("-")
    entity, category, subcategory = parts

    # Determine value type
    value_type = "numeric" if isinstance(item["value"], (int, float)) else "text"

    # Create transformed data point
    return {
        "entity": entity,
        "category": category,
        "subcategory": subcategory,
        "value": item["value"],
        "value_type": value_type,
    }


def transform_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforms a list of data points

    Args:
        data: List of input data points

    Returns:
        List of transformed data points
    """
    return [transform_data_point(item) for item in data]


def save_as_excel(data: List[Dict[str, Any]], output_file: str) -> None:
    """
    Saves transformed data as Excel file

    Args:
        data: List of transformed data points
        output_file: Path to output Excel file
    """
    df = pd.DataFrame(data)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Create Excel file with formatting
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Transformed Data")
        worksheet = writer.sheets["Transformed Data"]

        # Basic formatting (set column widths)
        for idx, col in enumerate(df.columns):
            # Find maximum length of value in column
            max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
            # Excel uses letters for columns (A, B, C...)
            column_letter = chr(65 + idx)
            worksheet.column_dimensions[column_letter].width = max_length


def save_as_pdf(data: List[Dict[str, Any]], output_file: str) -> None:
    """
    Saves transformed data as PDF file

    Args:
        data: List of transformed data points
        output_file: Path to output PDF file
    """
    df = pd.DataFrame(data)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    pdf = FPDF()
    pdf.add_page()

    # Set font for header
    pdf.set_font("Arial", style="B", size=10)

    # Determine column width and row height
    col_width = pdf.w / len(df.columns) - 10
    row_height = 10

    # Add table header
    for col in df.columns:
        pdf.cell(col_width, row_height, col, border=1)
    pdf.ln()

    # Set font for data
    pdf.set_font("Arial", size=10)

    # Add data rows
    for i, row in df.iterrows():
        for col in df.columns:
            value = str(row[col])
            # Truncate too long values
            if len(value) > 25:
                value = value[:22] + "..."
            pdf.cell(col_width, row_height, value, border=1)
        pdf.ln()

    # Save PDF
    pdf.output(output_file)


def process_and_save_data(
    data: List[Dict[str, Any]], timestamp: str, output_dir: str
) -> Dict[str, str]:
    """
    Processes data and saves it as Excel and PDF

    Args:
        data: List of input data points
        timestamp: Timestamp for naming files
        output_dir: Directory for saving output files

    Returns:
        Dictionary with paths to generated files
    """
    # Transform data
    transformed_data = transform_data(data)

    # Paths to output files
    excel_path = os.path.join(output_dir, f"output_{timestamp}.xlsx")
    pdf_path = os.path.join(output_dir, f"output_{timestamp}.pdf")

    # Save as Excel
    save_as_excel(transformed_data, excel_path)

    # Save as PDF
    save_as_pdf(transformed_data, pdf_path)

    return {"excel": excel_path, "pdf": pdf_path}
