"""
Bronze layer loader.

Reads raw CSV files and stores them as Parquet files in the Bronze layer.

Architecture notes:
The Bronze layer does not apply business rules, type conversion, cleaning, or
data quality transformations. Its responsibility is to preserve raw data in an
optimized storage format.
"""

from pathlib import Path

import pandas as pd

from src.config.settings import BRONZE_DATA_PATH, RAW_DATA_PATH
from src.observability.logger import get_logger

# =============================================================================
# Constants
# =============================================================================

CSV_EXTENSION = "*.csv"

logger = get_logger(__name__)


# =============================================================================
# Functions
# =============================================================================

def list_raw_csv_files(raw_data_path: Path = RAW_DATA_PATH) -> list[Path]:
    """List all CSV files available in the raw data directory.

    Args:
        raw_data_path: Directory where raw CSV files are stored.

    Returns:
        A sorted list of CSV file paths.

    Raises:
        FileNotFoundError: If the raw data directory does not exist.
    """
    if not raw_data_path.exists():
        raise FileNotFoundError(f"Raw data directory not found: {raw_data_path}")

    return sorted(raw_data_path.glob(CSV_EXTENSION))


def load_csv_to_bronze(
    csv_file_path: Path,
    bronze_data_path: Path = BRONZE_DATA_PATH,
) -> Path:
    """Load a raw CSV file and save it as a Bronze Parquet file.

    Args:
        csv_file_path: Path to the raw CSV file.
        bronze_data_path: Directory where Bronze files are stored.

    Returns:
        Path to the generated Bronze Parquet file.
    """
    logger.info("Reading raw CSV file: %s", csv_file_path)

    dataframe = pd.read_csv(
        csv_file_path,
        dtype=str,
        low_memory=False,
    )

    bronze_data_path.mkdir(parents=True, exist_ok=True)

    output_file_path = bronze_data_path / f"{csv_file_path.stem}.parquet"

    dataframe.to_parquet(output_file_path, index=False)

    logger.info("Bronze file created: %s", output_file_path)

    return output_file_path


def run_bronze_layer() -> list[Path]:
    """Run the Bronze layer pipeline.

    Returns:
        A list of generated Bronze Parquet file paths.
    """
    logger.info("Starting Bronze layer pipeline.")

    csv_files = list_raw_csv_files()

    if not csv_files:
        logger.warning("No raw CSV files found in: %s", RAW_DATA_PATH)
        return []

    generated_files = [
        load_csv_to_bronze(csv_file_path)
        for csv_file_path in csv_files
    ]

    logger.info("Bronze layer completed successfully.")

    return generated_files


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    run_bronze_layer()