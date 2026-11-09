"""Catalogue-backed quote calculations."""
from decimal import Decimal, ROUND_HALF_UP

def calculate_quote(catalogue, quantities, profile=None):
    profile = profile or {}
    lookup = catalogue.set_index("product_id", drop=False)
    items, monthly, setup, contract, install = [], Decimal("0"), Decimal("0"), 0, 0
    for product_id, quantity in quantities.items():
        qty = int(quantity)
        if qty <= 0 or product_id not in lookup.index:
            continue
        product = lookup.loc[product_id]
        unit_monthly = Decimal(str(product["price_min_inr_per_month"]))
        unit_setup = Decimal(str(product["one_time_setup_inr"]))
        count = qty
        if str(product["unit"]).lower() in {"per site", "per device", "per camera", "per counter", "per vehicle", "per line", "per user", "per ip", "per channel"}:
            count *= max(1, int(profile.get("sites", 1) or 1)) if str(product["unit"]).lower() == "per site" else 1
        line_monthly, line_setup = unit_monthly * count, unit_setup * qty
        monthly += line_monthly
        setup += line_setup
        contract = max(contract, int(product["min_contract_months"]))
        install = max(install, int(product["typical_install_days"]))
        items.append({"product_id": product_id, "product_name": product["product_name"], "quantity": qty, "monthly": float(line_monthly), "setup": float(line_setup), "unit": product["unit"]})
    return {"items": items, "monthly_total": float(monthly.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)), "setup_total": float(setup), "contract_months": contract, "install_days": install}
