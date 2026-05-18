import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from ..main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("backend.main.portfolio_analyzer_agent.analyze_user", new_callable=AsyncMock)
def test_analyze_portfolio(mock_analyze):
    mock_analyze.return_value = {"username": "testuser", "score": {"score": 90}}
    
    response = client.post("/analyze", json={"username": "testuser"})
    
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    mock_analyze.assert_called_once_with("testuser")

@patch("backend.main.scrape_github", new_callable=AsyncMock)
@patch("backend.main.compare_developers", new_callable=AsyncMock)
def test_compare_portfolios(mock_compare, mock_scrape):
    mock_scrape.return_value = {"username": "user1"}
    mock_compare.return_value = {"winner": "user1"}
    
    response = client.post("/compare", json={"user1": "user1", "user2": "user2"})
    
    assert response.status_code == 200
    assert response.json()["comparison"]["winner"] == "user1"
