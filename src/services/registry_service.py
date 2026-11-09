"""Demo-only registry lookups; format checks are separate from existence/status."""
from src.data.loaders import load_gstin_registry, load_udyam_registry
from src.utils.validators import validate_gstin_format, validate_udyam_format

def verify_gstin(number):
    valid, message = validate_gstin_format(number)
    if not valid: return {"format_valid": False, "found": False, "status": "Invalid format/checksum", "message": message}
    matches=load_gstin_registry(); row=matches[matches["gstin"].str.upper()==number.strip().upper()]
    if row.empty: return {"format_valid": True, "found": False, "status": "Not found in demo registry", "message": "Format is valid; the supplied mock registry has no matching record."}
    data=row.iloc[0].to_dict()
    return {"format_valid":True,"found":True,"status":data.get("status","Unknown"),"message":f"Mock registry record found: {data.get('status','Unknown')}.","record":data}

def verify_udyam(number):
    valid,message=validate_udyam_format(number)
    if not valid: return {"format_valid":False,"found":False,"status":"Invalid format","message":message}
    df=load_udyam_registry(); row=df[df["udyam_number"].str.upper()==number.strip().upper()]
    if row.empty: return {"format_valid":True,"found":False,"status":"Not found in demo registry","message":"Format is valid; the supplied mock registry has no matching record."}
    data=row.iloc[0].to_dict()
    return {"format_valid":True,"found":True,"status":"Matched in mock registry","message":"Record found in the mock registry.","record":data}
