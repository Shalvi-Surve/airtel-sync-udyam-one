"""Cached, validated access to supplied CSV datasets."""
import pandas as pd
import streamlit as st
from src.config.settings import CATALOGUE_PATH, GSTIN_REGISTRY_PATH, UDYAM_REGISTRY_PATH, ANALYTICS_PATH

def _read_required_csv(path, label, **kwargs):
    if not path.is_file():
        raise FileNotFoundError(f"Required {label} dataset is missing from the deployment package.")
    return pd.read_csv(path, **kwargs)

@st.cache_data(show_spinner=False)
def load_catalogue():
    df = _read_required_csv(CATALOGUE_PATH, "product catalogue", keep_default_na=False)
    required = {"product_id", "product_name", "category", "price_min_inr_per_month", "price_max_inr_per_month", "one_time_setup_inr"}
    if not required.issubset(df.columns):
        raise ValueError(f"Catalogue is missing columns: {', '.join(sorted(required - set(df.columns)))}")
    for col in ("price_min_inr_per_month", "price_max_inr_per_month", "one_time_setup_inr", "min_contract_months", "min_employees", "min_sites", "typical_install_days"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

@st.cache_data(show_spinner=False)
def load_gstin_registry():
    return _read_required_csv(GSTIN_REGISTRY_PATH, "mock GSTIN registry", dtype=str).fillna("")

@st.cache_data(show_spinner=False)
def load_udyam_registry():
    return _read_required_csv(UDYAM_REGISTRY_PATH, "mock Udyam registry", dtype=str).fillna("")

@st.cache_data(show_spinner=False)
def load_analytics():
    if not ANALYTICS_PATH.is_file():
        return pd.DataFrame()
    df = _read_required_csv(ANALYTICS_PATH, "synthetic demo analytics")
    required = {"dataset_label", "segment", "city_tier", "outcome", "days_lead_to_activation", "churned_within_6_months", "stage_reached", "has_gstin", "drop_reason"}
    if not required.issubset(df.columns):
        raise ValueError(f"Synthetic demo analytics is missing columns: {', '.join(sorted(required - set(df.columns)))}")
    if not df.empty and set(df["dataset_label"].dropna()) != {"SYNTHETIC DEMO DATA — NO REAL LEAD RECORDS"}:
        raise ValueError("Analytics data must be labelled as synthetic demo data.")
    if "created_date" in df:
        df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
    return df
