"""Test configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from main import app
import io
from pypdf import PdfWriter
from reportlab.pdfgen import canvas
import warnings

# Suppress ReportLab deprecation warning
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module="reportlab.*",
    message="ast.NameConstant is deprecated"
)

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing."""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(595.27, 841.89))  # A4 size
    can.drawString(100, 100, "Test PDF")
    can.save()
    packet.seek(0)
    return packet.getvalue()

@pytest.fixture
def invalid_pdf():
    """Create an invalid PDF file for testing."""
    return b"Not a PDF file"

@pytest.fixture
def qr_content():
    """Sample QR code content."""
    return "https://example.com" 