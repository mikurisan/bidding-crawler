from .logging import setup_logger
from .dependencies import get_crawler_manager
from .lifespan import create_instance

__version__ = "1.0.0"

__all__ = [
    "setup_logger",
    "get_crawler_manager",
    "create_instance"
]