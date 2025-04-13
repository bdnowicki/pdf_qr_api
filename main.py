from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import pdf_qr
from app.core.logging import configure_logging

# Configure logging
configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION
)

# Include routers
app.include_router(pdf_qr.router, prefix="/api/v1", tags=["pdf-qr"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 