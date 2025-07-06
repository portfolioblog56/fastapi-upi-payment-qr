"""
Rate limiting middleware using in-memory cache.
"""

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from cachetools import TTLCache
from loguru import logger

from app.config import settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter middleware."""
    
    def __init__(self, app):
        super().__init__(app)
        # Use TTLCache for automatic cleanup of expired entries
        self.cache: TTLCache = TTLCache(
            maxsize=10000,  # Maximum number of IP addresses to track
            ttl=settings.RATE_LIMIT_WINDOW  # TTL in seconds
        )
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        if request.url.path.startswith("/static/"):
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if self._is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW} seconds",
                    "retry_after": settings.RATE_LIMIT_WINDOW
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self._get_remaining_requests(client_ip)
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + settings.RATE_LIMIT_WINDOW)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client IP is rate limited."""
        current_time = time.time()
        
        # Get current request count and window start time
        request_count, window_start = self.cache.get(client_ip, (0, current_time))
        
        # Check if we're in a new window
        if current_time - window_start >= settings.RATE_LIMIT_WINDOW:
            # Reset counter for new window
            request_count = 0
            window_start = current_time
        
        # Increment request count
        request_count += 1
        
        # Update cache
        self.cache[client_ip] = (request_count, window_start)
        
        # Check if rate limit exceeded
        return request_count > settings.RATE_LIMIT_REQUESTS
    
    def _get_remaining_requests(self, client_ip: str) -> int:
        """Get remaining requests for client IP."""
        request_count, _ = self.cache.get(client_ip, (0, time.time()))
        return max(0, settings.RATE_LIMIT_REQUESTS - request_count)
