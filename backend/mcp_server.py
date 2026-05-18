import os
import json
import google.generativeai as genai
from fastmcp import FastMCP
from github_service import GitHubService
from ai_service import AIService
from utils import calculate_activity_score, slugify
from fastapi import HTTPException

# Initialize MCP
mcp = FastMCP("PortfolioAnalyzer")

# Initialize Services for internal tool usage
github_svc = GitHubService()
ai_svc = AIService()

@mcp.tool()
async def scrape_github(username: str) -> dict:
    """Fetches and aggregates comprehensive GitHub profile data for a user."""
    return await github_svc.get_full_profile(username)

@mcp.tool()
async def analyze_coding_personality(github_data: dict) -> dict:
    """Uses Gemini to analyze coding personality and career traits."""
    prompt = f"""
    Act as a Senior Technical Lead. Analyze this GitHub profile data:
    {json.dumps(github_data)}
    
    CRITICAL: Provide HYPER-SPECIFIC insights. Do not use generic phrases like 'Project Delivery' or 'Rapid Learning'.
    
    Return a JSON object with exactly these keys:
    'developer_personality': A unique, technical-focused persona (e.g., 'Async Go Specialist', 'TypeScript UI Architect').
    'top_strengths': 3 specific technical strengths derived from their repos (e.g., 'Expertise in {github_data['languages'][0] if github_data['languages'] else 'System Design'}', 'Consistent {github_data['languages'][1] if len(github_data['languages']) > 1 else 'backend'} implementation', 'Complex state management').
    'weaknesses': 2 specific areas to improve (e.g., 'Lack of {github_data['languages'][-1] if github_data['languages'] else 'testing'} documentation', 'Low repository diversity').
    'recommended_roles': 3 precise roles.
    'learning_suggestions': 3 advanced technologies.
    """
    analysis = await ai_svc.generate_content(prompt)
    if not analysis or "error" in analysis:
        # Emergency robust fallback with some data injection
        primary_lang = github_data['languages'][0] if github_data['languages'] else "Software"
        return {
            "developer_personality": f"{primary_lang} Explorer",
            "top_strengths": [f"Focus on {primary_lang}", "Active Repository Management", f"Project Building in {primary_lang}"],
            "weaknesses": ["README Documentation", "Automated Testing"],
            "recommended_roles": [f"{primary_lang} Developer"],
            "learning_suggestions": ["CI/CD Pipelines"],
            "status": "partial_success"
        }
    return analysis

@mcp.tool()
async def generate_portfolio_summary(github_data: dict, analysis: dict) -> dict:
    """Generates professional summaries for LinkedIn and Resumes."""
    prompt = f"""
    Create two unique professional summaries for this developer:
    Developer: {github_data['name']} (@{github_data['username']})
    Personality: {analysis['developer_personality']}
    Primary Skills: {', '.join(github_data['languages'])}
    Stats: {github_data['total_stars']} stars, {github_data['public_repos']} repos.
    
    1. LinkedIn-style summary (3-4 impactful sentences, first person).
    2. A short resume introduction (1-2 sentences, professional).
    
    Return JSON: {{"linkedin_summary": "...", "resume_intro": "..."}}
    """
    summary = await ai_svc.generate_content(prompt)
    if not summary or "error" in summary:
        return {
            "linkedin_summary": f"I am a passionate developer skilled in {', '.join(github_data['languages'])}. I have built {github_data['public_repos']} projects and earned {github_data['total_stars']} stars on GitHub.",
            "resume_intro": f"Professional Software Engineer with expertise in {', '.join(github_data['languages'][:2])}."
        }
    return summary

@mcp.tool()
async def calculate_developer_score(github_data: dict) -> dict:
    """Generates a developer score from 1-100 and categorizes their level."""
    score = github_data.get("activity_score", 0)
    
    # Normalize score to 1-100 range (rough heuristic)
    normalized = min(100, max(1, int(score / 50))) 
    
    levels = [
        (90, "Elite Architect"),
        (75, "Advanced Developer"),
        (50, "Proficient Engineer"),
        (25, "Rising Star"),
        (0, "Aspiring Developer")
    ]
    
    level = "Unknown"
    for threshold, name in levels:
        if normalized >= threshold:
            level = name
            break
            
    return {"score": normalized, "level": level}

@mcp.tool()
async def compare_developers(user1_data: dict, user2_data: dict) -> dict:
    """Compares two developers and generates a benchmark report."""
    metrics = ["total_stars", "followers", "public_repos", "activity_score"]
    comparison = {}
    
    for metric in metrics:
        v1 = user1_data.get(metric, 0)
        v2 = user2_data.get(metric, 0)
        comparison[metric] = {
            user1_data["username"]: v1,
            user2_data["username"]: v2,
            "winner": user1_data["username"] if v1 > v2 else user2_data["username"]
        }
        
    return comparison

@mcp.tool()
async def generate_portfolio_card(username: str, github_data: dict, analysis: dict, theme: str = "dark") -> str:
    """Generates a beautiful Glassmorphism HTML portfolio card."""
    
    themes = {
        "glassmorphism": "linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05))",
        "hacker": "linear-gradient(135deg, rgba(0,255,65,0.1), rgba(0,0,0,0.9))",
        "neon-cyberpunk": "linear-gradient(135deg, rgba(255,0,255,0.1), rgba(0,255,255,0.1))",
        "github-dark-pro": "linear-gradient(135deg, #0d1117, #161b22)",
        "AI-futuristic": "linear-gradient(135deg, #0f172a, #1e293b)",
        "dark": "linear-gradient(135deg, #0f172a, #1e293b)",
        "light": "linear-gradient(135deg, #ffffff, #f1f5f9)"
    }
    
    # Map 'glassmorphism' to dark by default if not specified, or use request theme
    selected_theme = theme if theme in themes else "dark"
    bg = themes[selected_theme]
    
    # Determine text color based on theme
    is_light = selected_theme == "light"
    text_color = "#0f172a" if is_light else "white"
    muted_text = "rgba(15, 23, 42, 0.6)" if is_light else "rgba(255, 255, 255, 0.6)"
    box_bg = "rgba(0, 0, 0, 0.05)" if is_light else "rgba(255, 255, 255, 0.05)"
    border_color = "rgba(0, 0, 0, 0.1)" if is_light else "rgba(255, 255, 255, 0.1)"
    
    # Normalize score for consistency with website
    raw_score = github_data.get("activity_score", 0)
    normalized_score = min(100, max(1, int(raw_score / 50)))
    
    # Use specialization from github_data for consistency
    specialization = github_data.get("specialization", "Full Stack")
    
    html = f"""
    <div class="portfolio-card" style="background: {bg}; backdrop-filter: blur(15px); border: 1px solid {border_color}; border-radius: 24px; padding: 40px; color: {text_color}; font-family: 'Inter', sans-serif; max-width: 500px; box-shadow: 0 20px 50px rgba(0,0,0,0.2);">
        <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 30px;">
            <img src="{github_data['avatar']}" style="width: 80px; height: 80px; border-radius: 50%; border: 3px solid #38bdf8;">
            <div>
                <h2 style="margin: 0; font-size: 24px; color: {text_color};">{github_data['name']}</h2>
                <p style="margin: 5px 0 0; color: #38bdf8; font-weight: 600;">@{username}</p>
            </div>
        </div>
        
        <div style="background: {box_bg}; padding: 15px; border-radius: 12px; margin-bottom: 20px;">
            <p style="margin: 0; font-style: italic; opacity: 0.9; color: {text_color};">"{analysis['developer_personality']}"</p>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px;">
            <div style="text-align: center; background: {box_bg}; padding: 10px; border-radius: 12px;">
                <span style="display: block; font-size: 12px; opacity: 0.6; color: {text_color};">Dev Score</span>
                <strong style="font-size: 20px; color: #38bdf8;">{normalized_score}</strong>
            </div>
            <div style="text-align: center; background: {box_bg}; padding: 10px; border-radius: 12px;">
                <span style="display: block; font-size: 12px; opacity: 0.6; color: {text_color};">Specialization</span>
                <strong style="font-size: 16px; color: {text_color};">{specialization}</strong>
            </div>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h3 style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; opacity: 0.7; color: {text_color};">Top Skills</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                {' '.join([f'<span style="background: #38bdf822; color: #38bdf8; padding: 4px 10px; border-radius: 20px; font-size: 12px; border: 1px solid #38bdf844;">{lang}</span>' for lang in github_data['languages']])}
            </div>
        </div>
        
        <div style="border-top: 1px solid {border_color}; padding-top: 20px; display: flex; justify-content: space-between; font-size: 14px; color: {text_color};">
            <span><strong>{github_data['total_stars']}</strong> Stars</span>
            <span><strong>{github_data['followers']}</strong> Followers</span>
            <span><strong>{github_data['public_repos']}</strong> Repos</span>
        </div>
    </div>
    """
    return html

@mcp.tool()
async def save_portfolio_card(username: str, html: str) -> str:
    """Saves the generated HTML card to the static directory and returns the URL."""
    filename = f"{slugify(username)}-card.html"
    # Detect static path for local vs Docker
    static_base = "static" if os.path.exists("static") else "backend/static"
    cards_dir = os.path.join(static_base, "cards")
    
    os.makedirs(cards_dir, exist_ok=True)
    
    file_path = os.path.join(cards_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    return f"/static/cards/{filename}"

if __name__ == "__main__":
    mcp.run()
