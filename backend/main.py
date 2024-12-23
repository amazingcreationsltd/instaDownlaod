# backend/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.rate_limiter import RateLimiter
from services.instagram_service import InstagramService

app = FastAPI()
rate_limiter = RateLimiter(
    requests_per_minute=30,  # Adjust these limits as needed
    requests_per_hour=500,
    requests_per_day=5000
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/limits")
async def get_limits(request: Request):
    """Get current rate limit status"""
    return rate_limiter.get_remaining_limits(request.client.host)

@app.post("/api/download")
async def download_content(request: Request, url: str):
    """Download Instagram content with rate limiting"""
    try:
        # Rate limiting is handled by middleware
        result = await instagram_service.download_content(url)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))