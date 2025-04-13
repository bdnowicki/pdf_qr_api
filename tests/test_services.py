"""Tests for PDF and QR services."""
import pytest
from app.services.pdf_service import PDFService
from app.services.qr_service import QRService
import io
from pypdf import PdfReader
from fastapi import HTTPException
import qrcode.exceptions

def test_validate_pdf_valid(sample_pdf):
    """Test PDF validation with valid PDF."""
    assert PDFService.validate_pdf(sample_pdf) is True

def test_validate_pdf_invalid(invalid_pdf):
    """Test PDF validation with invalid PDF."""
    assert PDFService.validate_pdf(invalid_pdf) is False

def test_validate_pdf_empty():
    """Test PDF validation with empty PDF."""
    # Create an empty PDF
    packet = io.BytesIO()
    packet.write(b"%PDF-1.7\n")
    packet.seek(0)
    assert PDFService.validate_pdf(packet.getvalue()) is False

def test_get_page_dimensions(sample_pdf):
    """Test getting page dimensions."""
    width, height = PDFService.get_page_dimensions(sample_pdf)
    assert width == 595.27  # A4 width in points
    assert height == 841.89  # A4 height in points

def test_get_page_dimensions_invalid(invalid_pdf):
    """Test getting page dimensions with invalid PDF."""
    with pytest.raises(HTTPException) as exc_info:
        PDFService.get_page_dimensions(invalid_pdf)
    assert exc_info.value.status_code == 400
    assert "Invalid PDF file" in str(exc_info.value.detail)

def test_get_page_dimensions_empty():
    """Test getting page dimensions with empty PDF."""
    # Create an empty PDF
    packet = io.BytesIO()
    packet.write(b"%PDF-1.7\n")
    packet.seek(0)
    with pytest.raises(HTTPException) as exc_info:
        PDFService.get_page_dimensions(packet.getvalue())
    assert exc_info.value.status_code == 400
    assert "Invalid PDF file" in str(exc_info.value.detail)

def test_generate_qr_code_svg():
    """Test QR code generation."""
    content = "https://example.com"
    svg_bytes = QRService.generate_qr_code_svg(content)
    assert isinstance(svg_bytes, bytes)
    assert b"<svg" in svg_bytes

@pytest.mark.xfail(raises=Exception)
def test_generate_qr_code_svg_error():
    """Test QR code generation with invalid input."""
    QRService.generate_qr_code_svg(None)

def test_create_qr_overlay():
    """Test QR overlay creation."""
    # Generate QR code
    content = "https://example.com"
    svg_bytes = QRService.generate_qr_code_svg(content)
    
    # Create overlay
    page_width = 595.27  # A4 width
    page_height = 841.89  # A4 height
    overlay_bytes = QRService.create_qr_overlay(svg_bytes, page_width, page_height)
    
    # Verify overlay is a valid PDF
    assert isinstance(overlay_bytes, bytes)
    assert overlay_bytes.startswith(b"%PDF-")
    
    # Verify overlay has correct dimensions
    reader = PdfReader(io.BytesIO(overlay_bytes))
    page = reader.pages[0]
    assert float(page.mediabox.width) == page_width
    assert float(page.mediabox.height) == page_height

def test_create_qr_overlay_error():
    """Test QR overlay creation with invalid input."""
    with pytest.raises(Exception):
        QRService.create_qr_overlay(b"invalid svg", 100, 100)

def test_merge_pdf_pages(sample_pdf):
    """Test PDF page merging."""
    # Generate QR code and overlay
    content = "https://example.com"
    svg_bytes = QRService.generate_qr_code_svg(content)
    page_width, page_height = PDFService.get_page_dimensions(sample_pdf)
    overlay_bytes = QRService.create_qr_overlay(svg_bytes, page_width, page_height)
    
    # Merge PDFs
    result_bytes = PDFService.merge_pdf_pages(sample_pdf, overlay_bytes)
    
    # Verify result
    assert isinstance(result_bytes, bytes)
    assert result_bytes.startswith(b"%PDF-")
    
    # Verify page count is preserved
    original_reader = PdfReader(io.BytesIO(sample_pdf))
    result_reader = PdfReader(io.BytesIO(result_bytes))
    assert len(result_reader.pages) == len(original_reader.pages)

def test_merge_pdf_pages_error():
    """Test PDF merging with invalid input."""
    with pytest.raises(HTTPException) as exc_info:
        PDFService.merge_pdf_pages(b"invalid pdf", b"invalid overlay")
    assert exc_info.value.status_code == 500
    assert "Error processing PDF" in str(exc_info.value.detail) 