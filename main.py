from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from PyPDF2 import PdfReader, PdfWriter
import qrcode
import qrcode.image.svg
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import magic
import logging
import traceback
import warnings

# Configure logging - INFO level for main app, WARNING for svglib, ERROR for PyPDF2
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('svglib.svglib').setLevel(logging.WARNING)
logging.getLogger('PyPDF2').setLevel(logging.ERROR)

app = FastAPI(title="PDF QR Code API")

def generate_qr_code_svg(content: str) -> bytes:
    """Generate QR code as SVG bytes.
    
    Args:
        content: String to encode in the QR code
        
    Returns:
        bytes: SVG representation of the QR code
        
    Raises:
        Exception: If QR code generation fails
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)
        
        # Use SvgPathImage for simpler SVG output with fewer styling issues
        factory = qrcode.image.svg.SvgPathImage
        img = qr.make_image(image_factory=factory)
        
        # Convert to bytes for further processing
        svg_stream = io.BytesIO()
        img.save(svg_stream)
        svg_stream.seek(0)
        return svg_stream.getvalue()
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def validate_pdf(pdf_bytes: bytes) -> bool:
    """Validate PDF file structure and basic content.
    
    Args:
        pdf_bytes: Raw PDF file content
        
    Returns:
        bool: True if PDF is valid, False otherwise
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
        if len(reader.pages) == 0:
            return False
        _ = reader.pages[0]  # Verify first page is accessible
        return True
    except Exception as e:
        logger.error(f"PDF validation failed: {str(e)}")
        return False

def add_qr_to_pdf(pdf_bytes: bytes, qr_content: str) -> bytes:
    """Add QR code to the first page of PDF.
    
    Places a QR code with white background in the top-right corner of the first page.
    
    Args:
        pdf_bytes: Raw PDF file content
        qr_content: Content to encode in QR code
        
    Returns:
        bytes: Modified PDF content
        
    Raises:
        HTTPException: If PDF is invalid or processing fails
    """
    try:
        # Validate input PDF
        if not validate_pdf(pdf_bytes):
            raise HTTPException(status_code=400, detail="Invalid or corrupted PDF file")

        # Read PDF with relaxed parsing
        pdf_stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream, strict=False)
        writer = PdfWriter()
        
        if len(reader.pages) == 0:
            raise HTTPException(status_code=400, detail="PDF file is empty")
        
        # Get page dimensions
        first_page = reader.pages[0]
        page_width = float(first_page.mediabox.width)
        page_height = float(first_page.mediabox.height)
        
        # Generate and convert QR code
        qr_svg = generate_qr_code_svg(qr_content)
        svg_file = io.BytesIO(qr_svg)
        drawing = svg2rlg(svg_file)
        
        # Create QR code overlay
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))
        
        # Calculate adaptive QR code size
        min_qr_size = 100  # Minimum readable size in points
        max_qr_size = min(page_width, page_height) * 0.2
        target_size = (page_width * page_height) ** 0.3 * 0.1
        qr_size = max(min_qr_size, min(target_size, max_qr_size))
        
        # Position QR code in top-right corner with margins
        margin = 20  # Edge margin in points
        padding = 2  # Background padding in points
        x = page_width - qr_size - margin - padding
        y = page_height - qr_size - margin - padding 
        
        # Draw white background for contrast
        can.setFillColorRGB(1, 1, 1)
        can.rect(x - padding, y - padding, qr_size + 2*padding, qr_size + 2*padding, fill=1, stroke=0)
        
        # Add QR code and merge with original
        renderPDF.draw(drawing, can, x, y)
        can.save()
        packet.seek(0)
        
        qr_pdf = PdfReader(packet)
        first_page.merge_page(qr_pdf.pages[0])
        
        # Write all pages to output
        writer.add_page(first_page)
        for page in reader.pages[1:]:
            writer.add_page(page)
        
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream.getvalue()
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.post("/add-qr-to-pdf/")
async def add_qr_to_pdf_endpoint(
    pdf_file: UploadFile,
    qr_content: str
):
    """Add QR code to the first page of a PDF file.
    
    Args:
        pdf_file: PDF file to modify
        qr_content: Content to encode in the QR code
    
    Returns:
        StreamingResponse: Modified PDF file as attachment
        
    Raises:
        HTTPException: If file is not PDF or processing fails
    """
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
        
        # Process and return result
        result_bytes = add_qr_to_pdf(pdf_bytes, qr_content)
        logger.info("PDF processing completed successfully")
        
        return StreamingResponse(
            io.BytesIO(result_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=modified_{pdf_file.filename}"
            }
        )
    except Exception as e:
        logger.error(f"Error in endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) 