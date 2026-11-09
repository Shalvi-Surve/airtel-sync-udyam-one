from src.utils.validators import validate_gstin_format, validate_udyam_format, gstin_checksum_valid
from src.services.registry_service import verify_gstin, verify_udyam

def test_gstin_format_rejects_bad_checksum():
    ok, _ = validate_gstin_format("32TTNXB7384T1Z0")
    assert not ok

def test_gstin_rejects_unknown_state_code_even_with_checksum_shaped_value():
    assert validate_gstin_format("00AAPFU0939F1Z0")[0] is False

def test_gstin_checksum_can_validate_generated_value():
    # Build the checksum from the first 14 characters using the GSTIN base-36 rule.
    chars="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"; prefix="27AAPFU0939F1Z"
    factor,total=2,0
    for char in reversed(prefix):
        product=chars.index(char)*factor; total += product//36+product%36; factor=1 if factor==2 else 2
    gstin=prefix+chars[(36-total%36)%36]
    assert gstin_checksum_valid(gstin)
    assert validate_gstin_format(gstin)[0]

def test_udyam_format_and_mock_registry_are_distinct():
    assert validate_udyam_format("UDYAM-KL-00-3078801")[0]
    result = verify_udyam("UDYAM-KL-00-3078801")
    assert "mock registry" in result["message"]
    assert result["format_valid"] is True

def test_gstin_mock_lookup_does_not_skip_format_validation():
    result=verify_gstin("not-a-gstin")
    assert result["format_valid"] is False
    assert result["found"] is False

def test_synthetic_demo_registry_pair_is_active_and_name_matched():
    gst=verify_gstin("32TTNXB7384T1ZW")
    udyam=verify_udyam("UDYAM-KL-00-3078801")
    assert gst["format_valid"] and gst["found"] and gst["status"]=="Active"
    assert udyam["format_valid"] and udyam["found"]
    assert gst["record"]["trade_name"]==udyam["record"]["enterprise_name"]
