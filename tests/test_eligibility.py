from src.data.loaders import load_catalogue
from src.engines.eligibility_engine import evaluate_product
from src.engines.recommendation_engine import recommend
from src.utils.validators import validate_business_profile

def test_gstin_required_product_needs_profile_gstin():
    df=load_catalogue(); product=df[df.product_id=="P03"].iloc[0]
    result=evaluate_product(product,{"city_tier":1,"employees":5,"sites":1,"segment":"prof","has_gstin":False,"selected_ids":[]})
    assert result["status"] == "Requires additional information"
    assert "GSTIN" in result["missing"]

def test_dependency_is_reported():
    df=load_catalogue(); product=df[df.product_id=="P09"].iloc[0]
    result=evaluate_product(product,{"city_tier":1,"employees":2,"sites":1,"segment":"prof","has_gstin":False,"selected_ids":[]})
    assert any("compatible base connectivity product" in item for item in result["missing"])
    fulfilled=evaluate_product(product,{"city_tier":1,"employees":2,"sites":1,"segment":"prof","has_gstin":False,"selected_ids":["P01"]})
    assert "compatible base connectivity product" not in fulfilled["missing"]

def test_city_tier_segment_and_employee_restrictions_are_honored():
    product=load_catalogue().query("product_id == 'P03'").iloc[0]
    result=evaluate_product(product,{"city_tier":2,"employees":2,"sites":1,"segment":"micro","has_gstin":True,"selected_ids":[]})
    assert result["status"]=="Not eligible"
    assert any("city tiers" in r for r in result["reasons"])
    assert any("employees" in r for r in result["reasons"])

def test_recommendations_are_catalogue_backed():
    df=load_catalogue(); result=recommend(df,{"city_tier":1,"employees":2,"sites":1,"segment":"micro","has_gstin":False,"selected_ids":[]})
    assert result
    assert all(item["product"]["product_id"] in set(df.product_id) for item in result)

def test_profile_requirements_reject_missing_location_and_type():
    valid,missing=validate_business_profile({"business_name":"Demo","employees":1,"sites":1,"city_tier":1})
    assert not valid
    assert "business type" in missing and "city" in missing and "state" in missing

def test_profile_requirements_treat_none_and_whitespace_as_missing():
    valid,missing=validate_business_profile({"business_name":None,"business_type":" ","city":None,"state":"Kerala","employees":1,"sites":1,"city_tier":1})
    assert not valid
    assert "business name" in missing and "business type" in missing and "city" in missing
