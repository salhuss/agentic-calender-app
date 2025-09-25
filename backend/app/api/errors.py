"""API error handling."""
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail structure."""

    code: str
    message: str
    fields: Optional[Dict[str, Any]] = None


class APIError(Exception):
    """Base API exception."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.fields = fields
        super().__init__(message)


class ValidationError(APIError):
    """Validation error."""

    def __init__(self, message: str, fields: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            fields=fields,
        )


class NotFoundError(APIError):
    """Not found error."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=404,
        )


class ConflictError(APIError):
    """Conflict error."""

    def __init__(self, message: str) -> None:
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
        )