from typing import List, Union

from pydantic import BaseModel, Field, field_validator


class DataItem(BaseModel):
    """
    Model for representing a data point from client
    """

    dataPoint: str = Field(
        ..., description="Data point identifier in entity-category-subcategory format"
    )
    value: Union[int, float, str] = Field(
        ..., description="Value of the data point (number or text)"
    )

    @field_validator("dataPoint")
    @classmethod
    def validate_data_point_format(cls, v: str) -> str:
        """Validates dataPoint format (e-5-3)"""
        parts = v.split("-")
        if len(parts) != 3:
            raise ValueError("dataPoint must be in 'entity-category-subcategory' format")
        return v


class TransformedDataItem(BaseModel):
    """
    Model for transformed data point
    """

    entity: str
    category: str
    subcategory: str
    value: Union[int, float, str]
    value_type: str


class DataResponse(BaseModel):
    """
    Model for data reception response
    """

    status: str
    timestamp: str
    message: str


class FileListResponse(BaseModel):
    """
    Model for list of available generated files
    """

    excel_files: List[str]
    pdf_files: List[str]
