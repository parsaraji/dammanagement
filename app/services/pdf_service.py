import io
import base64
import qrcode
from xhtml2pdf import pisa
from app.services.jalali import to_jalali

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
    sex_str = 'ماده' if (getattr(animal.sex, 'value', animal.sex) == 'female') else 'نر'
    species_str = 'گوسفند' if (getattr(animal.species, 'value', animal.species) == 'sheep') else 'بز'

    html = f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A6 landscape;
                margin: 10mm;
            }}
            body {{
                font-family: Arial, Helvetica, sans-serif;
                direction: rtl;
                text-align: right;
                font-size: 12pt;
            }}
            .card {{
                border: 2px solid #333;
                padding: 15px;
                border-radius: 8px;
            }}
            .title {{
                text-align: center;
                font-size: 16pt;
                font-weight: bold;
                border-bottom: 1px solid #ccc;
                padding-bottom: 5px;
                margin-bottom: 15px;
            }}
            table {{
                width: 100%;
            }}
            td {{
                padding: 5px;
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
            <div class="title">شناسنامه دام (کارت هویت)</div>
            <table>
                <tr>
                    <td width="70%">
                        <p><strong>شماره پلاستیکی:</strong> {animal.plastic_tag}</p>
                        <p><strong>شماره سریال:</strong> {animal.serial_number}</p>
                        <p><strong>شناسنامه ملی:</strong> {animal.national_id or '---'}</p>
                        <p><strong>جنسیت:</strong> {sex_str}</p>
                        <p><strong>گونه / نژاد:</strong> {species_str} - {animal.breed or '---'}</p>
                        <p><strong>تاریخ تولد:</strong> {to_jalali(animal.birth_date)}</p>
                    </td>
                    <td width="30%" class="qr-cell">
                        <img src="data:image/png;base64,{qr_b64}" width="120" height="120"/>
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
    rows_html = ""
    for row in rows:
        cells = "".join([f"<td>{cell}</td>" for cell in row])
        rows_html += f"<tr>{cells}</tr>"

    headers_html = "".join([f"<th>{h}</th>" for h in headers])

    html = f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4 portrait;
                margin: 15mm;
            }}
            body {{
                font-family: Arial, Helvetica, sans-serif;
                direction: rtl;
                text-align: right;
                font-size: 10pt;
            }}
            h2 {{
                text-align: center;
                margin-bottom: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>
        <h2>{title}</h2>
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
