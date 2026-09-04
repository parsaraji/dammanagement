from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.medical import TreatmentReproduction, MedicineNoVisit, Vaccination, VisitType
from app.services.jalali import from_jalali

bp = Blueprint('medical', __name__)

@bp.route('/medical/<int:animal_id>/treatment', methods=['POST'])
@login_required
def treatment_new(animal_id):
    raw_date = request.form.get('date')
    try:
        d = from_jalali(raw_date) if raw_date else None
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده نامعتبر است: {str(e)}'})

    if not d:
        return jsonify({'success': False, 'message': 'لطفاً تاریخ را وارد کنید.'})

    vtype_str = request.form.get('visit_type', 'medical').lower()
    vtype = VisitType.REPRODUCTIVE if vtype_str == 'reproductive' else VisitType.MEDICAL

    t = TreatmentReproduction(
        animal_id=animal_id,
        visit_type=vtype,
        date=d,
        doctor=request.form.get('doctor'),
        visit_reason=request.form.get('visit_reason'),
        diagnosis=request.form.get('diagnosis'),
        notes=request.form.get('notes'),
        created_by_user_id=current_user.id
    )
    db.session.add(t)
    db.session.commit()
    return jsonify({'success': True, 'message': 'درمان/ویزیت ثبت شد.', 'reload': True})

@bp.route('/medical/treatment/<int:id>/end', methods=['POST'])
@login_required
def treatment_end(id):
    t = db.session.get(TreatmentReproduction, id)
    if not t:
        return jsonify({'success': False, 'message': 'سابقه درمان یافت نشد.'})

    raw_date = request.form.get('treatment_end_date')
    try:
        end_d = from_jalali(raw_date) if raw_date else None
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ پایان درمان نامعتبر است: {str(e)}'})

    t.treatment_end_date = end_d
    db.session.commit()
    return jsonify({'success': True, 'message': 'پایان درمان ثبت شد.', 'reload': True})

@bp.route('/medical/<int:animal_id>/medicine-no-visit', methods=['POST'])
@login_required
def medicine_no_visit_new(animal_id):
    raw_pdate = request.form.get('prescribe_date')
    raw_cdate = request.form.get('consume_date')
    try:
        pdate = from_jalali(raw_pdate) if raw_pdate else None
        cdate = from_jalali(raw_cdate) if raw_cdate else pdate
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده نامعتبر است: {str(e)}'})

    if not pdate:
        return jsonify({'success': False, 'message': 'لطفاً تاریخ تجویز را وارد کنید.'})

    try:
        dose_amt = float(request.form.get('dose_amount', 0))
    except (ValueError, TypeError):
        dose_amt = 0.0

    mnv = MedicineNoVisit(
        animal_id=animal_id,
        prescribe_date=pdate,
        consume_date=cdate,
        medicine_name=request.form.get('medicine_name'),
        dose_amount=dose_amt,
        dose_unit=request.form.get('dose_unit'),
        consumption_method=request.form.get('consumption_method'),
        created_by_user_id=current_user.id
    )
    db.session.add(mnv)
    db.session.commit()
    return jsonify({'success': True, 'message': 'مصرف دارو بدون ویزیت ثبت شد.', 'reload': True})

@bp.route('/medical/<int:animal_id>/vaccination', methods=['POST'])
@login_required
def vaccination_new(animal_id):
    d = from_jalali(request.form.get('date'))
    v = Vaccination(
        animal_id=animal_id,
        date=d,
        dose_number=request.form.get('dose_number'),
        vaccine_name=request.form.get('vaccine_name'),
        agent_name=request.form.get('agent_name'),
        created_by_user_id=current_user.id
    )
    db.session.add(v)
    db.session.commit()
    return jsonify({'success': True, 'message': 'واکسیناسیون ثبت شد.', 'reload': True})
