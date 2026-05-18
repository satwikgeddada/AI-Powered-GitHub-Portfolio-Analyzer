from typing import List, Dict

def calculate_total_stars(repos: List[Dict]) -> int:
    """Calculates the sum of stars across all non-forked repositories."""
    return sum(repo.get("stargazers_count", 0) for repo in repos if not repo.get("fork"))

def get_language_stats(repos: List[Dict]) -> Dict:
    """Calculates language counts and percentages."""
    languages = {}
    total_repos = 0
    
    for repo in repos:
        lang = repo.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
            total_repos += 1
            
    if not total_repos:
        return {"top_languages": [], "percentages": {}}
        
    # Sort and calculate percentages
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
    percentages = {lang: round((count / total_repos) * 100, 1) for lang, count in sorted_langs}
    
    return {
        "top_languages": [lang[0] for lang in sorted_langs[:5]],
        "percentages": percentages
    }

def detect_specialization(repos: List[Dict]) -> Dict:
    """Heuristic to detect developer specialization and return scores for all categories."""
    keywords = {
        "AI/ML": ["python", "pytorch", "tensorflow", "jupyter", "nlp", "ml", "ai"],
        "Backend": ["go", "rust", "java", "node", "express", "fastapi", "django", "sql", "postgresql"],
        "Frontend": ["javascript", "typescript", "react", "vue", "angular", "css", "html", "tailwind", "sass"],
        "Mobile": ["swift", "kotlin", "flutter", "dart", "react-native"],
        "DevOps": ["docker", "kubernetes", "jenkins", "terraform", "ansible", "actions", "yaml", "shell", "bash"]
    }
    
    scores = {spec: 0 for spec in keywords}
    
    for repo in repos:
        lang = (repo.get("language") or "").lower()
        name = repo.get("name", "").lower()
        description = (repo.get("description") or "").lower()
        
        for spec, tags in keywords.items():
            if lang in tags:
                scores[spec] += 2
            if any(tag in name for tag in tags):
                scores[spec] += 1
            if any(tag in description for tag in tags):
                scores[spec] += 1
                
    max_spec = max(scores, key=scores.get)
    primary = max_spec if scores[max_spec] > 0 else "Full Stack"
    
    # Normalize scores to 0-100 for radar chart
    normalized_scores = {}
    for spec, score in scores.items():
        normalized_scores[spec] = min(100, score * 10 + 20) if score > 0 else 10
        
    return {
        "primary": primary,
        "all_scores": normalized_scores
    }

def sort_repositories(repos: List[Dict], limit: int = 5) -> List[Dict]:
    """Sorts repositories by stars and recency."""
    # Custom sort: primarily stars, secondarily by size (proxy for complexity)
    sorted_repos = sorted(
        repos, 
        key=lambda x: (x.get("stargazers_count", 0), x.get("size", 0)), 
        reverse=True
    )
    
    return [{
        "name": repo.get("name"),
        "description": repo.get("description"),
        "stars": repo.get("stargazers_count"),
        "language": repo.get("language"),
        "url": repo.get("html_url")
    } for repo in sorted_repos[:limit]]

def calculate_activity_score(user_data: Dict, repos: List[Dict]) -> int:
    """Calculates a rough activity score based on followers, repos, and stars."""
    followers = user_data.get("followers", 0)
    public_repos = user_data.get("public_repos", 0)
    stars = calculate_total_stars(repos)
    
    # Simple weighted formula
    score = (followers * 5) + (public_repos * 2) + (stars * 10)
    return score

def slugify(text: str) -> str:
    """Simple slugify for filenames."""
    return text.lower().replace(' ', '-').replace('/', '-')
