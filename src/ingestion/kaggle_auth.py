"""
Kaggle authentication helpers.

This module prepares Kaggle credentials for local execution across
Linux, macOS, Windows and Windows Subsystem for Linux (WSL).

When running inside WSL, the module can discover a valid kaggle.json
stored in a mounted Windows user profile and securely copy it to the
current Linux user profile.

Credential values are never logged or exposed.
"""

from __future__ import annotations

import json
import logging
import os
import platform
import shutil
from pathlib import Path


logger = logging.getLogger(__name__)

KAGGLE_DIRECTORY = Path.home() / ".kaggle"
KAGGLE_CREDENTIALS_PATH = KAGGLE_DIRECTORY / "kaggle.json"

WINDOWS_USERS_PATH = Path("/mnt/c/Users")

IGNORED_WINDOWS_PROFILES = {
    "All Users",
    "Default",
    "Default User",
    "Public",
    "defaultuser0",
}


class KaggleAuthenticationError(RuntimeError):
    """Raised when Kaggle credentials cannot be configured."""


def is_wsl() -> bool:
    """Return whether the application is running inside WSL."""
    release = platform.uname().release.lower()

    try:
        version = Path("/proc/version").read_text(
            encoding="utf-8",
        ).lower()
    except OSError:
        version = ""

    return "microsoft" in release or "microsoft" in version


def is_valid_kaggle_credentials(path: Path) -> bool:
    """
    Return whether a file contains valid Kaggle credentials.

    A valid legacy kaggle.json file must contain non-empty
    username and key fields.
    """
    if not path.is_file():
        return False

    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False

    if not isinstance(content, dict):
        return False

    username = content.get("username")
    key = content.get("key")

    return (
        isinstance(username, str)
        and bool(username.strip())
        and isinstance(key, str)
        and bool(key.strip())
    )


def find_windows_kaggle_credentials() -> list[Path]:
    """
    Find valid kaggle.json files in Windows profiles mounted by WSL.

    Returns:
        Sorted list of valid credential file paths.
    """
    if not WINDOWS_USERS_PATH.is_dir():
        return []

    candidates: list[Path] = []

    try:
        profiles = WINDOWS_USERS_PATH.iterdir()
    except OSError:
        return []

    for profile in profiles:
        if not profile.is_dir():
            continue

        if profile.name in IGNORED_WINDOWS_PROFILES:
            continue

        candidate = profile / ".kaggle" / "kaggle.json"

        if is_valid_kaggle_credentials(candidate):
            candidates.append(candidate)

    return sorted(candidates)


def copy_credentials(source: Path, destination: Path) -> None:
    """
    Copy Kaggle credentials using restricted file permissions.

    Args:
        source: Existing valid credential file.
        destination: Credential path for the current environment.

    Raises:
        KaggleAuthenticationError: If the file cannot be copied or secured.
    """
    try:
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copyfile(
            source,
            destination,
        )

        destination.chmod(0o600)

    except OSError as error:
        destination.unlink(missing_ok=True)

        raise KaggleAuthenticationError(
            "Kaggle credentials were found, but they could not be copied "
            "and configured with safe permissions."
        ) from error


def ensure_kaggle_credentials() -> Path | None:
    """
    Ensure Kaggle authentication is available for the current environment.

    Authentication priority:

    1. KAGGLE_API_TOKEN environment variable
    2. Existing ~/.kaggle/kaggle.json
    3. Valid Windows kaggle.json discovered automatically from WSL

    Returns:
        The local kaggle.json path when file-based authentication is used,
        or None when KAGGLE_API_TOKEN is configured.

    Raises:
        KaggleAuthenticationError: If valid credentials cannot be found.
    """
    if os.getenv("KAGGLE_API_TOKEN"):
        logger.info(
            "Kaggle authentication found in the "
            "KAGGLE_API_TOKEN environment variable."
        )
        return None

    if is_valid_kaggle_credentials(KAGGLE_CREDENTIALS_PATH):
        try:
            KAGGLE_CREDENTIALS_PATH.chmod(0o600)
        except OSError:
            logger.warning(
                "Valid Kaggle credentials were found at %s, but their "
                "permissions could not be updated.",
                KAGGLE_CREDENTIALS_PATH,
            )

        logger.info(
            "Valid Kaggle credentials found at %s.",
            KAGGLE_CREDENTIALS_PATH,
        )

        return KAGGLE_CREDENTIALS_PATH

    if not is_wsl():
        raise KaggleAuthenticationError(
            "Kaggle credentials were not found.\n\n"
            "Generate a Kaggle Legacy API Key and save kaggle.json at:\n"
            f"  {KAGGLE_CREDENTIALS_PATH}\n\n"
            "Then execute the ingestion pipeline again."
        )

    logger.info(
        "Local WSL Kaggle credentials were not found. "
        "Searching mounted Windows user profiles."
    )

    candidates = find_windows_kaggle_credentials()

    if not candidates:
        raise KaggleAuthenticationError(
            "Kaggle credentials were not found in WSL or in the mounted "
            "Windows user profiles.\n\n"
            "Generate a Kaggle Legacy API Key and save kaggle.json at:\n"
            "  C:\\Users\\<your-user>\\.kaggle\\kaggle.json\n\n"
            "The next execution will import it automatically into WSL."
        )

    if len(candidates) > 1:
        locations = "\n".join(
            f"  - {candidate}"
            for candidate in candidates
        )

        raise KaggleAuthenticationError(
            "Multiple valid Kaggle credential files were found:\n"
            f"{locations}\n\n"
            "For safety, copy the desired file manually to:\n"
            f"  {KAGGLE_CREDENTIALS_PATH}"
        )

    source = candidates[0]

    logger.info(
        "Valid Kaggle credentials found in a Windows user profile."
    )

    copy_credentials(
        source=source,
        destination=KAGGLE_CREDENTIALS_PATH,
    )

    logger.info(
        "Kaggle credentials were securely imported into WSL at %s.",
        KAGGLE_CREDENTIALS_PATH,
    )

    return KAGGLE_CREDENTIALS_PATH
