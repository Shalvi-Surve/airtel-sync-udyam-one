from src.integrations.demo_documents import make_sample_pdf

def test_sample_document_is_pdf_and_watermarked():
    sample=make_sample_pdf("GST sample",["Synthetic test data"])
    assert sample.startswith(b"%PDF-1.4")
    assert b"SYNTHETIC SAMPLE - NOT A GOVERNMENT DOCUMENT" in sample
    assert sample.endswith(b"%%EOF")
