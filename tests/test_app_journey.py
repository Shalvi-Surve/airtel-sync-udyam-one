"""UI-level synthetic customer journey through Streamlit AppTest."""
import json
from src.database import connection
from src.database.repository import list_quotes, get_order
from streamlit.testing.v1 import AppTest

def test_synthetic_customer_journey_with_quote_revision_and_kyc_recovery(tmp_path, monkeypatch):
    db_path=tmp_path/"journey.sqlite"
    monkeypatch.setattr(connection,"DB_PATH",db_path)
    app=AppTest.from_file("app.py").run(timeout=30)
    next(b for b in app.button if b.label=="Load synthetic clinic demo").click(); app.run(timeout=30)
    assert app.session_state["profile"]["business_name"]=="Balaji Dental Care LLP"
    assert app.session_state["bundle"]=={"P01":1,"P12":1,"P16":4}

    app.radio[0].set_value("Bundle Builder"); app.run(timeout=30)
    next(b for b in app.button if b.label=="Review and save quote").click(); app.run(timeout=30)
    quote_id=app.session_state["active_quote"]

    # Change the bundle after saving and confirm a quote revision uses current rates/quantities.
    next(n for n in app.number_input if n.key=="qty_P16").set_value(5); app.run(timeout=30)
    app.radio[0].set_value("Quotes & Orders"); app.run(timeout=30)
    next(b for b in app.button if b.label.startswith("Recalculate ")).click(); app.run(timeout=30)
    quote=next(q for q in list_quotes(app.session_state["profile"]["id"]) if q["id"]==quote_id)
    assert json.loads(quote["quote_json"])["monthly_total"]==2624
    next(b for b in app.button if b.label.startswith("Accept ")).click(); app.run(timeout=30)
    order_id=app.session_state["active_order"]

    app.radio[0].set_value("Smart KYC"); app.run(timeout=30)
    app.checkbox[0].check(); next(b for b in app.button if b.label=="Record consent").click(); app.run(timeout=30)
    app.text_input[0].set_value("bad"); app.text_input[1].set_value("")
    next(b for b in app.button if b.label=="Run demo checks").click(); app.run(timeout=30)
    assert get_order(order_id)["status"]=="KYC Action Required"
    assert any(result["status"]=="Failed" for result in app.session_state["kyc_results"])

    app.text_input[0].set_value("32TTNXB7384T1ZW"); app.text_input[1].set_value("UDYAM-KL-00-3078801")
    next(b for b in app.button if b.label=="Run demo checks").click(); app.run(timeout=30)
    assert get_order(order_id)["status"]=="KYC Verified"

    app.radio[0].set_value("Order Tracker"); app.run(timeout=30)
    next(b for b in app.button if b.label=="Track order").click(); app.run(timeout=30)
    for label,expected in [
        ("Move demo order to processing","Order Processing"),
        ("Schedule demo installation","Installation Scheduled"),
        ("Start demo installation","Installation In Progress"),
        ("Mark demo journey complete","Activated"),
    ]:
        next(b for b in app.button if b.label==label).click(); app.run(timeout=30)
        assert get_order(order_id)["status"]==expected
        assert not app.exception

def test_operations_dashboard_shows_privacy_aware_empty_state_without_dataset(monkeypatch):
    import src.data.loaders as loaders
    import pandas as pd
    monkeypatch.setattr(loaders, "load_analytics", lambda: pd.DataFrame())
    view=AppTest.from_file("app.py").run(timeout=30)
    view.radio[0].set_value("Operations Dashboard"); view.run(timeout=30)
    assert not view.exception
    assert any("synthetic demo analytics file is missing" in item.value for item in view.info)
