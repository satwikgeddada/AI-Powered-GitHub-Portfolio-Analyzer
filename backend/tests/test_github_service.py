import pytest
import httpx
from ..github_service import GitHubService

@pytest.mark.asyncio
async def test_get_full_profile_success(respx_mock):
    service = GitHubService()
    username = "testuser"
    
    # Mock Profile API
    respx_mock.get(f"https://api.github.com/users/{username}").mock(return_value=httpx.Response(200, json={
        "login": "testuser",
        "name": "Test User",
        "avatar_url": "http://avatar.com",
        "bio": "Test bio",
        "followers": 10,
        "following": 5,
        "public_repos": 2
    }))
    
    # Mock Repos API
    respx_mock.get(f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated").mock(return_value=httpx.Response(200, json=[
        {"name": "repo1", "stargazers_count": 5, "language": "Python", "fork": False, "html_url": "http://repo1.com"},
        {"name": "repo2", "stargazers_count": 10, "language": "JavaScript", "fork": False, "html_url": "http://repo2.com"}
    ]))
    
    profile = await service.get_full_profile(username)
    
    assert profile["username"] == "testuser"
    assert profile["total_stars"] == 15
    assert "Python" in profile["languages"]
    assert len(profile["top_repositories"]) == 2

@pytest.mark.asyncio
async def test_get_full_profile_not_found(respx_mock):
    service = GitHubService()
    username = "nonexistent"
    
    respx_mock.get(f"https://api.github.com/users/{username}").mock(return_value=httpx.Response(404))
    
    with pytest.raises(Exception) as excinfo:
        await service.get_full_profile(username)
    assert "404" in str(excinfo.value)
