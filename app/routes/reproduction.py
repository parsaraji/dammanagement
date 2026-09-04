from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.animal import Animal, Sex, Species
from app.models.sperm import Sperm
from app.models.reproduction import (
    CIDR, Insemination, HeatNoInsemination, DryOff, Calving, CalvingOffspring,
    InseminationType, CalvingType
)
from app.services.jalali import from_jalali

bp = Blueprint('reproduction', __name__)

@bp.route('/reproduction/<int:animal_id>/insemination', methods=['POST'])
@login_required
def insemination_new(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    if animal.sex != Sex.FEMALE:
        return jsonify({'success': False, 'message': 'تلقیح فقط برای دام ماده قابل ثبت است.'})

    raw_date = request.form.get('date')
    try:
        d = from_jalali(raw_date) if raw_date else None
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده شمسی نامعتبر است: {str(e)}'})

    if not d:
        return jsonify({'success': False, 'message': 'لطفاً تاریخ تلقیح را وارد کنید.'})

    insem_type = request.form.get('insemination_type', 'artificial')
    sperm_id = int(request.form.get('sperm_id')) if request.form.get('sperm_id') and request.form.get('sperm_id').isdigit() else None
    sire_id = int(request.form.get('sire_animal_id')) if request.form.get('sire_animal_id') and request.form.get('sire_animal_id').isdigit() else None
    led_to_preg = True if request.form.get('led_to_pregnancy') in ['y', 'true', 'True', '1'] else False

    if sperm_id:
        sperm_obj = db.session.get(Sperm, sperm_id)
        if not sperm_obj:
            return jsonify({'success': False, 'message': 'اسپرم انتخابی یافت نشد.'})

    if sire_id:
        sire_obj = db.session.get(Animal, sire_id)
        if not sire_obj:
            return jsonify({'success': False, 'message': 'دام نر انتخابی یافت نشد.'})
        if sire_obj.sex != Sex.MALE:
            return jsonify({'success': False, 'message': 'دام پدر انتخابی باید نر باشد.'})
        if sire_obj.species != animal.species:
            return jsonify({'success': False, 'message': 'گونه دام پدر و مادر یکسان نیست.'})

    insem = Insemination(
        animal_id=animal.id,
        date=d,
        insemination_type=InseminationType.ARTIFICIAL if insem_type == 'artificial' else InseminationType.NATURAL,
        sperm_id=sperm_id,
        sire_animal_id=sire_id,
        parity_cycle=animal.parity or 1,
        led_to_pregnancy=led_to_preg,
        created_by_user_id=current_user.id
    )
    db.session.add(insem)
    db.session.commit()
    return jsonify({'success': True, 'message': 'تلقیح با موفقیت ثبت شد.', 'reload': True})

@bp.route('/reproduction/<int:animal_id>/cidr', methods=['POST'])
@login_required
def cidr_new(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    try:
        ins_date = from_jalali(request.form.get('insert_date'))
        rem_date = from_jalali(request.form.get('remove_date')) if request.form.get('remove_date') else None
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده شمسی نامعتبر است: {str(e)}'})

    if not ins_date:
        return jsonify({'success': False, 'message': 'لطفاً تاریخ سیدرگذاری را وارد کنید.'})

    cidr = CIDR(
        animal_id=animal.id,
        insert_date=ins_date,
        remove_date=rem_date,
        cidr_type=request.form.get('cidr_type'),
        notes=request.form.get('notes'),
        created_by_user_id=current_user.id
    )
    db.session.add(cidr)
    db.session.commit()
    return jsonify({'success': True, 'message': 'سیدرگذاری ثبت شد.', 'reload': True})

@bp.route('/reproduction/<int:animal_id>/dry-off', methods=['POST'])
@login_required
def dry_off_new(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    try:
        start_d = from_jalali(request.form.get('start_date'))
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده شمسی نامعتبر است: {str(e)}'})

    if not start_d:
        return jsonify({'success': False, 'message': 'لطفاً تاریخ شروع خشکی را وارد کنید.'})

    dry = DryOff(
        animal_id=animal.id,
        start_date=start_d,
        notes=request.form.get('notes'),
        created_by_user_id=current_user.id
    )
    db.session.add(dry)
    db.session.commit()
    return jsonify({'success': True, 'message': 'خشکی با موفقیت ثبت شد.', 'reload': True})

@bp.route('/reproduction/<int:animal_id>/calving', methods=['POST'])
@login_required
def calving_new(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    if animal.sex != Sex.FEMALE:
        return jsonify({'success': False, 'message': 'ثبت زایش فقط برای دام ماده مجاز است.'})

    try:
        calv_date = from_jalali(request.form.get('date'))
    except ValueError as e:
        return jsonify({'success': False, 'message': f'تاریخ وارد شده شمسی نامعتبر است: {str(e)}'})

    if not calv_date:
        return jsonify({'success': False, 'message': 'لطفاً تاریخ زایش را وارد کنید.'})

    calv_type_str = request.form.get('calving_type', 'normal').lower()
    if calv_type_str not in [t.value for t in CalvingType]:
        return jsonify({'success': False, 'message': 'نوع زایش نامعتبر است.'})

    try:
        offspring_cnt = int(request.form.get('offspring_count', 1))
        if offspring_cnt < 0 or offspring_cnt > 5:
            return jsonify({'success': False, 'message': 'تعداد فرزندان باید بین ۰ تا ۵ باشد.'})
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'تعداد فرزندان نامعتبر است.'})

    calv = Calving(
        animal_id=animal.id,
        date=calv_date,
        calving_type=CalvingType(calv_type_str),
        offspring_count=offspring_cnt,
        created_by_user_id=current_user.id
    )

    # Business rule: abortion does NOT increment parity
    if calv_type_str != 'abortion':
        animal.parity = (animal.parity or 0) + 1

    db.session.add(calv)
    db.session.commit()

    if calv_type_str != 'abortion' and offspring_cnt > 0:
        return jsonify({
            'success': True,
            'message': 'زایش ثبت شد. لطفاً مشخصات بره/بزغاله متولد شده را ثبت کنید.',
            'open_newborn_modal': True,
            'newborn_data': {
                'mother_id': animal.id,
                'species': animal.species.value if hasattr(animal.species, 'value') else animal.species,
                'birth_date': request.form.get('date'),
                'count': offspring_cnt
            }
        })

    return jsonify({'success': True, 'message': 'زایش با موفقیت ثبت شد.', 'reload': True})
