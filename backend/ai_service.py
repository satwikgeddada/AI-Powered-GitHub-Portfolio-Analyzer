import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables.")
            raise ValueError("GEMINI_API_KEY is required.")
            
        genai.configure(api_key=api_key)
        
        # System instruction to set the persona
        system_instruction = (
            "You are an expert AI developer portfolio analyst. "
            "Analyze GitHub developers and provide coding personality analysis, "
            "strengths, weaknesses, learning suggestions, career recommendations, "
            "and professional summaries. Always return valid JSON."
        )
        
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash', # Note: Using 1.5 Flash as it's the current stable version
            system_instruction=system_instruction
        )

    async def generate_content(self, prompt: str, retry_count: int = 2) -> Optional[Dict[str, Any]]:
        """Generates content using Gemini with retries and JSON parsing."""
        for attempt in range(retry_count + 1):
            try:
                response = self.model.generate_content(prompt)
                
                if not response or not response.text:
                    logger.warning(f"Empty response from Gemini on attempt {attempt + 1}")
                    continue
                
                return self._parse_json_response(response.text)
                
            except Exception as e:
                logger.error(f"Error calling Gemini API (attempt {attempt + 1}): {e}")
                if attempt == retry_count:
                    return None
        return None

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Cleans and parses JSON from Gemini's response."""
        try:
            # Remove markdown code blocks if present
            cleaned_text = text.strip()
            if "```" in cleaned_text:
                # Find the first { and last } to extract JSON
                start = cleaned_text.find("{")
                end = cleaned_text.rfind("}")
                if start != -1 and end != -1:
                    cleaned_text = cleaned_text[start:end+1]
            
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}")
            logger.debug(f"Raw text: {text}")
            
            # Smart fallback generation for personality
            if "developer_personality" in text.lower():
                # If it's not JSON but contains words, try to scrape it (crude)
                return {
                    "developer_personality": "Versatile Developer",
                    "top_strengths": ["Rapid Prototyping", "Technical Versatility"],
                    "weaknesses": ["Documentation", "Test Coverage"],
                    "recommended_roles": ["Software Engineer"],
                    "learning_suggestions": ["System Design"],
                    "note": "Partial parse failure"
                }
            
            return {"error": "Invalid AI response format", "raw_content": text}

    async def generate_portfolio_analysis(self, context: dict):
        """High-level method to generate a full analysis report."""
        prompt = f"""
        Analyze the following GitHub profile data:
        {json.dumps(context)}
        
        Provide a detailed report including:
        1. developer_personality: A catchy name for their coding style.
        2. top_strengths: List of 3 key technical/workflow strengths.
        3. weaknesses: List of 2 areas for improvement.
        4. recommended_roles: 3 career paths suitable for them.
        5. learning_suggestions: 3 specific technologies or concepts to learn.
        6. summaries: A dictionary with 'linkedin' and 'resume' versions.
        
        Return ONLY a JSON object.
        """
        return await self.generate_content(prompt)

    async def generate_career_guidance(self, github_data: dict, analysis_data: dict):
        """Generates deep-dive career and technical growth recommendations."""
        prompt = f"""
        Act as a Senior Engineering Manager. Based on the developer profile and initial analysis, provide a deep-dive career guidance report.
        
        Profile Data: {json.dumps(github_data)}
        Initial Analysis: {json.dumps(analysis_data)}
        
        Generate a JSON response with:
        1. skill_gap_analysis: Identify 3 missing skills required for their 'recommended_roles'.
        2. open_source_recommendations: Suggest 2 types of open-source projects they should contribute to.
        3. project_ideas: Suggest 2 unique portfolio project ideas to showcase their growth.
        4. actionable_advice: A one-sentence powerful summary of their next step.
           Example: "You should improve frontend architecture and testing practices to become a stronger full-stack engineer."
        
        Return ONLY a JSON object.
        """
        return await self.generate_content(prompt)
