import logging
import sys
from typing import Dict

def configure_logging() -> None:
    """Configure logging for the application."""
    print("\n=== Configuring logging ===")
    
    # Configure root logger with console handler
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    loggers: Dict[str, int] = {
        'svglib.svglib': logging.WARNING,
        'PyPDF2': logging.ERROR,
        'pypdf': logging.ERROR,
        'uvicorn': logging.INFO,
        'fastapi': logging.INFO,
        'app.api.endpoints.pdf_qr': logging.INFO,
        'app.middleware.logging_middleware': logging.INFO,
        'pdf_qr_api.main': logging.INFO,
        '__main__': logging.INFO
    }
    
    print("=== Setting up loggers ===")
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        if not logger.handlers:  # Only add handler if none exists
            logger.addHandler(console_handler)
        print(f"Configured logger: {logger_name} with level {level}")
    
    print("=== Logging configuration complete ===\n") 