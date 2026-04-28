from typing import List, Dict
import re

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep common ones
    text = re.sub(r'[^\w\s\-\+\#\.]', '', text)
    return text.strip()

def calculate_similarity(skills1: List[str], skills2: List[str]) -> float:
    """Calculate Jaccard similarity between two skill sets"""
    set1 = set([s.lower() for s in skills1])
    set2 = set([s.lower() for s in skills2])
    
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return round(intersection / union, 2) if union > 0 else 0.0

def format_duration(weeks: int) -> str:
    """Format duration in human-readable format"""
    if weeks < 4:
        return f"{weeks} week{'s' if weeks != 1 else ''}"
    elif weeks < 52:
        months = round(weeks / 4.33, 1)
        return f"{months} month{'s' if months != 1 else ''}"
    else:
        years = round(weeks / 52, 1)
        return f"{years} year{'s' if years != 1 else ''}"

def prioritize_by_impact(skills: List[Dict], top_n: int = 5) -> List[Dict]:
    """Get top N skills by priority score"""
    sorted_skills = sorted(skills, key=lambda x: x.get('priority_score', 0), reverse=True)
    return sorted_skills[:top_n]

def group_by_category(skills: List[str], skill_graph: Dict) -> Dict[str, List[str]]:
    """Group skills by their category"""
    categories = {}
    
    for skill in skills:
        skill_info = skill_graph.get(skill, {})
        category = skill_info.get('category', 'general')
        
        if category not in categories:
            categories[category] = []
        categories[category].append(skill)
    
    return categories

def estimate_completion_date(weeks: int) -> str:
    """Estimate completion date based on current date"""
    from datetime import datetime, timedelta
    
    completion_date = datetime.now() + timedelta(weeks=weeks)
    return completion_date.strftime("%B %Y")

def generate_progress_tracker(weekly_plan: List[Dict]) -> Dict:
    """Generate a progress tracking structure"""
    return {
        "total_weeks": len(weekly_plan),
        "completed_weeks": 0,
        "current_week": 1,
        "completion_percentage": 0,
        "skills_learned": [],
        "skills_in_progress": [],
        "skills_remaining": [],
        "estimated_completion": estimate_completion_date(len(weekly_plan))
    }