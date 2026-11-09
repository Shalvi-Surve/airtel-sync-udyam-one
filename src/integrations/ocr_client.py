"""OCR adapter boundary. The current demo intentionally does not extract text."""
def extract_document(_content: bytes, _mime_type: str):
    return {"available": False, "fields": {}, "message": "OCR is not configured; file signature checks do not verify document contents."}
