from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "PDF QR Code API"
    PROJECT_DESCRIPTION: str = "API for adding QR codes to PDF documents"
    VERSION: str = "1.0.0"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # QR code settings
    QR_CODE_SIZE: int = 100
    QR_CODE_MARGIN: int = 20
    QR_CODE_PADDING: int = 2
    
    class Config:
        case_sensitive = True

settings = Settings() 