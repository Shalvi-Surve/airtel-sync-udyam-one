"""Minimal synthetic, watermark-labeled PDF specimens for demo UX testing."""

def make_sample_pdf(title, lines):
    def esc(value):
        return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("latin-1", "replace").decode("latin-1")

    commands=["BT /F1 16 Tf 50 770 Td (SYNTHETIC SAMPLE - NOT A GOVERNMENT DOCUMENT) Tj /F1 14 Tf 0 -34 Td ("+esc(title)+") Tj /F1 10 Tf 0 -30 Td"]
    for index,line in enumerate(lines):
        if index: commands.append("0 -18 Td")
        commands.append("("+esc(line)+") Tj")
    commands.append("0 -40 Td (For UdyamOne demo testing only. No real person or business.) Tj ET")
    stream="\n".join(commands).encode("latin-1")
    objects=[b"<< /Type /Catalog /Pages 2 0 R >>",b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",b"<< /Length "+str(len(stream)).encode()+b" >>\nstream\n"+stream+b"\nendstream"]
    pdf=bytearray(b"%PDF-1.4\n"); offsets=[0]
    for i,obj in enumerate(objects,1): offsets.append(len(pdf)); pdf+=f"{i} 0 obj\n".encode()+obj+b"\nendobj\n"
    xref=len(pdf); pdf+=f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode()
    for offset in offsets[1:]: pdf+=f"{offset:010d} 00000 n \n".encode()
    pdf+=f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    return bytes(pdf)
