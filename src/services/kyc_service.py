"""KYC demo checks deliberately separate format, registry, and document steps."""
from src.services.registry_service import verify_gstin, verify_udyam

def validate_identifiers(gstin="", udyam=""):
    checks=[]
    if gstin:
        result=verify_gstin(gstin)
        checks.extend([
            {"name":"GSTIN format/checksum","status":"Passed" if result["format_valid"] else "Failed","detail":result["message"]},
            {"name":"Mock GSTIN registry","status":result["status"],"detail":result["message"]},
        ])
    if udyam:
        result=verify_udyam(udyam)
        checks.extend([
            {"name":"Udyam number format","status":"Passed" if result["format_valid"] else "Failed","detail":result["message"]},
            {"name":"Mock Udyam registry","status":result["status"],"detail":result["message"]},
        ])
    return checks
