"""
Silver layer loader.

Reads Bronze Parquet files, applies cleaning, type conversion and LGPD rules,
then writes trusted datasets into the Silver layer.
"""

from pathlib import Path

import pandas as pd

from src.config.settings import BRONZE_DATA_PATH, SILVER_DATA_PATH
from src.observability.logger import get_logger
from src.processing.silver.cleaning import (
    remove_pii_columns,
    replace_invalid_values,
    standardize_column_names,
    replace_out_of_range_values,
)
from src.processing.silver.schema import (
    CATEGORICAL_COLUMNS,
    COLUMN_RENAME_MAPPING,
    EXPECTED_COLUMNS,
    FLOAT_COLUMNS,
    INTEGER_COLUMNS,
    PII_COLUMNS,
    REQUIRED_COLUMNS,
    SILVER_SCHEMA,
)
from src.processing.silver.typing import (
    convert_category_columns,
    convert_float_columns,
    convert_integer_columns,
)
from src.processing.silver.validator import validate_silver_dataframe

# =============================================================================
# Constants
# =============================================================================

PARQUET_EXTENSION = "*.parquet"

logger = get_logger(__name__)


# =============================================================================
# Functions
# =============================================================================


def list_bronze_parquet_files(
    bronze_data_path: Path = BRONZE_DATA_PATH,
) -> list[Path]:
    """List Bronze Parquet files."""
    if not bronze_data_path.exists():
        raise FileNotFoundError(
            f"Bronze data directory not found: {bronze_data_path}"
        )

    return sorted(bronze_data_path.glob(PARQUET_EXTENSION))


def transform_to_silver(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Apply Silver transformations to a Bronze dataframe."""
    dataframe = standardize_column_names(dataframe, COLUMN_RENAME_MAPPING)
    dataframe = replace_invalid_values(dataframe)
    dataframe = remove_pii_columns(dataframe, PII_COLUMNS)
    dataframe = convert_integer_columns(dataframe, INTEGER_COLUMNS)
    dataframe = convert_float_columns(dataframe, FLOAT_COLUMNS)
    dataframe = replace_out_of_range_values(dataframe, SILVER_SCHEMA)
    dataframe = convert_category_columns(dataframe, CATEGORICAL_COLUMNS)

    return dataframe


def load_parquet_to_silver(
    parquet_file_path: Path,
    silver_data_path: Path = SILVER_DATA_PATH,
) -> Path:
    """Load a Bronze Parquet file and save it as a Silver Parquet file."""
    logger.info("Reading Bronze file: %s", parquet_file_path)

    dataframe = pd.read_parquet(parquet_file_path)
    silver_dataframe = transform_to_silver(dataframe)

    validate_silver_dataframe(
        silver_dataframe,
        SILVER_SCHEMA,
        REQUIRED_COLUMNS,
        EXPECTED_COLUMNS,
    )

    silver_data_path.mkdir(parents=True, exist_ok=True)

    output_file_path = silver_data_path / parquet_file_path.name
    silver_dataframe.to_parquet(output_file_path, index=False)

    logger.info("Silver file created: %s", output_file_path)

    return output_file_path


def run_silver_layer() -> list[Path]:
    """Run the Silver layer pipeline."""
    logger.info("Starting Silver layer pipeline.")

    parquet_files = list_bronze_parquet_files()

    if not parquet_files:
        logger.warning("No Bronze Parquet files found in: %s", BRONZE_DATA_PATH)
        return []

    generated_files = [
        load_parquet_to_silver(parquet_file_path)
        for parquet_file_path in parquet_files
    ]

    logger.info("Silver layer completed successfully.")

    return generated_files


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    run_silver_layer()