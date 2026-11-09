"""Deterministic product eligibility and dependency checks."""
def evaluate_product(product, profile):
    reasons, missing = [], []
    tier = int(profile.get("city_tier", 1) or 1)
    tiers = [int(x) for x in str(product.get("available_city_tiers", "")).split(";") if x.strip().isdigit()]
    segment = str(profile.get("segment", "micro")).lower()
    target = [x.strip().lower() for x in str(product.get("target_segments", "")).split(";") if x.strip()]
    if tiers and tier not in tiers:
        reasons.append(f"Available city tiers: {', '.join(map(str, tiers))}; this profile is tier {tier}.")
    if int(profile.get("employees", 1) or 1) < int(product.get("min_employees", 0) or 0):
        reasons.append(f"Requires at least {int(product['min_employees'])} employees.")
    if int(profile.get("sites", 1) or 1) < int(product.get("min_sites", 0) or 0):
        reasons.append(f"Requires at least {int(product['min_sites'])} sites.")
    if target and segment not in target:
        reasons.append("This product is not listed for the selected business segment.")
    if str(product.get("requires_gstin", "N")).upper() == "Y" and not profile.get("has_gstin"):
        missing.append("GSTIN")
    selected = set(profile.get("selected_ids", []))
    dependencies = [x for x in str(product.get("requires_one_of", "")).split("|") if x]
    if dependencies and not selected.intersection(dependencies):
        missing.append("a compatible base connectivity product")
    status = "Not eligible" if reasons else ("Requires additional information" if missing else "Eligible")
    return {"status": status, "reasons": reasons, "missing": missing}
