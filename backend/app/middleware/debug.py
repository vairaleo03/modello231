from fastapi import Request
import logging

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    """Middleware per loggare tutte le richieste"""
    logger.debug(f"📥 {request.method} {request.url}")
    logger.debug(f"📥 Headers: {dict(request.headers)}")
    logger.debug(f"📥 Cookies: {dict(request.cookies)}")
    
    response = await call_next(request)
    
    logger.debug(f"📤 Status: {response.status_code}")
    
    return response