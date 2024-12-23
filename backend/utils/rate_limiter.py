# backend/utils/rate_limiter.py

from datetime import datetime, timedelta
from typing import Dict, List
from fastapi import HTTPException
import threading
from collections import defaultdict

class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 30,
        requests_per_hour: int = 500,
        requests_per_day: int = 5000
    ):
        self._locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)
        self._minute_requests: Dict[str, List[datetime]] = defaultdict(list)
        self._hour_requests: Dict[str, List[datetime]] = defaultdict(list)
        self._day_requests: Dict[str, List[datetime]] = defaultdict(list)
        
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day

    def _clean_old_requests(self, client_ip: str) -> None:
        """Remove expired requests from tracking."""
        now = datetime.now()
        
        # Clean minute requests
        minute_ago = now - timedelta(minutes=1)
        self._minute_requests[client_ip] = [
            req_time for req_time in self._minute_requests[client_ip]
            if req_time > minute_ago
        ]
        
        # Clean hour requests
        hour_ago = now - timedelta(hours=1)
        self._hour_requests[client_ip] = [
            req_time for req_time in self._hour_requests[client_ip]
            if req_time > hour_ago
        ]
        
        # Clean day requests
        day_ago = now - timedelta(days=1)
        self._day_requests[client_ip] = [
            req_time for req_time in self._day_requests[client_ip]
            if req_time > day_ago
        ]

    def _check_limits(self, client_ip: str) -> None:
        """Check if the request exceeds any rate limits."""
        # Check minute limit
        if len(self._minute_requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": "minute",
                    "retry_after": "60 seconds"
                }
            )
        
        # Check hour limit
        if len(self._hour_requests[client_ip]) >= self.requests_per_hour:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": "hour",
                    "retry_after": "1 hour"
                }
            )
        
        # Check day limit
        if len(self._day_requests[client_ip]) >= self.requests_per_day:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": "day",
                    "retry_after": "24 hours"
                }
            )

    def _add_request(self, client_ip: str) -> None:
        """Record a new request."""
        now = datetime.now()
        self._minute_requests[client_ip].append(now)
        self._hour_requests[client_ip].append(now)
        self._day_requests[client_ip].append(now)

    def get_remaining_limits(self, client_ip: str) -> Dict[str, int]:
        """Get remaining requests for each time window."""
        with self._locks[client_ip]:
            self._clean_old_requests(client_ip)
            return {
                "minute": self.requests_per_minute - len(self._minute_requests[client_ip]),
                "hour": self.requests_per_hour - len(self._hour_requests[client_ip]),
                "day": self.requests_per_day - len(self._day_requests[client_ip])
            }

    async def check_rate_limit(self, client_ip: str) -> None:
        """Check if a request is allowed and record it."""
        with self._locks[client_ip]:
            self._clean_old_requests(client_ip)
            self._check_limits(client_ip)
            self._add_request(client_ip)

# Usage example in your FastAPI main.py:

from fastapi import FastAPI, Request
from utils.rate_limiter import RateLimiter

app = FastAPI()
rate_limiter = RateLimiter()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    await rate_limiter.check_rate_limit(client_ip)
    
    # Add rate limit headers
    response = await call_next(request)
    limits = rate_limiter.get_remaining_limits(client_ip)
    
    response.headers["X-RateLimit-Limit-Minute"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining-Minute"] = str(limits["minute"])
    response.headers["X-RateLimit-Limit-Hour"] = str(rate_limiter.requests_per_hour)
    response.headers["X-RateLimit-Remaining-Hour"] = str(limits["hour"])
    response.headers["X-RateLimit-Limit-Day"] = str(rate_limiter.requests_per_day)
    response.headers["X-RateLimit-Remaining-Day"] = str(limits["day"])
    
    return response

# Error handler for rate limit exceptions
@app.exception_handler(HTTPException)
async def rate_limit_handler(request: Request, exc: HTTPException):
    if exc.status_code == 429:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "detail": exc.detail,
                "remaining_limits": rate_limiter.get_remaining_limits(request.client.host)
            }
        )
    raise exc