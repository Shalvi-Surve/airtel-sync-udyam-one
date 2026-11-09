import pytest
from src.database.repository import save_business, save_quote, revise_quote, accept_quote, get_order, update_order
from src.services.order_service import record_kyc_outcome
from src.services.consent_service import record_registry_consent, registry_consent_granted
from src.services.order_service import accept_quote_checked
from src.data.loaders import load_catalogue
from src.engines.pricing_engine import calculate_quote

def test_quote_to_order_transitions(tmp_path, monkeypatch):
    from src.config import settings
    monkeypatch.setattr(settings,"DB_PATH",tmp_path/"test.sqlite")
    from src.database import connection
    monkeypatch.setattr(connection,"DB_PATH",tmp_path/"test.sqlite")
    profile={"business_name":"Example Shop"}; bid=save_business(profile)
    record_registry_consent(bid,True)
    assert registry_consent_granted(bid)
    record_registry_consent(bid,False)
    assert not registry_consent_granted(bid)
    with pytest.raises(ValueError): record_registry_consent(bid,"yes")
    qid=save_quote(bid,{"items":[],"monthly_total":100})
    revision=revise_quote(bid,qid,{"items":[],"monthly_total":150})
    assert revision==1
    oid=accept_quote(bid,qid)
    assert get_order(oid)["status"]=="KYC Pending"
    assert get_order(oid)["quote"]["monthly_total"]==150
    with pytest.raises(ValueError): accept_quote(bid,qid)
    with pytest.raises(ValueError): update_order(oid,"Activated","invalid shortcut")
    outcome=record_kyc_outcome(oid,False)
    assert outcome["order"]["status"]=="KYC Action Required"
    outcome=record_kyc_outcome(oid,True)
    assert outcome["order"]["status"]=="KYC Verified"
    update_order(oid,"Order Processing","demo")
    update_order(oid,"Installation Scheduled","demo")
    update_order(oid,"Installation In Progress","demo")
    update_order(oid,"Activated","demo completion; not real activation")
    assert get_order(oid)["status"]=="Activated"

def test_acceptance_revalidates_current_price_and_eligibility(tmp_path,monkeypatch):
    from src.config import settings
    from src.database import connection
    path=tmp_path/"acceptance.sqlite"; monkeypatch.setattr(settings,"DB_PATH",path); monkeypatch.setattr(connection,"DB_PATH",path)
    catalogue=load_catalogue(); profile={"business_name":"Demo Office","business_type":"Office","segment":"prof","city":"Pune","state":"Maharashtra","city_tier":1,"employees":8,"sites":1,"has_gstin":True}
    business_id=save_business(profile); quote=calculate_quote(catalogue,{"P03":1},profile); quote_id=save_quote(business_id,quote)
    changed=catalogue.copy(); changed.loc[changed.product_id=="P03","price_min_inr_per_month"]=4100
    with pytest.raises(ValueError,match="pricing or bundle quantity changed"):
        accept_quote_checked(business_id,quote_id,changed,profile)
    updated=calculate_quote(changed,{"P03":1},profile); revise_quote(business_id,quote_id,updated)
    ineligible={**profile,"city_tier":2}
    with pytest.raises(ValueError,match="Not eligible"):
        accept_quote_checked(business_id,quote_id,changed,ineligible)
