import re
import html
from typing import Optional
from fastapi import HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import secrets

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

def setup_security_middleware(app):
    """Setup all security middleware"""
    
    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://yourdomain.com"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Trusted hosts
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "yourdomain.com"]
    )

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS"""
    if not text:
        return text
    # Remove HTML tags and escape special characters
    text = re.sub(r'<[^>]*>', '', text)
    return html.escape(text.strip())

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_username(username: str) -> bool:
    """Validate username format"""
    # Alphanumeric and underscore only, 3-20 characters
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))

def generate_secure_token() -> str:
    """Generate secure random token for password reset"""
    return secrets.token_urlsafe(32)

# Rate limiting decorators
def login_rate_limit():
    return limiter.limit("5/minute")

def registration_rate_limit():
    return limiter.limit("3/minute")

def password_reset_rate_limit():
    return limiter.limit("1/minute")

def general_rate_limit():
    return limiter.limit("100/minute") 