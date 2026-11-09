"""Transparent deterministic recommendations from the supplied catalogue."""
from src.engines.eligibility_engine import evaluate_product

def recommend(catalogue, profile, budget=None):
    rows = []
    for _, product in catalogue.iterrows():
        result = evaluate_product(product, profile)
        if result["status"] == "Not eligible":
            continue
        site_multiplier=max(1,int(profile.get("sites",1) or 1)) if str(product.get("unit","")).lower()=="per site" else 1
        monthly = float(product["price_min_inr_per_month"]) * site_multiplier
        status = "Over budget" if budget and monthly > float(budget) else result["status"]
        category_reason = {
            "Connectivity":"supports day-to-day business connectivity",
            "Communication":"helps the business communicate with customers or teams",
            "Cloud & Productivity":"supports digital work or business operations",
            "Security":"adds a security or managed-network capability",
            "IoT & Physical":"connects a physical business asset or location",
        }.get(product["category"],"matches the selected business profile")
        rationale=f"This {product['category'].lower()} option {category_reason}. {product['description']}"
        if profile.get("existing_services"):
            rationale += f" Current service noted: {profile['existing_services']}. Compare this option with what you already use."
        rows.append({"product": product, "eligibility": result, "status": status, "monthly_from": monthly,
                     "why": rationale})
    return rows
