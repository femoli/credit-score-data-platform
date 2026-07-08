"""
Metadata generator.

This module creates metadata for each ingestion execution,
providing basic data lineage and traceability for the pipeline.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def generate_metadata(output_dir: str, dataset_ref: str) -> None:
    """
    Generate metadata for a dataset ingestion execution.

    Args:
        output_dir: Directory containing the downloaded dataset.
        dataset_ref: Kaggle dataset identifier.
    """

    output_path = Path(output_dir)

    # Ignore the metadata file when listing downloaded assets
    files = [
        file.name
        for file in output_path.iterdir()
        if file.is_file() and file.name != "metadata.json"
    ]

    metadata = {
        "dataset_ref": dataset_ref,
        "source": "Kaggle",
        "ingestion_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "landing_zone": str(output_path),
        "files": files,
    }

    # Persist ingestion metadata for traceability
    with open(output_path / "metadata.json", "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)