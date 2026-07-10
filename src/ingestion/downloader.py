"""
Dataset downloader.

This module orchestrates the ingestion process by downloading the dataset
from Kaggle and generating metadata for the Raw layer.

It represents the Extract stage of the ETL pipeline.
"""

from src.config.settings import DATASET_REF, RAW_DATA_PATH
from src.ingestion.kaggle_auth import KaggleAuthenticationError
from src.ingestion.kaggle_client import download_dataset
from src.ingestion.metadata import generate_metadata


def main() -> None:
    """Execute the dataset ingestion pipeline."""
    try:
        # Ensure the Raw landing zone exists
        RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)

        # Download the dataset into the Raw layer
        download_dataset(output_dir=str(RAW_DATA_PATH))

        # Generate ingestion metadata
        generate_metadata(
            output_dir=str(RAW_DATA_PATH),
            dataset_ref=DATASET_REF,
        )

    except KaggleAuthenticationError as error:
        print(f"❌ Kaggle authentication failed.\n\n{error}")
        raise SystemExit(1) from error

    print("✅ Dataset ingestion completed successfully.")


if __name__ == "__main__":
    main()