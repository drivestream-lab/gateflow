"""GitHub webhook HMAC signature verification."""

import hashlib
import hmac


def verify_github_webhook_signature(secret: str, body: bytes, signature_header: str) -> bool:
    """Return True when X-Hub-Signature-256 matches HMAC-SHA256 of the raw body."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    expected = f"sha256={digest}"
    return hmac.compare_digest(expected, signature_header)
