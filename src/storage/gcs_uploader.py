"""
Google Cloud Storage uploader.

This module uploads processed Gold layer datasets to Google Cloud
Storage while preserving their local directory structure.
"""

from pathlib import Path

from google.api_core.exceptions import GoogleAPIError
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage

from src.config.settings import (
    GCP_PROJECT_ID,
    GCS_BUCKET_NAME,
    GCS_PREFIX,
    GOLD_DATA_PATH,
)
from src.observability.logger import get_logger


logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = {".parquet", ".csv"}


def normalize_prefix(prefix: str) -> str:
    """Remove leading and trailing slashes from a storage prefix."""
    return prefix.strip().strip("/")


def find_uploadable_files(source_directory: Path) -> list[Path]:
    """Return all supported files found recursively in a directory."""
    if not source_directory.exists():
        raise FileNotFoundError(
            f"Source directory does not exist: {source_directory}"
        )

    files = sorted(
        path
        for path in source_directory.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        raise ValueError(
            f"No Parquet or CSV files found in: {source_directory}"
        )

    return files


def build_blob_name(
    file_path: Path,
    source_directory: Path,
    prefix: str,
) -> str:
    """Build the destination object name preserving local folders."""
    relative_path = file_path.relative_to(source_directory).as_posix()
    normalized_prefix = normalize_prefix(prefix)

    parts = [
        part
        for part in (
            normalized_prefix,
            "gold",
            relative_path,
        )
        if part
    ]

    return "/".join(parts)


def create_storage_client(
    project_id: str,
) -> storage.Client:
    """Create an authenticated Google Cloud Storage client."""
    return storage.Client(project=project_id)


def upload_file(
    file_path: Path,
    bucket_name: str,
    blob_name: str,
    client: storage.Client,
) -> None:
    """Upload one local file to Google Cloud Storage."""
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    logger.info(
        "Uploading file to GCS: file=%s bucket=%s object=%s",
        file_path,
        bucket_name,
        blob_name,
    )

    blob.upload_from_filename(str(file_path))

    logger.info(
        "GCS upload completed: gs://%s/%s",
        bucket_name,
        blob_name,
    )


def upload_gold_layer(
    source_directory: Path = GOLD_DATA_PATH,
    project_id: str = GCP_PROJECT_ID,
    bucket_name: str = GCS_BUCKET_NAME,
    prefix: str = GCS_PREFIX,
    client: storage.Client | None = None,
) -> list[str]:
    """Upload every supported Gold layer file to GCS."""
    if not project_id:
        raise ValueError("GCP_PROJECT_ID is not configured.")

    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME is not configured.")

    files = find_uploadable_files(source_directory)

    try:
        storage_client = client or create_storage_client(project_id)
        uploaded_objects: list[str] = []

        for file_path in files:
            blob_name = build_blob_name(
                file_path=file_path,
                source_directory=source_directory,
                prefix=prefix,
            )

            upload_file(
                file_path=file_path,
                bucket_name=bucket_name,
                blob_name=blob_name,
                client=storage_client,
            )

            uploaded_objects.append(blob_name)

    except DefaultCredentialsError as error:
        raise RuntimeError(
            "Google Cloud credentials were not found. Run "
            "'gcloud auth application-default login'."
        ) from error

    except GoogleAPIError as error:
        raise RuntimeError(
            f"Google Cloud Storage upload failed: {error}"
        ) from error

    logger.info(
        "Gold layer upload completed: files=%s bucket=%s",
        len(uploaded_objects),
        bucket_name,
    )

    return uploaded_objects


def main() -> None:
    """Run the Gold layer cloud upload."""
    try:
        uploaded_objects = upload_gold_layer()

        logger.info(
            "Cloud upload pipeline completed successfully: files=%s",
            len(uploaded_objects),
        )

    except (
        FileNotFoundError,
        ValueError,
        RuntimeError,
    ) as error:
        logger.error("Cloud upload pipeline failed: %s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()