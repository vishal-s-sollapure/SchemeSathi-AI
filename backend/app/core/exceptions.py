from typing import Any, Optional


class SchemeSathiException(Exception):
    """Base exception for SchemeSathi AI backend."""
    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.detail = detail


class EntityNotFoundException(SchemeSathiException):
    """Raised when a requested resource is not found."""
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found.",
            detail={"entity": entity_name, "identifier": identifier},
        )


class EntityConflictException(SchemeSathiException):
    """Raised when an entity conflict exists (e.g. duplicate key)."""
    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(message=message, detail=detail)


class ValidationException(SchemeSathiException):
    """Raised when business validation fails."""
    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(message=message, detail=detail)
