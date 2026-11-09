"""Input validators for Indian business identifiers."""
import re

GSTIN_RE = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
UDYAM_RE = re.compile(r"^UDYAM-[A-Z]{2}-\d{2}-\d{7}$", re.I)
GSTIN_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GST_STATE_CODES = {f"{code:02d}" for code in range(1,39)} | {"97", "99"}

def validate_business_profile(profile: dict) -> tuple[bool, list[str]]:
    missing=[label for key,label in (("business_name","business name"),("business_type","business type"),("city","city"),("state","state")) if not str(profile.get(key) or "").strip()]
    def integer(key):
        try: return int(profile.get(key,0) or 0)
        except (TypeError,ValueError): return 0
    if integer("employees")<1: missing.append("at least one employee")
    if integer("sites")<1: missing.append("at least one business location")
    if integer("city_tier") not in {1,2}: missing.append("a supported city tier")
    return not missing, missing

def gstin_checksum_valid(gstin: str) -> bool:
    """Validate GSTIN's base-36 checksum character."""
    value = (gstin or "").strip().upper()
    if not GSTIN_RE.fullmatch(value):
        return False
    if value[:2] not in GST_STATE_CODES:
        return False
    factor, total = 2, 0
    for char in reversed(value[:-1]):
        product = GSTIN_CHARS.index(char) * factor
        total += product // 36 + product % 36
        factor = 1 if factor == 2 else 2
    check = (36 - total % 36) % 36
    return GSTIN_CHARS[check] == value[-1]

def validate_gstin_format(gstin: str) -> tuple[bool, str]:
    value = (gstin or "").strip().upper()
    if not GSTIN_RE.fullmatch(value):
        return False, "Enter a 15-character GSTIN with a valid structure."
    if value[:2] not in GST_STATE_CODES:
        return False, "The GSTIN state code is not recognized. Check the first two digits."
    if not gstin_checksum_valid(value):
        return False, "The GSTIN checksum does not match. Check the number and try again."
    return True, "GSTIN format and checksum are valid. Registry status must be checked separately."

def validate_udyam_format(number: str) -> tuple[bool, str]:
    if not UDYAM_RE.fullmatch((number or "").strip().upper()):
        return False, "Use the format UDYAM-XX-00-0000000."
    return True, "Udyam number format is valid. Registry status must be checked separately."
