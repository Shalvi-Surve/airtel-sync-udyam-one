from src.database.repository import save_consent, get_latest_consent

def record_registry_consent(business_id: str, granted: bool):
    if type(granted) is not bool:
        raise ValueError("Consent must be explicitly true or false.")
    save_consent(business_id, "mock_registry_verification", granted)
    return {"purpose": "mock_registry_verification", "granted": bool(granted)}

def registry_consent_granted(business_id: str) -> bool:
    return get_latest_consent(business_id,"mock_registry_verification") is True
