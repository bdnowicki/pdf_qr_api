from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import pdf_qr
from app.core.logging import configure_logging
from app.middleware.logging_middleware import LoggingMiddleware
import logging

# Configure logging
configure_logging()

# Get logger
logger = logging.getLogger(__name__)
print("\n=== Initializing FastAPI application ===")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION
)

# Add logging middleware
print("\n=== Adding LoggingMiddleware ===")
app.add_middleware(LoggingMiddleware)
print("=== LoggingMiddleware added successfully ===\n")

# Include routers
app.include_router(pdf_qr.router, prefix="/api/v1", tags=["pdf-qr"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 