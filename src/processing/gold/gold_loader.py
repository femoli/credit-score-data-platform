"""
Gold layer loader.

Reads Silver Parquet files, builds dimensional tables and writes them
to the Gold layer.
"""

from pathlib import Path

import pandas as pd

from src.config.settings import GOLD_DATA_PATH, SILVER_DATA_PATH
from src.observability.logger import get_logger
from src.processing.gold.dimensions import (
    build_credit_score_dimension,
    build_date_dimension,
    build_occupation_dimension,
)

# =============================================================================
# Constants
# =============================================================================

PARQUET_EXTENSION = "*.parquet"

logger = get_logger(__name__)


# =============================================================================
# Functions
# =============================================================================


def list_silver_parquet_files(
    silver_data_path: Path = SILVER_DATA_PATH,
) -> list[Path]:
    """
    List Silver Parquet files used by the Gold layer.

    Only the training dataset is loaded because the Gold layer contains
    business-ready analytical models that require the target variable
    (credit_score), which is not available in the Kaggle test dataset.
    """
    if not silver_data_path.exists():
        raise FileNotFoundError(
            f"Silver data directory not found: {silver_data_path}"
        )

    train_file = silver_data_path / "train.parquet"

    if not train_file.exists():
        raise FileNotFoundError(
            f"Train dataset not found: {train_file}"
        )

    return [train_file]


def build_gold_dimensions(
    dataframe: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Build all Gold dimensions."""
    return {
        "dim_occupation": build_occupation_dimension(dataframe),
        "dim_credit_score": build_credit_score_dimension(dataframe),
        "dim_date": build_date_dimension(dataframe),
    }


def load_parquet_to_gold(
    parquet_file_path: Path,
    gold_data_path: Path = GOLD_DATA_PATH,
) -> Path:
    """Load a Silver Parquet file and create Gold dimensions."""

    logger.info("Reading Silver file: %s", parquet_file_path)

    dataframe = pd.read_parquet(parquet_file_path)

    dimensions = build_gold_dimensions(dataframe)

    output_directory = gold_data_path / parquet_file_path.stem
    output_directory.mkdir(parents=True, exist_ok=True)

    for dimension_name, dimension_dataframe in dimensions.items():

        output_file = output_directory / f"{dimension_name}.parquet"

        dimension_dataframe.to_parquet(
            output_file,
            index=False,
        )

        logger.info(
            "%s created: %s",
            dimension_name,
            output_file,
        )

    return output_directory


def run_gold_layer() -> list[Path]:
    """Run the Gold layer pipeline."""

    logger.info("Starting Gold layer pipeline.")

    parquet_files = list_silver_parquet_files()

    if not parquet_files:
        logger.warning(
            "No Silver Parquet files found in: %s",
            SILVER_DATA_PATH,
        )
        return []

    generated_directories = [
        load_parquet_to_gold(parquet_file_path)
        for parquet_file_path in parquet_files
    ]

    logger.info("Gold layer completed successfully.")

    return generated_directories


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    run_gold_layer()