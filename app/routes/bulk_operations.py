from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.animal import Animal, AnimalStatus, Sex, Species
from app.models.pen import Pen
from app.models.medical import Vaccination, TreatmentReproduction, MedicineNoVisit, VisitType
from app.models.reproduction import CIDR, DryOff, Insemination, InseminationType, Calving, CalvingType, HeatNoInsemination
from app.models.measurement import (
    Measurement, MeasurementType, HoofTrimming, HoofStatusEnum, BodyScore, MovementScore,
    Quarter, QuarterEnum, OneTimeEvent, SuggestedSperm
)
from app.models.sperm import Sperm
from app.services.jalali import from_jalali

bp = Blueprint('bulk_operations', __name__)

@bp.route('/bulk-operations')
@login_required
def index():
    working_ids = session.get('bulk_working_ids', [])
    selected_animals = Animal.query.filter(Animal.id.in_(working_ids)).all() if working_ids else []
    pens = Pen.query.all()
    return render_template('bulk_operations/index.html', working_list=working_ids, selected_animals=selected_animals, pens=pens)

@bp.route('/bulk-operations/select', methods=['POST'])
@login_required
def select_animals():
    pen_id = request.form.get('pen_id')
    species = request.form.get('species')
    sex = request.form.get('sex')

    query = Animal.query.filter_by(status=AnimalStatus.ALIVE)
    if pen_id:
        query = query.filter_by(current_pen_id=int(pen_id))
    if species:
        query = query.filter_by(species=Species[species.upper()])
    if sex:
        query = query.filter_by(sex=Sex[sex.upper()])

    animals = query.all()
    session['bulk_working_ids'] = [a.id for a in animals]
    flash(f'تعداد {len(animals)} دام بر اساس فیلترها به لیست کاری اضافه شدند.', 'info')
    return redirect(url_for('bulk_operations.index'))

@bp.route('/bulk-operations/quick-apply', methods=['POST'])
@login_required
def quick_apply():
    working_ids = session.get('bulk_working_ids', [])
    if not working_ids:
        flash('هیچ دامی در لیست کاری وجود ندارد.', 'warning')
        return redirect(url_for('bulk_operations.index'))

    op_type = request.form.get('op_type')
    raw_date = request.form.get('date')
    try:
        d = from_jalali(raw_date) if raw_date else None
    except ValueError as e:
        flash(f'تاریخ وارد شده نامعتبر است: {str(e)}', 'danger')
        return redirect(url_for('bulk_operations.index'))

    if not d:
        flash('تاریخ انجام عملیات الزامی است.', 'danger')
        return redirect(url_for('bulk_operations.index'))

    count = 0
    try:
        for aid in working_ids:
            animal = db.session.get(Animal, aid)
            if not animal:
                continue

            if op_type == 'vaccination':
                vac_name = request.form.get('vaccine_name') or request.form.get('detail') or 'واکسن عمومی'
                v = Vaccination(
                    animal_id=aid,
                    date=d,
                    vaccine_name=vac_name,
                    dose_number=request.form.get('dose_number'),
                    agent_name=request.form.get('agent_name'),
                    created_by_user_id=current_user.id
                )
                db.session.add(v)
                count += 1

            elif op_type == 'cidr':
                rem_raw = request.form.get('remove_date')
                rem_d = from_jalali(rem_raw) if rem_raw else None
                c = CIDR(
                    animal_id=aid,
                    insert_date=d,
                    remove_date=rem_d,
                    cidr_type=request.form.get('cidr_type'),
                    notes=request.form.get('notes'),
                    created_by_user_id=current_user.id
                )
                db.session.add(c)
                count += 1

            elif op_type == 'removal':
                status_choice = request.form.get('removal_status', 'ready_for_removal')
                if status_choice == 'removed':
                    animal.status = AnimalStatus.REMOVED
                    animal.removal_date = d
                    animal.removal_buyer_name = request.form.get('removal_buyer_name')
                else:
                    animal.status = AnimalStatus.READY_FOR_REMOVAL
                animal.removal_reason = request.form.get('removal_reason')
                count += 1

            elif op_type == 'natural_mating':
                if animal.sex == Sex.FEMALE:
                    sire_id_raw = request.form.get('sire_animal_id')
                    sire_id = int(sire_id_raw) if sire_id_raw and sire_id_raw.isdigit() else None
                    insem = Insemination(
                        animal_id=aid,
                        date=d,
                        insemination_type=InseminationType.NATURAL,
                        sire_animal_id=sire_id,
                        parity_cycle=animal.parity or 1,
                        led_to_pregnancy=True if request.form.get('led_to_pregnancy') in ['y', 'true', '1'] else False,
                        created_by_user_id=current_user.id
                    )
                    db.session.add(insem)
                    count += 1

            elif op_type == 'dry_off':
                if animal.sex == Sex.FEMALE:
                    dry = DryOff(
                        animal_id=aid,
                        start_date=d,
                        notes=request.form.get('notes'),
                        created_by_user_id=current_user.id
                    )
                    db.session.add(dry)
                    count += 1

        db.session.commit()
        flash(f'عملیات سریع ({op_type}) روی {count} دام با موفقیت اعمال گردید.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در اجرای عملیات سریع: {str(e)}', 'danger')

    return redirect(url_for('bulk_operations.index'))

@bp.route('/bulk-operations/batch-submit', methods=['POST'])
@login_required
def batch_submit():
    animal_ids = request.form.getlist('batch_animal_id[]')
    op_types = request.form.getlist('batch_op_type[]')
    dates = request.form.getlist('batch_date[]')
    p1s = request.form.getlist('batch_p1[]')
    p2s = request.form.getlist('batch_p2[]')

    if not animal_ids:
        flash('هیچ عملیاتی در بچ ثبت نشده است.', 'warning')
        return redirect(url_for('bulk_operations.index'))

    count = 0
    try:
        for i, aid_str in enumerate(animal_ids):
            aid = int(aid_str)
            op = op_types[i]
            raw_d = dates[i]
            d = from_jalali(raw_d) if raw_d else None
            p1 = p1s[i] if i < len(p1s) else ''
            p2 = p2s[i] if i < len(p2s) else ''

            if op == 'vaccine':
                v = Vaccination(animal_id=aid, date=d, vaccine_name=p1 or 'واکسن عمومی', dose_number=p2, created_by_user_id=current_user.id)
                db.session.add(v)
            elif op == 'insemination':
                insem = Insemination(
                    animal_id=aid,
                    date=d,
                    insemination_type=InseminationType.ARTIFICIAL if p1 == 'artificial' else InseminationType.NATURAL,
                    sperm_id=int(p2) if p2 and p2.isdigit() else None,
                    created_by_user_id=current_user.id
                )
                db.session.add(insem)
            elif op == 'calving':
                cnt = int(p2) if p2 and p2.isdigit() else 1
                c = Calving(
                    animal_id=aid,
                    date=d,
                    calving_type=CalvingType(p1) if p1 in [t.value for t in CalvingType] else CalvingType.NORMAL,
                    offspring_count=cnt,
                    created_by_user_id=current_user.id
                )
                db.session.add(c)
            elif op == 'cidr':
                c = CIDR(animal_id=aid, insert_date=d, cidr_type=p1, notes=p2, created_by_user_id=current_user.id)
                db.session.add(c)
            elif op == 'dry_off':
                dry = DryOff(animal_id=aid, start_date=d, notes=p1, created_by_user_id=current_user.id)
                db.session.add(dry)
            elif op == 'treatment':
                tr = TreatmentReproduction(animal_id=aid, date=d, visit_type=VisitType.MEDICAL, doctor=p1, diagnosis=p2, created_by_user_id=current_user.id)
                db.session.add(tr)
            elif op == 'medicine_no_visit':
                mnv = MedicineNoVisit(animal_id=aid, prescribe_date=d, medicine_name=p1, dose_amount=float(p2 or 0), created_by_user_id=current_user.id)
                db.session.add(mnv)
            elif op == 'weight':
                m = Measurement(animal_id=aid, date=d, measurement_type=MeasurementType.WEIGHT, value=float(p1 or 0), unit='کیلوگرم', created_by_user_id=current_user.id)
                db.session.add(m)
            elif op == 'body_score':
                bs = BodyScore(animal_id=aid, date=d, score=float(p1 or 3.0), created_by_user_id=current_user.id)
                db.session.add(bs)
            elif op == 'hoof':
                h = HoofTrimming(
                    animal_id=aid, date=d,
                    front_left_status=HoofStatusEnum.HEALTHY, front_right_status=HoofStatusEnum.HEALTHY,
                    rear_left_status=HoofStatusEnum.HEALTHY, rear_right_status=HoofStatusEnum.HEALTHY,
                    created_by_user_id=current_user.id
                )
                db.session.add(h)
            count += 1

        db.session.commit()
        flash(f'تراکنش دسته جمعی شامل {count} عملیات با موفقیت ثبت شد.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در ثبت تراکنش دسته جمعی: {str(e)} - هیچ تغییری در پایگاه داده اعمال نشد.', 'danger')

    return redirect(url_for('bulk_operations.index'))
