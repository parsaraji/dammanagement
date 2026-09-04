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
    d = from_jalali(request.form.get('date'))
    m_type = request.form.get('measurement_type', 'weight')
    val = float(request.form.get('value', 0))

    m = Measurement(
        animal_id=animal_id,
        date=d,
        measurement_type=MeasurementType[m_type.upper()],
        value=val,
        unit=request.form.get('unit', 'کیلوگرم'),
        created_by_user_id=current_user.id
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({'success': True, 'message': 'اندازه‌گیری ثبت شد.', 'reload': True})
