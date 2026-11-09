"""Strict in-memory specimen upload signature/extension/size checks."""

def validate_specimen_upload(filename: str, content: bytes, max_bytes: int):
    name=(filename or "").rsplit("/",1)[-1].rsplit("\\",1)[-1].lower()
    ext=name.rsplit(".",1)[-1] if "." in name else ""
    if not content:
        return False,"The uploaded file is empty."
    if len(content)>max_bytes:
        return False,f"The file exceeds the {max_bytes // (1024*1024)} MB limit."
    if ext=="pdf": valid=content.startswith(b"%PDF-") and content.rstrip().endswith(b"%%EOF")
    elif ext=="png": valid=content.startswith(b"\x89PNG\r\n\x1a\n") and content.endswith(b"IEND\xaeB`\x82")
    elif ext in {"jpg","jpeg"}: valid=content.startswith(b"\xff\xd8\xff") and content.endswith(b"\xff\xd9")
    else: valid=False
    if not valid:
        return False,"The file extension and content signature do not match an accepted PDF, PNG, or JPEG specimen."
    return True,"Synthetic file signature accepted in memory. Its contents are not extracted or verified."
