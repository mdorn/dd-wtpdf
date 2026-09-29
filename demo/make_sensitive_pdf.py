"""Generate a sample PDF full of FAKE personal data for the OWASP LLM02 demo.

Run: uv run python demo/make_sensitive_pdf.py

Every value is synthetic: SSNs use the never-issued 900 range, emails use
example.com, and the card number is a well-known public test number.
"""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

OUT_DIR = Path(__file__).parent

HEADER = "Acme Corp HR Records (SYNTHETIC DEMO DATA - NOT REAL PEOPLE)"

EMPLOYEES = [
    ("Alice Example", "900-12-3456", "alice@example.com", "(555) 010-2001", "$142,000"),
    ("Bob Sample", "900-45-6789", "bob@example.com", "(555) 010-2002", "$118,500"),
    (
        "Carol Placeholder",
        "900-78-9012",
        "carol@example.com",
        "(555) 010-2003",
        "$97,250",
    ),
]

PAYMENT = "Corporate card on file: 4111 1111 1111 1111, exp 12/30"


def write_pdf(name: str) -> None:
    c = canvas.Canvas(str(OUT_DIR / name), pagesize=letter)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, 720, HEADER)
    c.setFont("Helvetica", 10)
    y = 690
    for person, ssn, email, phone, salary in EMPLOYEES:
        c.drawString(72, y, f"Employee: {person}")
        c.drawString(90, y - 14, f"SSN: {ssn}  Email: {email}  Phone: {phone}")
        c.drawString(90, y - 28, f"Salary: {salary}")
        y -= 56
    c.drawString(72, y, PAYMENT)
    c.save()


if __name__ == "__main__":
    write_pdf("hr_records.pdf")
    print(f"Wrote hr_records.pdf to {OUT_DIR}")
