import pypdf
import io
from app.models.animal import Animal
from app.services.pdf_service import generate_animal_id_card, generate_pdf_report, fa_pdf

def test_fa_pdf_shaping():
    reshaped = fa_pdf("مدیریت و اطلاعات دامداری")
    assert reshaped is not None
    assert len(reshaped) > 0

def test_pdf_id_card_generation(app):
    with app.app_context():
        animal = Animal.query.filter_by(plastic_tag='IR-G0-F1').first()
        assert animal is not None

        pdf_bytes = generate_animal_id_card(animal)
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000

        # Verify PDF can be read by PyPDF
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        assert len(reader.pages) >= 1

def test_pdf_report_generation(app):
    with app.app_context():
        headers = ["نام دام", "شماره پلاک", "جنسیت", "تاریخ تولد", "وضعیت"]
        rows = [
            ["گوسفند ۱", "12345", "ماده", "1402/01/01", "زنده"],
            ["بز ۲", "67890", "نر", "1401/05/10", "زنده"]
        ]
        pdf_bytes = generate_pdf_report("گزارش آزمایشی دام‌ها", headers, rows)
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000

        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        assert len(reader.pages) == 1
