from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import magic
import logging
import io
from app.services.pdf_service import PDFService
from app.services.qr_service import QRService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/add-qr-to-pdf/")
async def add_qr_to_pdf(
    pdf_file: UploadFile,
    qr_content: str
) -> StreamingResponse:
    """Add QR code to the first page of a PDF file."""
    try:
        logger.info(f"Processing file: {pdf_file.filename}")
        
        # Validate PDF mime type
        first_chunk = await pdf_file.read(2048)
        content_type = magic.from_buffer(first_chunk, mime=True)
        if content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Uploaded file is not a PDF")
        
        # Read complete file
        await pdf_file.seek(0)
        pdf_bytes = first_chunk + await pdf_file.read()
        
        # Validate PDF
        if not PDFService.validate_pdf(pdf_bytes):
            raise HTTPException(status_code=400, detail="Invalid or corrupted PDF file")
        
        # Get page dimensions
        page_width, page_height = PDFService.get_page_dimensions(pdf_bytes)
        
        # Generate QR code
        qr_svg = QRService.generate_qr_code_svg(qr_content)
        qr_overlay = QRService.create_qr_overlay(qr_svg, page_width, page_height)
        
        # Merge PDF with QR code
        result_bytes = PDFService.merge_pdf_pages(pdf_bytes, qr_overlay)
        
        logger.info("PDF processing completed successfully")
        
        return StreamingResponse(
            io.BytesIO(result_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=modified_{pdf_file.filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 