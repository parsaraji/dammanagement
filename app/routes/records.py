from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models.animal import Animal
from app.services.jalali import from_jalali, fa_enum

bp = Blueprint('records', __name__)

@bp.route('/animals/<int:id>/record/full')
@login_required
def full_record(id):
    animal = Animal.query.get_or_404(id)
    timeline = []

    # Safe Jalali date filter parsing
    raw_start = request.args.get('start_date', '').strip()
    raw_end = request.args.get('end_date', '').strip()
    op_filter = request.args.get('type', '').strip().lower()

    start_d = None
    end_d = None
    if raw_start:
        try:
            start_d = from_jalali(raw_start)
        except Exception:
            start_d = None

    if raw_end:
        try:
            end_d = from_jalali(raw_end)
        except Exception:
            end_d = None

    def in_date_range(dt):
        if not dt:
            return False
        if start_d and dt < start_d:
            return False
        if end_d and dt > end_d:
            return False
        return True

    # 1. Insemination
    if not op_filter or op_filter == 'insemination':
        for i in animal.inseminations.all():
            if in_date_range(i.date):
                sperm_info = i.sperm.code if i.sperm else (i.sire_animal.plastic_tag if i.sire_animal else '---')
                timeline.append({
                    'type': 'insemination',
                    'date': i.date,
                    'title': 'ثبت تلقیح',
                    'icon': 'fa-heart-pulse',
                    'color': 'primary',
                    'details': f"نوع: {fa_enum(i.insemination_type)} | اسپرم/پدر: {sperm_info} | آبستنی: {'بله' if i.led_to_pregnancy else 'خیر'}"
                })

    # 2. Calving
    if not op_filter or op_filter == 'calving':
        for c in animal.calvings.all():
            if in_date_range(c.date):
                timeline.append({
                    'type': 'calving',
                    'date': c.date,
                    'title': 'ثبت زایش',
                    'icon': 'fa-baby-carriage',
                    'color': 'success',
                    'details': f"نوع: {fa_enum(c.calving_type)} | تعداد فرزندان: {c.offspring_count}"
                })

    # 3. CIDR
    if not op_filter or op_filter == 'cidr':
        for cd in animal.cidrs.all():
            if in_date_range(cd.insert_date):
                timeline.append({
                    'type': 'cidr',
                    'date': cd.insert_date,
                    'title': 'سیدرگذاری',
                    'icon': 'fa-vial-circle-check',
                    'color': 'info',
                    'details': f"نوع: {cd.cidr_type or '---'} | تاریخ خروج: {cd.remove_date|jalali if cd.remove_date else 'نامشخص'}"
                })

    # 4. DryOff
    if not op_filter or op_filter == 'dry_off':
        for d in animal.dry_offs.all():
            if in_date_range(d.start_date):
                timeline.append({
                    'type': 'dry_off',
                    'date': d.start_date,
                    'title': 'شروع خشکی',
                    'icon': 'fa-leaf',
                    'color': 'warning',
                    'details': f"توضیحات: {d.notes or '---'} | تاریخ پایان: {d.end_date|jalali if d.end_date else 'در حال خشکی'}"
                })

    # 5. TreatmentReproduction
    if not op_filter or op_filter == 'treatment':
        for tr in animal.treatments.all():
            if in_date_range(tr.date):
                timeline.append({
                    'type': 'treatment',
                    'date': tr.date,
                    'title': f"درمان / ویزیت ({fa_enum(tr.visit_type)})",
                    'icon': 'fa-user-doctor',
                    'color': 'danger',
                    'details': f"پزشک: {tr.doctor or '---'} | علت: {tr.visit_reason or '---'} | تشخیص: {tr.diagnosis or '---'}"
                })

    # 6. MedicineNoVisit
    if not op_filter or op_filter == 'medicine':
        for mnv in animal.medicines_no_visit.all():
            if in_date_range(mnv.prescribe_date):
                timeline.append({
                    'type': 'medicine',
                    'date': mnv.prescribe_date,
                    'title': 'مصرف دارو بدون ویزیت',
                    'icon': 'fa-pills',
                    'color': 'dark',
                    'details': f"نام دارو: {mnv.medicine_name} | دوز: {mnv.dose_amount} {mnv.dose_unit or ''} | روش: {mnv.consumption_method or '---'}"
                })

    # 7. Vaccination
    if not op_filter or op_filter == 'vaccination':
        for v in animal.vaccinations.all():
            if in_date_range(v.date):
                timeline.append({
                    'type': 'vaccination',
                    'date': v.date,
                    'title': 'واکسیناسیون',
                    'icon': 'fa-syringe',
                    'color': 'secondary',
                    'details': f"واکسن: {v.vaccine_name} | دوز: {v.dose_number or '---'} | تزریق‌کننده: {v.agent_name or '---'}"
                })

    # 8. Measurement
    if not op_filter or op_filter == 'measurement':
        for m in animal.measurements.all():
            if in_date_range(m.date):
                timeline.append({
                    'type': 'measurement',
                    'date': m.date,
                    'title': f"اندازه‌گیری ({fa_enum(m.measurement_type)})",
                    'icon': 'fa-ruler-vertical',
                    'color': 'primary',
                    'details': f"مقدار: {m.value} {m.unit or ''}"
                })

    # 9. Quarter
    if not op_filter or op_filter == 'quarter':
        for q in animal.quarters.all():
            if in_date_range(q.date):
                timeline.append({
                    'type': 'quarter',
                    'date': q.date,
                    'title': 'وضعیت کارتیه',
                    'icon': 'fa-circle-exclamation',
                    'color': 'info',
                    'details': f"موقعیت: {fa_enum(q.quarter)} | مشکل: {q.issue_description or '---'}"
                })

    # 10. HoofTrimming
    if not op_filter or op_filter == 'hoof':
        for ht in animal.hoof_trimmings.all():
            if in_date_range(ht.date):
                timeline.append({
                    'type': 'hoof',
                    'date': ht.date,
                    'title': 'سم‌چینی',
                    'icon': 'fa-scissors',
                    'color': 'warning',
                    'details': f"جلو چپ: {fa_enum(ht.front_left_status)} | جلو راست: {fa_enum(ht.front_right_status)} | عقب چپ: {fa_enum(ht.rear_left_status)} | عقب راست: {fa_enum(ht.rear_right_status)}"
                })

    # 11. MilkRecord
    if not op_filter or op_filter == 'milk':
        for mr in animal.milk_records.all():
            if in_date_range(mr.date):
                timeline.append({
                    'type': 'milk',
                    'date': mr.date,
                    'title': 'رکورد شیر',
                    'icon': 'fa-bottle-water',
                    'color': 'primary',
                    'details': f"نوبت ۱: {mr.milking1_amount or 0} kg | نوبت ۲: {mr.milking2_amount or 0} kg | نوبت ۳: {mr.milking3_amount or 0} kg | مجموع: {mr.total_amount} kg"
                })

    timeline.sort(key=lambda x: x['date'], reverse=True)

    return render_template('records/full.html', animal=animal, events=timeline)

@bp.route('/animals/<int:id>/record/summary')
@login_required
def summary_record(id):
    animal = Animal.query.get_or_404(id)
    return render_template('records/summary.html', animal=animal)
