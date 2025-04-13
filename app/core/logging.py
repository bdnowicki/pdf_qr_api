import logging
from typing import Dict

def configure_logging() -> None:
    """Configure logging for the application."""
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure specific loggers
    loggers: Dict[str, int] = {
        'svglib.svglib': logging.WARNING,
        'PyPDF2': logging.ERROR,
        'pypdf': logging.ERROR,
        'uvicorn': logging.INFO,
        'fastapi': logging.INFO
    }
    
    for logger_name, level in loggers.items():
        logging.getLogger(logger_name).setLevel(level) 