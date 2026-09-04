from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.animal import Animal, AnimalStatus, Sex, Species
from app.models.pen import Pen
from app.models.medical import Vaccination
from app.models.reproduction import CIDR
from app.models.measurement import Measurement, MeasurementType, HoofTrimming, HoofStatusEnum
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
    d = from_jalali(request.form.get('date'))
    detail = request.form.get('detail', '')

    count = 0
    for aid in working_ids:
        if op_type == 'vaccination':
            v = Vaccination(animal_id=aid, date=d, vaccine_name=detail or 'واکسن عمومی', created_by_user_id=current_user.id)
            db.session.add(v)
            count += 1
        elif op_type == 'mark_removal':
            a = Animal.query.get(aid)
            if a:
                a.status = AnimalStatus.READY_FOR_REMOVAL
                a.removal_reason = detail
                count += 1
        elif op_type == 'cidr':
            c = CIDR(animal_id=aid, insert_date=d, notes=detail, created_by_user_id=current_user.id)
            db.session.add(c)
            count += 1

    db.session.commit()
    flash(f'عملیات سریع روی {count} دام با موفقیت اعمال گردید.', 'success')
    return redirect(url_for('bulk_operations.index'))

@bp.route('/bulk-operations/batch-submit', methods=['POST'])
@login_required
def batch_submit():
    animal_ids = request.form.getlist('animal_id[]')
    actions = request.form.getlist('action[]')
    dates = request.form.getlist('date[]')
    vals = request.form.getlist('val[]')

    try:
        count = 0
        for i, aid in enumerate(animal_ids):
            act = actions[i] if i < len(actions) else 'none'
            if act == 'none':
                continue
            raw_d = dates[i] if i < len(dates) else None
            d = from_jalali(raw_d) if raw_d else None
            val_str = vals[i] if i < len(vals) else ''

            if act == 'vaccine':
                v = Vaccination(animal_id=int(aid), date=d, vaccine_name=val_str or 'واکسن انتروتوکسمی', created_by_user_id=current_user.id)
                db.session.add(v)
            elif act == 'weight':
                m = Measurement(animal_id=int(aid), date=d, measurement_type=MeasurementType.WEIGHT, value=float(val_str or 0), unit='کیلوگرم', created_by_user_id=current_user.id)
                db.session.add(m)
            elif act == 'hoof':
                h = HoofTrimming(animal_id=int(aid), date=d, front_left_status=HoofStatusEnum.HEALTHY, front_right_status=HoofStatusEnum.HEALTHY, rear_left_status=HoofStatusEnum.HEALTHY, rear_right_status=HoofStatusEnum.HEALTHY, created_by_user_id=current_user.id)
                db.session.add(h)
            count += 1

        db.session.commit()
        flash(f'تراکنش دسته جمعی شامل {count} عملیات با موفقیت ثبت شد.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در ثبت تراکنش دسته جمعی: {str(e)} - هیچ تغییری اعمال نشد.', 'danger')

    return redirect(url_for('bulk_operations.index'))
