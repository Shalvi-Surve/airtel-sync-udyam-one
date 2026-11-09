"""Deterministic advisor orchestration; recommendations remain engine-owned."""
from src.engines.recommendation_engine import recommend

def get_recommendations(catalogue, profile, goal_categories=None):
    items = recommend(catalogue, profile, profile.get("budget"))
    if goal_categories:
        items = [item for item in items if item["product"]["category"] in goal_categories]
    return items

def fallback_message(profile):
    name = profile.get("business_name") or "your business"
    return f"I can help {name} explore catalogue-backed options. Share your business type, location, team size, and goal to get started."
