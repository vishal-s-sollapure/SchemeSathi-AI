import hmac
import logging
import secrets
from typing import Optional
from fastapi import Header, HTTPException, status
from app.config import settings

logger = logging.getLogger("schemesathi.auth")

DEFAULT_DEV_KEY = "dev-schemesathi-admin-key-change-in-prod"


def require_admin_key(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")) -> bool:
    """
    Validates X-Admin-Key header using constant-time comparison.
    Protects administrative mutation endpoints (POST/PUT/DELETE) on schemes,
    scholarships, rules, requirements, sources, and user administration.
    
    Security policies:
    1. Returns HTTP 401 when the X-Admin-Key header is missing.
    2. Returns HTTP 403 when the provided key is invalid or malformed.
    3. In production, refuses requests if ADMIN_API_KEY is not configured or using default dev key.
    4. Performs constant-time comparison (secrets.compare_digest) to prevent timing side-channels.
    """
    configured_key = settings.ADMIN_API_KEY

    # In strict production mode, reject any invocation if key is missing or unchanged from dev default
    if settings.ENVIRONMENT == "production" or not settings.DEBUG:
        if not configured_key or configured_key == DEFAULT_DEV_KEY:
            logger.error("Administrative mutation attempted but ADMIN_API_KEY is not configured for production.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrative operations are disabled. ADMIN_API_KEY must be configured in production environment.",
            )

    # 1. Check for missing header
    if not x_admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Missing 'X-Admin-Key' header. Administrative authentication required.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # 2. Constant-time comparison
    key_matches = secrets.compare_digest(
        x_admin_key.encode("utf-8"),
        configured_key.encode("utf-8")
    )

    if not key_matches:
        logger.warning("Failed administrative authentication attempt with invalid X-Admin-Key.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid 'X-Admin-Key' credentials.",
        )

    return True
