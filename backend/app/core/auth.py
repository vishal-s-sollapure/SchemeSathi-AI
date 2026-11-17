from typing import Optional
from fastapi import Header, HTTPException, status
from app.config import settings


def require_admin_key(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")) -> bool:
    """
    Validates X-Admin-Key header against configured ADMIN_API_KEY.
    Protects administrative mutation endpoints (POST/PUT/DELETE) on schemes,
    scholarships, rules, sources, and sensitive user administration.
    """
    configured_key = settings.ADMIN_API_KEY
    if not configured_key:
        return True

    if not x_admin_key or x_admin_key != configured_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Missing or invalid 'X-Admin-Key' header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return True
