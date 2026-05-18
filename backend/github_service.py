import httpx
import os
import logging
from dotenv import load_dotenv
from fastapi import HTTPException
from utils import (
    calculate_total_stars, 
    get_language_stats, 
    detect_specialization, 
    sort_repositories, 
    calculate_activity_score
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-GitHub-Portfolio-Analyzer"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    async def _make_request(self, client: httpx.AsyncClient, endpoint: str):
        try:
            response = await client.get(f"{self.base_url}/{endpoint}", headers=self.headers)
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"GitHub user not found: {endpoint}")
            elif response.status_code == 403:
                # Check for rate limit
                if "X-RateLimit-Remaining" in response.headers and response.headers["X-RateLimit-Remaining"] == "0":
                    raise HTTPException(status_code=429, detail="GitHub API rate limit exceeded. Please try again later.")
                raise HTTPException(status_code=403, detail="GitHub API access forbidden.")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise HTTPException(status_code=500, detail="Error connecting to GitHub API")

    async def get_full_profile(self, username: str):
        async with httpx.AsyncClient() as client:
            # 1. Fetch Profile Info
            user_data = await self._make_request(client, f"users/{username}")
            
            # 2. Fetch Repositories
            repos = await self._make_request(client, f"users/{username}/repos?per_page=100&sort=updated")
            
            # 3. Use Utils for Advanced Processing
            total_stars = calculate_total_stars(repos)
            lang_stats = get_language_stats(repos)
            spec_data = detect_specialization(repos)
            top_repos = sort_repositories(repos)
            activity_score = calculate_activity_score(user_data, repos)

            # 4. Construct Structured Response
            return {
                "username": user_data.get("login"),
                "name": user_data.get("name") or user_data.get("login"),
                "avatar": user_data.get("avatar_url"),
                "bio": user_data.get("bio") or "No bio available",
                "location": user_data.get("location"),
                "company": user_data.get("company"),
                "followers": user_data.get("followers", 0),
                "following": user_data.get("following", 0),
                "public_repos": user_data.get("public_repos", 0),
                "languages": lang_stats["top_languages"],
                "language_percentages": lang_stats["percentages"],
                "specialization": spec_data["primary"],
                "specialization_scores": spec_data["all_scores"],
                "top_repositories": top_repos,
                "total_stars": total_stars,
                "activity_score": activity_score
            }
