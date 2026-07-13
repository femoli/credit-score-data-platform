"""
Application settings.

This module centralizes application configuration, project paths, and
shared constants used across the data platform.

Application modules should import configuration from this module
instead of hardcoding paths or constants.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Project Paths
# =============================================================================

# Root directory of the project
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Landing zone for raw datasets
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"

# =============================================================================
# Medallion Architecture Paths
# =============================================================================

# Bronze layer
BRONZE_DATA_PATH = PROJECT_ROOT / "data" / "bronze"

# Silver layer
SILVER_DATA_PATH = PROJECT_ROOT / "data" / "silver"

# Gold layer
GOLD_DATA_PATH = PROJECT_ROOT / "data" / "gold"

# =============================================================================
# Dataset Configuration
# =============================================================================

# Official Kaggle dataset used by the ingestion pipeline
DATASET_REF = "parisrohan/credit-score-classification"

# =============================================================================
# Google Cloud Storage Configuration
# =============================================================================

GCP_PROJECT_ID = os.getenv(
    "GCP_PROJECT_ID",
    "credit-score-data-platform",
)

GCS_BUCKET_NAME = os.getenv(
    "GCS_BUCKET_NAME",
    "",
)

GCS_PREFIX = os.getenv(
    "GCS_PREFIX",
    "credit-score-data-platform",
)