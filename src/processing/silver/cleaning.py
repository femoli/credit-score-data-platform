"""
Silver layer cleaning functions.

Provides reusable cleaning transformations applied before type conversion.
"""

import re

import pandas as pd

# =============================================================================
# Constants
# =============================================================================

INVALID_VALUES = {
    "",
    "_",
    "__",
    "___",
    "____",
    "_______",
    "!@9#%8",
    "__-333333333333333333333333333__",
}

# =============================================================================
# Functions
# =============================================================================


def standardize_column_names(
    dataframe: pd.DataFrame,
    rename_mapping: dict[str, str],
) -> pd.DataFrame:
    """Rename dataframe columns using the Silver schema mapping."""
    return dataframe.rename(columns=rename_mapping)


def replace_invalid_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Replace known invalid values with missing values."""
    return dataframe.replace(list(INVALID_VALUES), pd.NA)


def clean_numeric_text(series: pd.Series) -> pd.Series:
    """Clean numeric text values before type conversion."""
    return (
        series.astype("string")
        .str.replace("_", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )


def remove_pii_columns(
    dataframe: pd.DataFrame,
    pii_columns: list[str],
) -> pd.DataFrame:
    """Remove personally identifiable information columns."""
    return dataframe.drop(columns=pii_columns, errors="ignore")


def replace_out_of_range_values(
    dataframe: pd.DataFrame,
    schema: dict[str, dict],
) -> pd.DataFrame:
    """Replace numeric values outside configured ranges with missing values."""
    for column, rules in schema.items():
        if column not in dataframe.columns:
            continue

        minimum = rules.get("min")
        maximum = rules.get("max")

        if minimum is not None:
            dataframe.loc[dataframe[column] < minimum, column] = pd.NA

        if maximum is not None:
            dataframe.loc[dataframe[column] > maximum, column] = pd.NA

    return dataframe