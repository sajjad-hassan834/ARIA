import logging
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class HealthCheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        # Suppress routine health check and status polling spam from terminal
        return not ("/health" in msg or "/api/gateway/status" in msg)


def silence_health_logs() -> None:
    """Filter out continuous polling health checks from uvicorn access logs."""
    for logger_name in ("uvicorn.access", "uvicorn", "fastapi"):
        l = logging.getLogger(logger_name)
        if not any(isinstance(f, HealthCheckFilter) for f in l.filters):
            l.addFilter(HealthCheckFilter())


# Apply on import
silence_health_logs()


def setup_cors(
    app: FastAPI,
    allow_origins: Optional[List[str]] = None,
    allow_methods: Optional[List[str]] = None,
    allow_headers: Optional[List[str]] = None,
) -> None:
    """Apply standardized CORS middleware to a FastAPI app."""
    silence_health_logs()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins or ["*"],
        allow_credentials=True,
        allow_methods=allow_methods or ["*"],
        allow_headers=allow_headers or ["*"],
    )
