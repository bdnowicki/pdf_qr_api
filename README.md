# PDF QR Code API

A FastAPI-based service that adds QR codes to PDF documents. The service places a QR code with a white background in the top-right corner of the first page of any PDF document.

## Features

- Adds QR codes to PDF documents
- Maintains original PDF quality and content
- Adaptive QR code sizing based on page dimensions
- White background for QR code visibility
- Supports all PDF formats (with relaxed parsing)
- Input validation and error handling
- Swagger UI for easy testing

## Technical Details

- QR code placement: Top-right corner with configurable margins
- QR code size: Adaptive, based on page dimensions
  - Minimum size: 100 points (for readability)
  - Maximum size: 20% of smallest page dimension
  - Target size: Calculated based on page area
- White background padding: 2 points
- Edge margin: 20 points

## API Endpoint

### POST /add-qr-to-pdf/

Adds a QR code to the first page of a PDF file.

**Parameters:**
- `pdf_file`: PDF file to modify (multipart/form-data)
- `qr_content`: Content to encode in the QR code (query parameter)

**Returns:**
- Modified PDF file as attachment

## Usage

1. Start the server:
```bash
python -m pip install uvicorn
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

2. Access the Swagger UI:
```
http://127.0.0.1:8000/docs
```

3. Use the /add-qr-to-pdf/ endpoint to upload a PDF and specify QR content

## Dependencies

- FastAPI
- PyPDF2
- qrcode
- reportlab
- svglib
- python-magic

## Error Handling

- Validates PDF structure before processing
- Checks file MIME type
- Provides detailed error messages
- Logs errors for debugging

## Development

The code includes comprehensive logging:
- INFO level for main application
- WARNING level for svglib
- ERROR level for PyPDF2

## Notes

- The service modifies only the first page of the PDF
- Original PDF pages after the first page remain unchanged
- QR codes include error correction
- White background ensures readability on any document 
