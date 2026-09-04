import io
import os
import base64
from pathlib import Path
import qrcode
import arabic_reshaper
from bidi.algorithm import get_display
from xhtml2pdf import pisa
from app.services.jalali import to_jalali

FONT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'vazirmatn', 'Vazirmatn-Regular.ttf'))
FONT_URI = Path(FONT_PATH).as_uri()

def fa_pdf(text) -> str:
    if text is None:
        return ""
    text_str = str(text)
    reshaped = arabic_reshaper.reshape(text_str)
    return get_display(reshaped)

def generate_qr_code_base64(data: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_animal_id_card(animal):
    qr_b64 = generate_qr_code_base64(animal.plastic_tag)
    sex_val = getattr(animal.sex, 'value', animal.sex)
    species_val = getattr(animal.species, 'value', animal.species)

    sex_str = fa_pdf('ماده' if sex_val == 'female' else 'نر')
    species_str = fa_pdf('گوسفند' if species_val == 'sheep' else 'بز')
    title_str = fa_pdf("شناسنامه دام (کارت هویت)")
    plastic_label = fa_pdf("شماره پلاستیکی:")
    serial_label = fa_pdf("شماره سریال:")
    national_label = fa_pdf("شناسنامه ملی:")
    sex_label = fa_pdf("جنسیت:")
    breed_label = fa_pdf("گونه / نژاد:")
    birth_label = fa_pdf("تاریخ تولد:")

    breed_val = fa_pdf(animal.breed) if animal.breed else "---"
    jalali_birth = fa_pdf(to_jalali(animal.birth_date))

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @font-face {{
                font-family: 'Vazirmatn';
                src: url('{FONT_URI}');
            }}
            @page {{
                size: A6 landscape;
                margin: 8mm;
            }}
            body {{
                font-family: 'Vazirmatn', sans-serif;
                text-align: right;
                font-size: 11pt;
            }}
            .card {{
                border: 2px solid #2c3e50;
                padding: 12px;
                border-radius: 6px;
            }}
            .title {{
                text-align: center;
                font-size: 15pt;
                font-weight: bold;
                border-bottom: 1px solid #ccc;
                padding-bottom: 4px;
                margin-bottom: 12px;
                color: #2c3e50;
            }}
            table {{
                width: 100%;
            }}
            td {{
                padding: 4px;
                vertical-align: top;
            }}
            .qr-cell {{
                text-align: center;
                vertical-align: middle;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="title">{title_str}</div>
            <table>
                <tr>
                    <td width="70%">
                        <p><strong>{plastic_label}</strong> {animal.plastic_tag}</p>
                        <p><strong>{serial_label}</strong> {animal.serial_number}</p>
                        <p><strong>{national_label}</strong> {animal.national_id or '---'}</p>
                        <p><strong>{sex_label}</strong> {sex_str}</p>
                        <p><strong>{breed_label}</strong> {species_str} - {breed_val}</p>
                        <p><strong>{birth_label}</strong> {jalali_birth}</p>
                    </td>
                    <td width="30%" class="qr-cell">
                        <img src="data:image/png;base64,{qr_b64}" width="110" height="120"/>
                        <p><small>{animal.plastic_tag}</small></p>
                    </td>
                </tr>
            </table>
        </div>
    </body>
    </html>
    """
    pdf_out = io.BytesIO()
    pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=pdf_out)
    return pdf_out.getvalue()

def generate_pdf_report(title, headers, rows):
    title_fa = fa_pdf(title)
    headers_fa = [fa_pdf(h) for h in headers]
    rows_fa = [[fa_pdf(cell) for cell in row] for row in rows]

    rows_html = ""
    for row in rows_fa:
        cells = "".join([f"<td>{cell}</td>" for cell in row])
        rows_html += f"<tr>{cells}</tr>"

    headers_html = "".join([f"<th>{h}</th>" for h in headers_fa])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @font-face {{
                font-family: 'Vazirmatn';
                src: url('{FONT_PATH}');
            }}
            @page {{
                size: A4 portrait;
                margin: 12mm;
            }}
            body {{
                font-family: 'Vazirmatn', sans-serif;
                text-align: right;
                font-size: 10pt;
            }}
            h2 {{
                text-align: center;
                margin-bottom: 16px;
                color: #2c3e50;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th, td {{
                border: 1px solid #bdc3c7;
                padding: 6px;
                text-align: center;
            }}
            th {{
                background-color: #ecf0f1;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <h2>{title_fa}</h2>
        <table>
            <thead>
                <tr>{headers_html}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </body>
    </html>
    """
    pdf_out = io.BytesIO()
    pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=pdf_out)
    return pdf_out.getvalue()
