import uuid
import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)    

async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    
    # attach request_id to request.state 
    request.state.request_id = request_id

    logger.info(
        f"Request ID: {request_id} middleware = request_start "
        f"method: {request.method} path: {request.url.path}"
    )

    response = await call_next(request)

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        f"Request ID: {request_id} middleware=request_end "
        f"method: {request.method} path: {request.url.path} "
        f"status_code: {response.status_code} duration_ms: {duration_ms}"
    )

    return response