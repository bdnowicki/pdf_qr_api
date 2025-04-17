import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)
print("\n=== Initializing LoggingMiddleware ===")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log the incoming request
        message = f"Request received: {request.method} {request.url.path}"
        print(f"\n=== {message} ===")
        print(f"=== Request headers: {dict(request.headers)} ===")
        logger.info(message)
        
        # Process the request
        response = await call_next(request)
        
        return response 