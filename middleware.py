import uuid
import logging
from fastapi import Request

logger = logging.getLogger(__name__)    

async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    
    # attach request_id to request.state 
    request.state.request_id = request_id

    logger.info(
        f"Request ID: {request_id} - Incoming request: {request.method} {request.url.path}"
    )

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    logger.info(
        f"Request ID: {request_id} - Response status: {response.status_code}"
    )

    return response