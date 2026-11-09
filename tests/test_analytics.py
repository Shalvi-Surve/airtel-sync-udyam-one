from src.data.loaders import load_analytics

def test_synthetic_demo_metrics_are_present_and_labelled():
    data=load_analytics(); activated=data[data.outcome=="Activated"]
    assert len(data)==5000
    assert len(activated)==368
    assert round(len(activated)/len(data)*100,2)==7.36
    assert round(activated.days_lead_to_activation.mean(),1)==17.6
    assert (activated.churned_within_6_months=="Y").sum()==56
    assert set(data.dataset_label)=={"SYNTHETIC DEMO DATA — NO REAL LEAD RECORDS"}
    assert set(data.columns)=={"dataset_label","segment","city_tier","outcome","days_lead_to_activation","churned_within_6_months","stage_reached","has_gstin","drop_reason"}

def test_synthetic_segment_and_gstin_rates_are_reproducible():
    data=load_analytics(); micro=data[data.segment=="Micro retail & services"]
    assert round(len(micro)/len(data)*100,1)==54.2
    assert round((micro.outcome=="Activated").mean()*100,1)==4.1
    for present,expected in [("Y",9.6),("N",2.0)]:
        subset=data[data.has_gstin==present]
        assert round((subset.outcome=="Activated").mean()*100,1)==expected

def test_missing_optional_analytics_returns_empty_data_frame(tmp_path,monkeypatch):
    import src.data.loaders as loaders
    monkeypatch.setattr(loaders,"ANALYTICS_PATH",tmp_path/"not-present.csv")
    loaders.load_analytics.clear()
    assert loaders.load_analytics().empty
