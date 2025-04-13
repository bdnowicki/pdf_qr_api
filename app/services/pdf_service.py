from typing import Tuple
import io
from PyPDF2 import PdfReader, PdfWriter
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class PDFService:
    @staticmethod
    def validate_pdf(pdf_bytes: bytes) -> bool:
        """Validate PDF file structure and basic content."""
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
            if len(reader.pages) == 0:
                return False
            _ = reader.pages[0]  # Verify first page is accessible
            return True
        except Exception as e:
            logger.error(f"PDF validation failed: {str(e)}")
            return False

    @staticmethod
    def get_page_dimensions(pdf_bytes: bytes) -> Tuple[float, float]:
        """Get dimensions of the first page of a PDF."""
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
            if len(reader.pages) == 0:
                raise HTTPException(status_code=400, detail="PDF file is empty")
            
            first_page = reader.pages[0]
            return float(first_page.mediabox.width), float(first_page.mediabox.height)
        except Exception as e:
            logger.error(f"Error getting page dimensions: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid PDF file")

    @staticmethod
    def merge_pdf_pages(original_pdf: bytes, qr_overlay: bytes) -> bytes:
        """Merge original PDF with QR code overlay."""
        try:
            reader = PdfReader(io.BytesIO(original_pdf), strict=False)
            writer = PdfWriter()
            
            # Merge first page with QR code
            first_page = reader.pages[0]
            qr_reader = PdfReader(io.BytesIO(qr_overlay))
            first_page.merge_page(qr_reader.pages[0])
            
            # Add all pages to output
            writer.add_page(first_page)
            for page in reader.pages[1:]:
                writer.add_page(page)
            
            output_stream = io.BytesIO()
            writer.write(output_stream)
            output_stream.seek(0)
            return output_stream.getvalue()
        except Exception as e:
            logger.error(f"Error merging PDF pages: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing PDF") 