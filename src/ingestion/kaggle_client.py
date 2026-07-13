"""
Kaggle client.

This module handles authentication and communication with the Kaggle API.

Its responsibility is to download the dataset into the Raw layer,
representing the Extract stage of the ETL pipeline.
"""

import logging

from src.config.settings import DATASET_REF
from src.ingestion.kaggle_auth import ensure_kaggle_credentials


logger = logging.getLogger(__name__)


def download_dataset(output_dir: str) -> None:
    """
    Download and extract the dataset from Kaggle.

    Args:
        output_dir: Destination directory for the downloaded dataset.
    """
    logger.info("Checking Kaggle authentication.")

    ensure_kaggle_credentials()

    # Imported only after credentials have been prepared.
    # Some Kaggle client versions validate authentication during import.
    from kaggle.api.kaggle_api_extended import KaggleApi

    logger.info("Connecting to the Kaggle API.")

    api = KaggleApi()
    api.authenticate()

    logger.info(
        "Downloading Kaggle dataset: %s",
        DATASET_REF,
    )

    api.dataset_download_files(
        dataset=DATASET_REF,
        path=output_dir,
        unzip=True,
        quiet=False,
    )

    logger.info("Kaggle dataset downloaded and extracted successfully.")