from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.medical import TreatmentReproduction, MedicineNoVisit, Vaccination, VisitType
from app.services.jalali import from_jalali

bp = Blueprint('medical', __name__)

@bp.route('/medical/<int:animal_id>/treatment', methods=['POST'])
@login_required
def treatment_new(animal_id):
    d = from_jalali(request.form.get('date'))
    t = TreatmentReproduction(
        animal_id=animal_id,
        visit_type=VisitType[request.form.get('visit_type', 'medical').upper()],
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
