import pytest
from unittest.mock import MagicMock, patch
from ..ai_service import AIService

@pytest.fixture
def ai_service():
    with patch('google.generativeai.configure'):
        with patch('google.generativeai.GenerativeModel'):
            return AIService()

@pytest.mark.asyncio
async def test_generate_portfolio_analysis(ai_service):
    mock_model = ai_service.model
    mock_response = MagicMock()
    mock_response.text = '{"developer_personality": "Wizard", "top_strengths": ["Fast"], "weaknesses": ["None"], "recommended_roles": ["Lead"], "learning_suggestions": ["More AI"], "summaries": {"linkedin": "...", "resume": "..."}}'
    mock_model.generate_content.return_value = mock_response
    
    result = await ai_service.generate_portfolio_analysis({"some": "data"})
    
    assert result["developer_personality"] == "Wizard"
    assert "top_strengths" in result
    mock_model.generate_content.assert_called_once()

def test_parse_json_response(ai_service):
    text = "```json\n{\"key\": \"value\"}\n```"
    parsed = ai_service._parse_json_response(text)
    assert parsed["key"] == "value"
    
    text_no_md = "{\"key\": \"value\"}"
    parsed_no_md = ai_service._parse_json_response(text_no_md)
    assert parsed_no_md["key"] == "value"
