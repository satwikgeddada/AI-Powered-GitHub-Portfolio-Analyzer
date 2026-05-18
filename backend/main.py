import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agent import portfolio_analyzer_agent
from github_service import GitHubService
from mcp_server import compare_developers, scrape_github

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI GitHub Portfolio Analyzer")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directories exist
# In Docker, backend/static is at /app/static
static_path = "static/cards" if os.path.exists("static") else "backend/static/cards"
os.makedirs(static_path, exist_ok=True)

# Static files for general assets
static_dir = "static" if os.path.exists("static") else "backend/static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Request Models
class AnalyzeRequest(BaseModel):
    username: str
    theme: str = "dark"

class CompareRequest(BaseModel):
    user1: str
    user2: str

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_portfolio(request: AnalyzeRequest):
    """Orchestrates full portfolio analysis for a single user."""
    try:
        logger.info(f"Analyzing portfolio for user: {request.username} with theme: {request.theme}")
        analysis = await portfolio_analyzer_agent.analyze_user(request.username, request.theme)
        return analysis
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare")
async def compare_portfolios(request: CompareRequest):
    """Compares two developers using internal MCP tools."""
    try:
        logger.info(f"Comparing {request.user1} vs {request.user2}")
        
        # 1. Scrape both users
        user1_data = await scrape_github(request.user1)
        user2_data = await scrape_github(request.user2)
        
        # 2. Compare using tool
        comparison = await compare_developers(user1_data, user2_data)
        
        return {
            "user1": user1_data,
            "user2": user2_data,
            "comparison": comparison
        }
    except Exception as e:
        logger.error(f"Comparison failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/card/{username}")
async def serve_card(username: str):
    """Serves the generated portfolio card for a user."""
    from utils import slugify
    filename = f"{slugify(username)}-card.html"
    file_path = os.path.join("backend/static/cards", filename)
    
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Portfolio card not found. Run analysis first.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
