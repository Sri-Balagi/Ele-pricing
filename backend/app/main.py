"""
Application entry point.

Run the development server from the backend/ directory:
    uvicorn app.main:app --reload

Run directly (alternative):
    python -m app.main

The 'app' object is imported by uvicorn. create_app() is called at module
import time so the ASGI app is ready before uvicorn begins accepting requests.
"""

import uvicorn

from app import create_app

# Create the ASGI application instance.
# Uvicorn references this as 'app.main:app'.
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
