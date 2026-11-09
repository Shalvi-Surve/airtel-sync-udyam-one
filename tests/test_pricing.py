from src.data.loaders import load_catalogue
from src.engines.pricing_engine import calculate_quote

def test_quote_uses_catalogue_minimum_and_setup():
    catalogue=load_catalogue()
    quote=calculate_quote(catalogue,{"P01":1,"P19":2},{"sites":1})
    assert quote["monthly_total"] == 999 + 2*599
    assert quote["setup_total"] == 2*2500
    assert quote["contract_months"] == 12

def test_unknown_and_zero_quantity_items_are_ignored():
    quote=calculate_quote(load_catalogue(),{"UNKNOWN":2,"P01":0})
    assert quote["items"] == []
    assert quote["monthly_total"] == 0

def test_per_site_price_scales_with_sites_but_setup_rule_is_quantity_based():
    quote=calculate_quote(load_catalogue(),{"P01":2},{"sites":3})
    assert quote["monthly_total"]==999*6
    assert quote["setup_total"]==0

def test_recalculation_tracks_catalogue_price_changes():
    catalogue=load_catalogue(); before=calculate_quote(catalogue,{"P01":1})
    catalogue.loc[catalogue.product_id=="P01","price_min_inr_per_month"]=1100
    after=calculate_quote(catalogue,{"P01":1})
    assert after["monthly_total"]-before["monthly_total"]==101
