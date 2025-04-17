from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import mimetypes
import logging
import io
from app.services.pdf_service import PDFService
from app.services.qr_service import QRService
from app.core.config import settings
import urllib.parse
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/add-qr-to-pdf/")
async def add_qr_to_pdf(
    pdf_file: UploadFile,
    qr_content: str
) -> StreamingResponse:
    """Add QR code to the first page of a PDF file."""
    logger.info(f"Received request to add QR code to PDF. Filename: {pdf_file.filename}, QR content length: {len(qr_content)}")
    try:
        # Early validation of QR content
        if not qr_content.strip():
            raise HTTPException(status_code=400, detail="QR content cannot be empty")
            
        # Properly handle Unicode filename
        filename = pdf_file.filename
        if isinstance(filename, str):
            filename = urllib.parse.unquote(filename)
        logger.info(f"Processing file: {filename}")
        
        # Validate PDF mime type
        content_type, _ = mimetypes.guess_type(filename)
        logger.debug(f"Detected file type: {content_type}")
        if content_type != "application/pdf":
            logger.warning(f"Invalid file type received: {content_type}")
            raise HTTPException(status_code=400, detail="Uploaded file is not a PDF")
        
        # Read complete file
        pdf_bytes = await pdf_file.read()
        logger.debug(f"PDF file size: {len(pdf_bytes)} bytes")
        
        # Validate PDF
        if not PDFService.validate_pdf(pdf_bytes):
            logger.warning("Invalid or corrupted PDF file received")
            raise HTTPException(status_code=400, detail="Invalid or corrupted PDF file")
        
        # Get page dimensions
        page_width, page_height = PDFService.get_page_dimensions(pdf_bytes)
        logger.debug(f"PDF page dimensions: {page_width}x{page_height}")
        
        # Generate QR code
        qr_svg = await asyncio.to_thread(QRService.generate_qr_code_svg, qr_content)
        
        # Create QR overlay
        qr_overlay = await asyncio.to_thread(QRService.create_qr_overlay, qr_svg, page_width, page_height)
        
        # Merge PDF with QR code
        result_bytes = await PDFService.merge_pdf_pages(pdf_bytes, qr_overlay)
        
        logger.info(f"PDF processing completed successfully. Output file size: {len(result_bytes)} bytes")
        
        return StreamingResponse(
            io.BytesIO(result_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{urllib.parse.quote(filename)}"'
            }
        )
    except HTTPException:
        # Re-raise HTTP exceptions to maintain their status codes
        raise
    except Exception as e:
        logger.error(f"Error in endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 