import time
from collections import defaultdict
from typing import Dict, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

# In-memory sliding window store for rate limiting: ip -> list of timestamps
_rate_limit_records: Dict[str, List[float]] = defaultdict(list)
_auth_rate_limit_records: Dict[str, List[float]] = defaultdict(list)

MAX_GENERAL_REQUESTS_PER_MINUTE = 300
MAX_AUTH_REQUESTS_PER_MINUTE = 30
WINDOW_SECONDS = 60.0


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Appends defensive HTTP security headers to all responses to protect against
    Clickjacking, MIME confusion, Cross-Site Scripting (XSS), and data leakage.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Content Security Policy (allows local assets plus designated trusted CDNs)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdnjs.cloudflare.com data:; "
            "img-src 'self' data: blob:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

        # Anti-Clickjacking: Disallows embedding portal in any iframe
        response.headers["X-Frame-Options"] = "DENY"

        # Anti-MIME Sniffing: Forces browsers to honor declared content-type
        response.headers["X-Content-Type-Options"] = "nosniff"

        # XSS Protection filter for legacy browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy: Suppresses leaking path and query parameters to external origins
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Restrict browser hardware APIs
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        # Cross-Origin Isolation
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        return response


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    Enforces Cross-Site Request Forgery (CSRF) protection on state-changing API methods.
    Requires custom verified headers that cross-origin HTML forms and elements cannot forge.
    """
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
    EXEMPT_PATHS = {"/api/auth/login", "/api/auth/register", "/api/auth/google/login", "/api/ai/copilot"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Only evaluate state-changing API endpoints
        if request.method not in self.SAFE_METHODS and path.startswith("/api/") and path not in self.EXEMPT_PATHS:
            auth_header = request.headers.get("authorization", "")
            csrf_token = request.headers.get("x-csrf-token", "")
            requested_with = request.headers.get("x-requested-with", "")

            # A valid state-changing request must carry either:
            # 1. Bearer JWT authorization (which browsers never send cross-origin automatically)
            # 2. X-CSRF-Token or X-Requested-With header (which triggers CORS preflight and blocks cross-origin forms)
            has_bearer = bool(auth_header.lower().startswith("bearer ") and len(auth_header) > 15)
            has_client_header = bool(
                requested_with.lower() in ["virasatsetuapp", "xmlhttprequest"]
                or len(csrf_token) > 0
            )

            if not has_bearer and not has_client_header:
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "CSRF verification failed: State-changing requests require custom client authorization headers."
                    }
                )

        return await call_next(request)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    In-memory rate limiting middleware to prevent brute force attacks on authentication
    endpoints and high-volume Denial of Service abuse on API routes.
    """
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Only rate limit API requests
        if path.startswith("/api/"):
            client_ip = request.client.host if request.client else "127.0.0.1"
            # Support reverse proxy headers like X-Forwarded-For if available
            forwarded = request.headers.get("x-forwarded-for")
            if forwarded:
                client_ip = forwarded.split(",")[0].strip()

            now = time.time()
            cutoff = now - WINDOW_SECONDS

            # Check authentication endpoints with strict threshold
            if path in ["/api/auth/login", "/api/auth/register"]:
                timestamps = _auth_rate_limit_records[client_ip]
                _auth_rate_limit_records[client_ip] = [t for t in timestamps if t > cutoff]
                if len(_auth_rate_limit_records[client_ip]) >= MAX_AUTH_REQUESTS_PER_MINUTE:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": "Rate limit exceeded: Too many authentication attempts. Please wait 60 seconds before trying again."
                        }
                    )
                _auth_rate_limit_records[client_ip].append(now)

            # Check general API endpoints
            else:
                timestamps = _rate_limit_records[client_ip]
                _rate_limit_records[client_ip] = [t for t in timestamps if t > cutoff]
                if len(_rate_limit_records[client_ip]) >= MAX_GENERAL_REQUESTS_PER_MINUTE:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": "Rate limit exceeded: Too many API requests. Please wait 60 seconds."
                        }
                    )
                _rate_limit_records[client_ip].append(now)

        return await call_next(request)
