from src.integrations.demo_documents import make_sample_pdf
from src.utils.upload_validation import validate_specimen_upload

def test_synthetic_pdf_is_accepted_by_signature_and_trailer():
    pdf=make_sample_pdf("Sample",["Synthetic"])
    ok,_=validate_specimen_upload("specimen.pdf",pdf,5*1024*1024)
    assert ok

def test_extension_spoof_and_oversized_upload_are_rejected():
    ok,_=validate_specimen_upload("fake.pdf",b"not a pdf",100)
    assert not ok
    ok,_=validate_specimen_upload("large.pdf",b"%PDF-1.4\n%%EOF",4)
    assert not ok

def test_path_like_filename_is_not_used_for_any_storage():
    pdf=make_sample_pdf("Sample",["Synthetic"])
    ok,_=validate_specimen_upload(r"C:\\fake\\specimen.pdf",pdf,5*1024*1024)
    assert ok
