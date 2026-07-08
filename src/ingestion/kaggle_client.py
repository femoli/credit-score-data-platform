"""
Kaggle client.

This module handles communication with the Kaggle API.
Its responsibility is to download the dataset into the Raw layer,
representing the Extract stage of the ETL pipeline.
"""

from kaggle.api.kaggle_api_extended import KaggleApi

from src.config.settings import DATASET_REF


def download_dataset(output_dir: str) -> None:
    """
    Download and extract the dataset from Kaggle.

    Args:
        output_dir: Destination directory for the downloaded dataset.
    """

    api = KaggleApi()
    api.authenticate()

    api.dataset_download_files(
        dataset=DATASET_REF,
        path=output_dir,
        unzip=True,
        quiet=False,
    )