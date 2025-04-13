"""Tests for API endpoints."""
import pytest
from fastapi import UploadFile
import io
import magic
from unittest.mock import patch, MagicMock

def test_add_qr_to_pdf_success(client, sample_pdf, qr_content):
    """Test successful QR code addition to PDF."""
    # Create a file-like object for the PDF
    pdf_file = io.BytesIO(sample_pdf)
    files = {"pdf_file": ("test.pdf", pdf_file, "application/pdf")}
    
    # Make the request
    response = client.post(
        "/api/v1/add-qr-to-pdf/?qr_content=" + qr_content,
        files=files
    )
    
    # Check response
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    
    # Verify the response is a valid PDF
    pdf_content = response.content
    assert pdf_content.startswith(b"%PDF-")

def test_add_qr_to_pdf_invalid_file(client, invalid_pdf, qr_content):
    """Test handling of invalid PDF file."""
    # Create a file-like object for the invalid PDF
    pdf_file = io.BytesIO(invalid_pdf)
    files = {"pdf_file": ("test.pdf", pdf_file, "application/pdf")}
    
    # Make the request
    response = client.post(
        "/api/v1/add-qr-to-pdf/?qr_content=" + qr_content,
        files=files
    )
    
    # Check response
    assert response.status_code == 400
    assert "Uploaded file is not a PDF" in response.json()["detail"]

def test_add_qr_to_pdf_missing_file(client, qr_content):
    """Test handling of missing file."""
    response = client.post(
        "/api/v1/add-qr-to-pdf/?qr_content=" + qr_content
    )
    assert response.status_code == 422  # FastAPI validation error

def test_add_qr_to_pdf_missing_qr_content(client, sample_pdf):
    """Test handling of missing QR content."""
    pdf_file = io.BytesIO(sample_pdf)
    files = {"pdf_file": ("test.pdf", pdf_file, "application/pdf")}
    
    response = client.post(
        "/api/v1/add-qr-to-pdf/",
        files=files
    )
    assert response.status_code == 422  # FastAPI validation error

def test_add_qr_to_pdf_general_error(client, sample_pdf, qr_content):
    """Test handling of general exceptions."""
    pdf_file = io.BytesIO(sample_pdf)
    files = {"pdf_file": ("test.pdf", pdf_file, "application/pdf")}
    
    # Mock PDFService to raise an exception
    with patch("app.api.endpoints.pdf_qr.PDFService.validate_pdf", side_effect=Exception("Test error")):
        response = client.post(
            "/api/v1/add-qr-to-pdf/?qr_content=" + qr_content,
            files=files
        )
        
        assert response.status_code == 500
        assert "Test error" in response.json()["detail"]

def test_add_qr_to_pdf_corrupted_pdf(client, sample_pdf, qr_content):
    """Test handling of corrupted PDF file."""
    # Create a file-like object for the PDF
    pdf_file = io.BytesIO(sample_pdf)
    files = {"pdf_file": ("test.pdf", pdf_file, "application/pdf")}
    
    # Mock PDFService to indicate invalid PDF
    with patch("app.api.endpoints.pdf_qr.PDFService.validate_pdf", return_value=False):
        response = client.post(
            "/api/v1/add-qr-to-pdf/?qr_content=" + qr_content,
            files=files
        )
        
        assert response.status_code == 400
        assert "Invalid or corrupted PDF file" in response.json()["detail"] 