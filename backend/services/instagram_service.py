# backend/services/instagram_service.py
import instaloader
from typing import Dict, Any

class InstagramService:
    def __init__(self):
        self.loader = instaloader.Instaloader()

    async def download_content(self, url: str) -> Dict[str, Any]:
        try:
            if "/p/" in url:
                return await self.download_post(url)
            elif "/stories/" in url:
                username = url.split("/stories/")[1].split("/")[0]
                return await self.download_story(username)
            else:
                raise ValueError("Unsupported URL type")
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")

    # Add other methods from previous response