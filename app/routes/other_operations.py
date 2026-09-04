from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.measurement import (
    Measurement, Quarter, OneTimeEvent, BodyScore, MovementScore,
    SuggestedSperm, HoofTrimming, MeasurementType, QuarterEnum, HoofStatusEnum
)
from app.services.jalali import from_jalali

bp = Blueprint('other_operations', __name__)

@bp.route('/other-operations/<int:animal_id>/measurement', methods=['POST'])
@login_required
def measurement_new(animal_id):
    raw_date = request.form.get('date')
    try:
        d = from_jalali(raw_date) if raw_date else None
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده نامعتبر است: {str(e)}'})

    m_type = request.form.get('measurement_type', 'weight').lower()
    try:
        val = float(request.form.get('value', 0))
    except (ValueError, TypeError):
        val = 0.0

    m = Measurement(
        animal_id=animal_id,
        date=d,
        measurement_type=MeasurementType(m_type),
        value=val,
        unit=request.form.get('unit', 'کیلوگرم'),
        created_by_user_id=current_user.id
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({'success': True, 'message': 'اندازه‌گیری ثبت شد.', 'reload': True})

@bp.route('/other-operations/<int:animal_id>/quarter', methods=['POST'])
@login_required
def quarter_new(animal_id):
    raw_date = request.form.get('date')
    try:
        d = from_jalali(raw_date) if raw_date else None
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده نامعتبر است: {str(e)}'})

    q_val = request.form.get('quarter', 'front_left').lower()
    q = Quarter(
        animal_id=animal_id,
        date=d,
        quarter=QuarterEnum(q_val),
        issue_description=request.form.get('issue_description'),
        created_by_user_id=current_user.id
    )
    db.session.add(q)
    db.session.commit()
    return jsonify({'success': True, 'message': 'وضعیت کارتیه ثبت شد.', 'reload': True})

@bp.route('/other-operations/<int:animal_id>/one-time-event', methods=['POST'])
@login_required
def one_time_event_new(animal_id):
    raw_date = request.form.get('date')
    try:
        d = from_jalali(raw_date) if raw_date else None
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده نامعتبر است: {str(e)}'})

    e = OneTimeEvent(
        animal_id=animal_id,
        date=d,
        event_type=request.form.get('event_type'),
        description=request.form.get('description'),
        created_by_user_id=current_user.id
    )
    db.session.add(e)
    db.session.commit()
    return jsonify({'success': True, 'message': 'واقعه یکبار ثبت شد.', 'reload': True})

@bp.route('/other-operations/<int:animal_id>/body-score', methods=['POST'])
@login_required
def body_score_new(animal_id):
    raw_date = request.form.get('date')
    try:
        d = from_jalali(raw_date) if raw_date else None
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده نامعتبر است: {str(e)}'})

    try:
        sc = float(request.form.get('score', 3.0))
    except (ValueError, TypeError):
        sc = 3.0

    bs = BodyScore(
        animal_id=animal_id,
        date=d,
        score=sc,
        created_by_user_id=current_user.id
    )
    db.session.add(bs)
    db.session.commit()
    return jsonify({'success': True, 'message': 'اسکور بدنی ثبت شد.', 'reload': True})

@bp.route('/other-operations/<int:animal_id>/movement-score', methods=['POST'])
@login_required
def movement_score_new(animal_id):
    raw_date = request.form.get('date')
    try:
        d = from_jalali(raw_date) if raw_date else None
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده نامعتبر است: {str(e)}'})

    try:
        sc = float(request.form.get('score', 3.0))
    except (ValueError, TypeError):
        sc = 3.0

    ms = MovementScore(
        animal_id=animal_id,
        date=d,
        score=sc,
        created_by_user_id=current_user.id
    )
    db.session.add(ms)
    db.session.commit()
    return jsonify({'success': True, 'message': 'اسکور حرکتی ثبت شد.', 'reload': True})

@bp.route('/other-operations/<int:animal_id>/suggested-sperm', methods=['POST'])
@login_required
def suggested_sperm_new(animal_id):
    raw_date = request.form.get('date')
    try:
        d = from_jalali(raw_date) if raw_date else None
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده نامعتبر است: {str(e)}'})

    ss = SuggestedSperm(
        animal_id=animal_id,
        date=d,
        parity_cycle=int(request.form.get('parity_cycle', 1)),
        sperm_1_id=int(request.form.get('sperm_1_id')) if request.form.get('sperm_1_id') and request.form.get('sperm_1_id').isdigit() else None,
        sperm_2_id=int(request.form.get('sperm_2_id')) if request.form.get('sperm_2_id') and request.form.get('sperm_2_id').isdigit() else None,
        created_by_user_id=current_user.id
    )
    db.session.add(ss)
    db.session.commit()
    return jsonify({'success': True, 'message': 'اسپرم پیشنهادی ثبت شد.', 'reload': True})

@bp.route('/other-operations/<int:animal_id>/hoof-trimming', methods=['POST'])
@login_required
def hoof_trimming_new(animal_id):
    raw_date = request.form.get('date')
    try:
        d = from_jalali(raw_date) if raw_date else None
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده نامعتبر است: {str(e)}'})

    ht = HoofTrimming(
        animal_id=animal_id,
        date=d,
        front_left_status=HoofStatusEnum(request.form.get('front_left_status', 'healthy')),
        front_right_status=HoofStatusEnum(request.form.get('front_right_status', 'healthy')),
        rear_left_status=HoofStatusEnum(request.form.get('rear_left_status', 'healthy')),
        rear_right_status=HoofStatusEnum(request.form.get('rear_right_status', 'healthy')),
        created_by_user_id=current_user.id
    )
    db.session.add(ht)
    db.session.commit()
    return jsonify({'success': True, 'message': 'سم‌چینی ثبت شد.', 'reload': True})
