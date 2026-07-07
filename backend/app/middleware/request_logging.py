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
        start_time = time.perf_counter()

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers[REQUEST_ID_HEADER] = request_id

        logger.info(
            "%s %s → %d  (%.1f ms)  [%s]",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        return response
