import os
import json
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

class PortfolioAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        self.system_instruction = (
            "You are an AI GitHub Portfolio Analyzer Agent. Whenever a user provides a GitHub username, "
            "always follow this sequence: scrape_github, analyze_coding_personality, "
            "generate_portfolio_summary, calculate_developer_score, generate_portfolio_card, save_portfolio_card. "
            "Never skip steps. Always provide professional and encouraging developer insights."
        )
        
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=self.system_instruction
        )
        
        from ai_service import AIService
        self.ai = AIService()
        
        # MCP Connection details
        # Detect environment to set correct path for mcp_server.py
        mcp_path = "mcp_server.py" if os.path.exists("mcp_server.py") else "backend/mcp_server.py"
        
        self.server_params = StdioServerParameters(
            command="python",
            args=[mcp_path],
            env=os.environ.copy()
        )

    async def analyze_user(self, username: str, theme: str = "dark"):
        """Orchestrates the portfolio analysis using MCP tools and Gemini."""
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # 1. Scrape GitHub
                    print(f"Scraping GitHub for {username}...")
                    github_data = await session.call_tool("scrape_github", {"username": username})
                    github_data_json = json.loads(github_data.content[0].text)
                    
                    # 2. Analyze Coding Personality
                    print("Analyzing personality...")
                    try:
                        personality = await session.call_tool("analyze_coding_personality", {"github_data": github_data_json})
                        personality_json = json.loads(personality.content[0].text)
                    except Exception as e:
                        print(f"Personality analysis tool failed: {e}")
                        raise
                    
                    # 3. Generate Portfolio Summary
                    print("Generating summary...")
                    try:
                        summary = await session.call_tool("generate_portfolio_summary", {
                            "github_data": github_data_json, 
                            "analysis": personality_json
                        })
                        summary_json = json.loads(summary.content[0].text)
                    except Exception as e:
                        print(f"Summary generation tool failed: {e}")
                        raise
                    
                    # 4. Calculate Developer Score
                    print("Calculating developer score...")
                    score = await session.call_tool("calculate_developer_score", {"github_data": github_data_json})
                    score_json = json.loads(score.content[0].text)

                    # 4.5 Generate Career Guidance
                    print("Generating career guidance...")
                    guidance = await self.ai.generate_career_guidance(github_data_json, personality_json)
                    
                    # 5. Generate Portfolio Card
                    print(f"Generating portfolio card with theme: {theme}...")
                    card_html = await session.call_tool("generate_portfolio_card", {
                        "username": username,
                        "github_data": github_data_json,
                        "analysis": personality_json,
                        "theme": theme
                    })
                    card_html_text = card_html.content[0].text
                    
                    # 6. Save Portfolio Card
                    print("Saving portfolio card...")
                    card_url = await session.call_tool("save_portfolio_card", {
                        "username": username,
                        "html": card_html_text
                    })
                    card_url_text = card_url.content[0].text

                    # Construct final response
                    return {
                        "username": username,
                        "profile": github_data_json,
                        "personality": personality_json,
                        "summary": summary_json,
                        "score": score_json,
                        "guidance": guidance,
                        "card_url": card_url_text
                    }
        except Exception as e:
            print(f"PortfolioAgent.analyze_user failed: {str(e)}")
            raise e

# Export the agent instance
portfolio_analyzer_agent = PortfolioAgent()
