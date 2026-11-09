"""Small SQLite repository; only structured demo data is persisted."""
import json, uuid
from src.database.connection import session, initialize

def save_business(profile):
    initialize(); key = profile.setdefault("id", str(uuid.uuid4()))
    with session() as db:
        db.execute("INSERT INTO businesses(id,profile_json) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET profile_json=excluded.profile_json", (key, json.dumps(profile)))
    return key

def save_quote(business_id, quote):
    initialize(); key = "Q-" + uuid.uuid4().hex[:8].upper()
    with session() as db:
        if not db.execute("SELECT 1 FROM businesses WHERE id=?", (business_id,)).fetchone():
            raise ValueError("Business profile must be saved before creating a quote.")
        db.execute("INSERT INTO quotes(id,business_id,quote_json) VALUES(?,?,?)", (key,business_id,json.dumps(quote)))
    return key

def revise_quote(business_id, quote_id, quote):
    """Recalculate a saved quote; keep a revision record and reject accepted quotes."""
    initialize()
    with session() as db:
        row=db.execute("SELECT status,quote_json FROM quotes WHERE id=? AND business_id=?",(quote_id,business_id)).fetchone()
        if not row: raise ValueError("Quote not found for this business.")
        if row["status"] != "Saved": raise ValueError("Accepted quotes cannot be recalculated.")
        revision=db.execute("SELECT COALESCE(MAX(revision),0)+1 FROM quote_revisions WHERE quote_id=?",(quote_id,)).fetchone()[0]
        db.execute("INSERT INTO quote_revisions(quote_id,revision,quote_json) VALUES(?,?,?)",(quote_id,revision,row["quote_json"]))
        db.execute("UPDATE quotes SET quote_json=? WHERE id=?",(json.dumps(quote),quote_id))
        return revision

def list_quotes(business_id):
    initialize()
    with session() as db: return [dict(r) for r in db.execute("SELECT * FROM quotes WHERE business_id=? ORDER BY created_at DESC", (business_id,))]

def accept_quote(business_id, quote_id):
    initialize(); order_id = "UO-" + uuid.uuid4().hex[:8].upper()
    with session() as db:
        quote = db.execute("SELECT id,status FROM quotes WHERE id=? AND business_id=?", (quote_id,business_id)).fetchone()
        if not quote: raise ValueError("Quote not found for this business.")
        if quote["status"] != "Saved": raise ValueError("This quote has already been accepted.")
        changed=db.execute("UPDATE quotes SET status='Accepted' WHERE id=? AND status='Saved'", (quote_id,))
        if changed.rowcount!=1: raise ValueError("This quote was already accepted or changed. Refresh and review it again.")
        db.execute("INSERT INTO orders(id,business_id,quote_id,status) VALUES(?,?,?,'KYC Pending')", (order_id,business_id,quote_id))
        db.execute("INSERT INTO order_events(order_id,status,note) VALUES(?,?,?)", (order_id,"KYC Pending","Quote accepted; demo order created."))
    return order_id

def update_order(order_id, status, note):
    initialize()
    allowed = {"KYC Pending": {"KYC In Progress", "Cancelled"}, "KYC In Progress": {"KYC Action Required", "KYC Verified", "Cancelled"}, "KYC Action Required": {"KYC In Progress", "Cancelled"}, "KYC Verified": {"Order Processing"}, "Order Processing": {"Installation Scheduled", "On Hold"}, "Installation Scheduled": {"Installation In Progress", "On Hold"}, "Installation In Progress": {"Activated", "On Hold"}, "On Hold": {"Order Processing", "Installation Scheduled", "Cancelled"}, "Activated": set(), "Cancelled": set()}
    with session() as db:
        row=db.execute("SELECT status FROM orders WHERE id=?",(order_id,)).fetchone()
        if not row: raise ValueError("Order not found.")
        if status not in allowed.get(row["status"], set()): raise ValueError(f"Invalid order transition: {row['status']} → {status}")
        changed=db.execute("UPDATE orders SET status=? WHERE id=? AND status=?",(status,order_id,row["status"]))
        if changed.rowcount!=1: raise ValueError("Order status changed during this update. Refresh the tracker and try again.")
        db.execute("INSERT INTO order_events(order_id,status,note) VALUES(?,?,?)",(order_id,status,note))

def get_order(order_id):
    initialize()
    with session() as db:
        row=db.execute("SELECT * FROM orders WHERE id=?",(order_id,)).fetchone()
        if not row: return None
        result=dict(row); result["events"]=[dict(e) for e in db.execute("SELECT * FROM order_events WHERE order_id=? ORDER BY id",(order_id,))]
        result["quote"]=json.loads(db.execute("SELECT quote_json FROM quotes WHERE id=?",(result["quote_id"],)).fetchone()[0])
        return result

def save_consent(business_id, purpose, granted):
    initialize()
    with session() as db: db.execute("INSERT INTO consents(business_id,purpose,granted) VALUES(?,?,?)",(business_id,purpose,int(granted)))

def get_latest_consent(business_id, purpose):
    initialize()
    with session() as db:
        row=db.execute("SELECT granted FROM consents WHERE business_id=? AND purpose=? ORDER BY id DESC LIMIT 1",(business_id,purpose)).fetchone()
        return None if not row else bool(row["granted"])

def save_kyc_result(business_id, result):
    initialize()
    with session() as db: db.execute("INSERT INTO kyc_results(business_id,result_json) VALUES(?,?)",(business_id,json.dumps(result)))
