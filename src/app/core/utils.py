import ipaddress
import os
import re
from urllib.parse import urlparse

from .logger import logger

def is_allowed_origin(origin: str) -> bool:
    if not origin:
        return False
    
    cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    allowed_origins = [os.strip() for os in cors_origins.split(",") if os.strip()]

    if origin in allowed_origins or "*" in allowed_origins:
        return True
    
    cors_origins_regex = os.environ.get("CORS_ALLOWED_ORIGINS_REGEX")
    if cors_origins_regex:
        try:
            if re.fullmatch(cors_origins_regex, origin):
                return True
        except Exception as e:
            logger.error(f"Invalid CORS regex: {cors_origins_regex}, error: {e}")
    
    return False

def _is_loopback_host(hostname: str | None) -> bool:
    if not hostname:
        return False
    if hostname == "localhost":
        return True
    
    try:
        return ipaddress.ip_address(hostname.strip("[]")).is_loopback
    except ValueError:
        logger.error("ValueError")
        return False

def is_allowed_redirect_uri(uri: str) -> bool:
    if not uri:
        return False
    
    try:
        parsed = urlparse(uri)
        origin = f"{parsed.scheme}://{parsed.netloc}"

        if _is_loopback_host(parsed.hostname):
            return True
        
        return is_allowed_origin(origin)
    except Exception:
        logger.error("Exception")
        return False
