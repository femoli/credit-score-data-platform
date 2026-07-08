"""
Logging utilities.

Provides a centralized logger configuration for the project.
"""

import logging

# =============================================================================
# Constants
# =============================================================================

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


# =============================================================================
# Functions
# =============================================================================

def get_logger(name: str) -> logging.Logger:
    """Create and return a configured logger.

    Args:
        name: Logger name, usually the module name.

    Returns:
        A configured logger instance.
    """
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
    )

    return logging.getLogger(name)