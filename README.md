# PDF QR Code API

A FastAPI-based service that adds QR codes to PDF documents. The service places a QR code with a white background in the top-right corner of the first page of any PDF document.

## Features

- Adds QR codes to PDF documents
- Maintains original PDF quality and content
- Configurable QR code sizing and positioning
- White background for QR code visibility
- Supports all PDF formats (with relaxed parsing)
- Input validation and error handling
- Swagger UI for easy testing
- Comprehensive test coverage

## Technical Details

- QR code placement: Top-right corner with configurable margins
- QR code size: Configurable through settings
  - Size and margins can be adjusted in configuration
  - Includes padding for better visibility
- White background padding: Configurable through settings
- Edge margin: Configurable through settings

## API Endpoint

### POST /add-qr-to-pdf/

Adds a QR code to the first page of a PDF file.

**Parameters:**
- `pdf_file`: PDF file to modify (multipart/form-data)
- `qr_content`: Content to encode in the QR code (query parameter)

**Returns:**
- Modified PDF file as attachment

## Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python -m uvicorn main:app --reload
```

3. Access the Swagger UI:
```
http://127.0.0.1:8000/docs
```

4. Use the /add-qr-to-pdf/ endpoint to upload a PDF and specify QR content

## Dependencies

- FastAPI
- pypdf (>=4.0.0)
- qrcode[svg]
- reportlab
- svglib
- python-magic-bin
- pydantic and pydantic-settings
- Testing: pytest, pytest-asyncio, pytest-cov, httpx

## Error Handling

- Validates PDF structure before processing
- Checks file MIME type
- Provides detailed error messages
- Comprehensive logging system
- Error tracking and debugging support

## Development

The project includes:
- Comprehensive test suite with pytest
- Code coverage reporting
- Async testing support
- Development server with auto-reload
- Editor configuration (.editorconfig)

## Testing

Run tests with coverage:
```bash
pytest --cov=app tests/
```

View coverage report:
```bash
pytest --cov=app --cov-report=html tests/
```

## Notes

- The service modifies only the first page of the PDF
- Original PDF pages after the first page remain unchanged
- QR codes include error correction
- White background ensures readability on any document
- All QR code parameters are configurable through settings
