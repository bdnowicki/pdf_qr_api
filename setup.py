from setuptools import setup, find_packages

setup(
    name="pdf_qr_api",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.88.0",
        "uvicorn>=0.24.0",
        "python-multipart==0.0.6",
        "pypdf>=4.0.0",
        "qrcode[svg]==7.4.2",
        "Pillow>=10.0.0",
        "reportlab==4.0.7",
        "python-magic-bin>=0.4.14; sys_platform == 'win32'",
        "python-magic>=0.4.27; sys_platform != 'win32'",
        "anyio>=4.5.0",
        "starlette>=0.41.3",
        "svglib==1.5.1",
        "pydantic-settings>=2.0.0",
        "pydantic>=2.0.0",
    ],
) 