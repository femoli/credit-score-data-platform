"""
Silver layer type conversion functions.

Converts cleaned Bronze data into trusted Silver data types.
"""

import pandas as pd

from src.processing.silver.cleaning import clean_numeric_text

# =============================================================================
# Functions
# =============================================================================


def convert_integer_columns(
    dataframe: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    """Convert columns to nullable integer type."""
    for column in columns:
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(
                clean_numeric_text(dataframe[column]),
                errors="coerce",
            ).astype("Int64")

    return dataframe


def convert_float_columns(
    dataframe: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    """Convert columns to nullable float type."""
    for column in columns:
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(
                clean_numeric_text(dataframe[column]),
                errors="coerce",
            ).astype("Float64")

    return dataframe


def convert_category_columns(
    dataframe: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    """Convert columns to category type."""
    for column in columns:
        if column in dataframe.columns:
            dataframe[column] = dataframe[column].astype("category")

    return dataframe