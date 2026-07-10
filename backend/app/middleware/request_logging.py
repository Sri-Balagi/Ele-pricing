"""
Request logging middleware.

Adds to every HTTP response:
  - X-Request-ID header: a unique UUID for distributed tracing.

Logs for every request:
  - HTTP method, path, response status code, and duration in milliseconds.

This middleware sits at the outermost layer so it captures accurate timing
including all inner middleware and route processing time.
"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.constants import REQUEST_ID_HEADER

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs every request and attaches a trace ID to the response.

    Log format:
        METHOD /path/to/route → STATUS_CODE  (XX.X ms)  [request-uuid]

    The X-Request-ID header on the response allows clients and log aggregators
    to correlate requests across services.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        # Attach a unified correlation ID to the request state
        request.state.correlation_id = request.headers.get("X-Correlation-ID", f"PIPE-{request_id}")
        
        start_time = time.perf_counter()
        
        # We can't safely get request size without consuming the body, which might break endpoints.
        # We'll just read content-length header if provided.
        req_size = request.headers.get("content-length", "0")
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Operational Enhancements (M5 Hardening)
        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers["X-Correlation-ID"] = request.state.correlation_id
        response.headers["X-API-Version"] = "v1"
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}"
        
        resp_size = response.headers.get("content-length", "0")

        logger.info(
            "%s %s -> %d (%.1f ms) [ReqId: %s] [CorrId: %s] [IP: %s] [UA: %s] [ReqSize: %s] [RespSize: %s]",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
            request.state.correlation_id,
            client_ip,
            user_agent,
            req_size,
            resp_size
        )

        return response
