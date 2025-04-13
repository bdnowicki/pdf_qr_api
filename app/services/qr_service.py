import io
import qrcode
import qrcode.image.svg
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class QRService:
    @staticmethod
    def generate_qr_code_svg(content: str) -> bytes:
        """Generate QR code as SVG bytes."""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(content)
            qr.make(fit=True)
            
            factory = qrcode.image.svg.SvgPathImage
            img = qr.make_image(image_factory=factory)
            
            svg_stream = io.BytesIO()
            img.save(svg_stream)
            svg_stream.seek(0)
            return svg_stream.getvalue()
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            raise

    @staticmethod
    def create_qr_overlay(qr_svg: bytes, page_width: float, page_height: float) -> bytes:
        """Create PDF overlay with QR code."""
        try:
            # Convert SVG to drawing
            svg_file = io.BytesIO(qr_svg)
            drawing = svg2rlg(svg_file)
            
            # Resize drawing to configured size
            drawing.scale(
                settings.QR_CODE_SIZE/drawing.width,
                settings.QR_CODE_SIZE/drawing.height
            )
            
            # Create PDF overlay
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))
            
            # Calculate QR code position
            x = page_width - settings.QR_CODE_SIZE - settings.QR_CODE_MARGIN - settings.QR_CODE_PADDING
            y = page_height - settings.QR_CODE_SIZE - settings.QR_CODE_MARGIN - settings.QR_CODE_PADDING
            
            # Draw white background
            can.setFillColorRGB(1, 1, 1)
            can.rect(
                x - settings.QR_CODE_PADDING,
                y - settings.QR_CODE_PADDING,
                settings.QR_CODE_SIZE + 2*settings.QR_CODE_PADDING,
                settings.QR_CODE_SIZE + 2*settings.QR_CODE_PADDING,
                fill=1,
                stroke=1
            )
            
            # Add QR code
            renderPDF.draw(drawing, can, x, y)
            can.save()
            packet.seek(0)
            return packet.getvalue()
        except Exception as e:
            logger.error(f"Error creating QR overlay: {str(e)}")
            raise 