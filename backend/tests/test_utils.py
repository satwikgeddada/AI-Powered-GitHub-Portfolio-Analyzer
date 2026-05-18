import pytest
from ..utils import (
    calculate_total_stars, 
    get_language_stats, 
    detect_specialization, 
    sort_repositories, 
    calculate_activity_score
)

def test_calculate_total_stars():
    repos = [
        {"stargazers_count": 10, "fork": False},
        {"stargazers_count": 5, "fork": True},
        {"stargazers_count": 20, "fork": False}
    ]
    assert calculate_total_stars(repos) == 30

def test_get_language_stats():
    repos = [
        {"language": "Python"},
        {"language": "Python"},
        {"language": "JavaScript"},
        {"language": None}
    ]
    stats = get_language_stats(repos)
    assert stats["top_languages"] == ["Python", "JavaScript"]
    assert stats["percentages"]["Python"] == 66.7
    assert stats["percentages"]["JavaScript"] == 33.3

def test_detect_specialization():
    ai_repos = [{"language": "Python", "name": "ml-project"}]
    assert detect_specialization(ai_repos) == "AI/ML"
    
    fe_repos = [{"language": "TypeScript", "name": "react-app"}]
    assert detect_specialization(fe_repos) == "Frontend"

def test_sort_repositories():
    repos = [
        {"name": "repo1", "stargazers_count": 5},
        {"name": "repo2", "stargazers_count": 10},
        {"name": "repo3", "stargazers_count": 2}
    ]
    sorted_repos = sort_repositories(repos, limit=2)
    assert len(sorted_repos) == 2
    assert sorted_repos[0]["name"] == "repo2"
    assert sorted_repos[1]["name"] == "repo1"

def test_calculate_activity_score():
    user_data = {"followers": 10, "public_repos": 5}
    repos = [{"stargazers_count": 100, "fork": False}]
    # (10 * 5) + (5 * 2) + (100 * 10) = 50 + 10 + 1000 = 1060
    assert calculate_activity_score(user_data, repos) == 1060
