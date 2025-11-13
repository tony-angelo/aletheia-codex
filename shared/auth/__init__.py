"""Authentication utilities for Cloud Functions."""

from shared.auth.firebase_auth import (
    require_auth as require_firebase_auth,
    get_user_id_from_request as get_user_id_from_firebase,
    verify_firebase_token,
)

from shared.auth.iap_auth import (
    validate_iap_jwt,
    extract_user_from_iap_token,
    get_user_from_iap,
    IAP_HEADER,
)

from shared.auth.unified_auth import (
    require_auth,
    get_user_id_from_request,
)

__all__ = [
    # Unified authentication (recommended)
    "require_auth",
    "get_user_id_from_request",
    
    # Firebase authentication (legacy)
    "require_firebase_auth",
    "get_user_id_from_firebase",
    "verify_firebase_token",
    
    # IAP authentication
    "validate_iap_jwt",
    "extract_user_from_iap_token",
    "get_user_from_iap",
    "IAP_HEADER",
]