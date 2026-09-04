from flask import Blueprint, render_template
from flask_login import login_required
from app.models.animal import Animal

bp = Blueprint('records', __name__)

@bp.route('/animals/<int:id>/record/full')
@login_required
def full_record(id):
    animal = Animal.query.get_or_404(id)
    timeline = []

    # Gather events across tables
    for i in animal.inseminations.all():
        timeline.append({'date': i.date, 'title': 'تلقیح', 'details': f"نوع: {i.insemination_type.value if hasattr(i.insemination_type, 'value') else i.insemination_type} - آبستنی: {'بله' if i.led_to_pregnancy else 'خیر'}"})

    for c in animal.calvings.all():
        timeline.append({'date': c.date, 'title': 'زایش', 'details': f"نوع: {c.calving_type.value if hasattr(c.calving_type, 'value') else c.calving_type} - تعداد: {c.offspring_count}"})

    for v in animal.vaccinations.all():
        timeline.append({'date': v.date, 'title': 'واکسیناسیون', 'details': f"واکسن: {v.vaccine_name}"})

    for m in animal.measurements.all():
        timeline.append({'date': m.date, 'title': f"اندازه‌گیری ({m.measurement_type.value if hasattr(m.measurement_type, 'value') else m.measurement_type})", 'details': f"مقدار: {m.value} {m.unit or ''}"})

    for mr in animal.milk_records.all():
        timeline.append({'date': mr.date, 'title': 'رکورد شیر', 'details': f"کل شیر: {mr.total_amount} کیلوگرم"})

    timeline.sort(key=lambda x: x['date'], reverse=True)

    return render_template('records/full.html', animal=animal, timeline=timeline)

@bp.route('/animals/<int:id>/record/summary')
@login_required
def summary_record(id):
    animal = Animal.query.get_or_404(id)
    return render_template('records/summary.html', animal=animal)
