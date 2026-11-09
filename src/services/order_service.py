from src.database.repository import accept_quote, get_order, update_order
import json
from src.engines.eligibility_engine import evaluate_product
from src.engines.pricing_engine import calculate_quote

def accept_quote_checked(business_id: str, quote_id: str, catalogue, profile: dict) -> str:
    """Recheck current eligibility and catalogue totals at the acceptance boundary."""
    from src.database.repository import list_quotes
    row=next((quote for quote in list_quotes(business_id) if quote["id"]==quote_id),None)
    if not row: raise ValueError("Quote not found for this business.")
    if row["status"]!="Saved": raise ValueError("This quote has already been accepted.")
    saved=json.loads(row["quote_json"])
    quantities={item["product_id"]:int(item["quantity"]) for item in saved.get("items",[])}
    current=calculate_quote(catalogue,quantities,profile)
    if current!=saved: raise ValueError("Catalogue pricing or bundle quantity changed. Recalculate this quote before accepting it.")
    selected_ids=list(quantities)
    for product_id in selected_ids:
        product=catalogue[catalogue.product_id==product_id]
        if product.empty: raise ValueError(f"Product {product_id} is no longer in the catalogue.")
        eligibility=evaluate_product(product.iloc[0],{**profile,"selected_ids":selected_ids})
        if eligibility["status"]!="Eligible":
            raise ValueError(f"{product.iloc[0]['product_name']} is {eligibility['status']}: " + "; ".join(eligibility["reasons"]+eligibility["missing"]))
    return accept_quote(business_id,quote_id)

def create_demo_order(business_id: str, quote_id: str) -> str:
    return accept_quote(business_id, quote_id)

def transition_demo_order(order_id: str, status: str, note: str):
    update_order(order_id, status, note)
    return get_order(order_id)

def record_kyc_outcome(order_id: str, passed: bool):
    """Move an order through KYC recovery states without swallowing errors."""
    order = get_order(order_id)
    if not order:
        raise ValueError("Order not found.")
    state=order["status"]
    if state in {"KYC Pending", "KYC Action Required"}:
        update_order(order_id,"KYC In Progress","Consent recorded; mock checks started.")
        state="KYC In Progress"
    if state != "KYC In Progress":
        return {"order":get_order(order_id),"message":f"KYC cannot change while the order is {state}."}
    final="KYC Verified" if passed else "KYC Action Required"
    note="Mock registry checks passed; demo workflow only." if passed else "Review the mock verification results and correct the inputs."
    update_order(order_id,final,note)
    return {"order":get_order(order_id),"message":note}
