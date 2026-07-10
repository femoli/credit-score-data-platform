"""
Dataset inspection utility.

Displays dataset information useful during development.
"""

import pandas as pd

from src.config.settings import BRONZE_DATA_PATH


def inspect_dataset() -> None:
    """Display basic information about the Bronze dataset."""
    dataframe = pd.read_parquet(BRONZE_DATA_PATH / "train.parquet")

    print(dataframe.info())
    print()
    print(dataframe.head())
    print()
    print(dataframe.describe(include="all"))
    print()
    print(dataframe.isna().sum())


if __name__ == "__main__":
    inspect_dataset()