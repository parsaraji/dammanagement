from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from app.extensions import db
from app.models.animal import Animal, AnimalStatus, Sex, Species, Origin
from app.models.pen import Pen
from app.models.sperm import Sperm
from app.models.admin import LookupItem
from app.models.reproduction import Insemination
from app.models.measurement import Measurement
from app.models.milk import MilkRecord
from app.forms.animal import AnimalForm, QuickRemovalForm, FullRemovalForm
from app.services.jalali import normalize_digits, from_jalali, to_jalali
from app.services.pdf_service import generate_qr_code_base64
from app.services.pedigree_service import calculate_inbreeding_coefficient, calculate_blood_purity, build_tree_node

bp = Blueprint('animals', __name__)

@bp.route('/animals')
@login_required
def list():
    animals = Animal.query.order_by(Animal.id.desc()).all()
    form = AnimalForm()

    # Populate dynamic select choices
    form.breed.choices = [(l.value, l.value) for l in LookupItem.query.filter_by(category='breed').all()]
    form.current_pen_id.choices = [(0, '--- انتخاب بهاربند ---')] + [(p.id, p.name) for p in Pen.query.all()]
    form.mother_id.choices = [(0, '--- بدون مادر ---')] + [(a.id, f"{a.plastic_tag} ({a.serial_number})") for a in Animal.query.filter_by(sex=Sex.FEMALE).all()]
    form.father_id.choices = [(0, '--- بدون پدر (دام) ---')] + [(a.id, f"{a.plastic_tag} ({a.serial_number})") for a in Animal.query.filter_by(sex=Sex.MALE).all()]
    form.father_sperm_id.choices = [(0, '--- بدون پدر (اسپرم) ---')] + [(s.id, f"{s.code} - {s.name}") for s in Sperm.query.all()]

    return render_template('animals/list.html', animals=animals, form=form)

@bp.route('/animals/new', methods=['POST'])
@login_required
def new():
    form = AnimalForm()
    # Re-assign choices for validation
    form.breed.choices = [(l.value, l.value) for l in LookupItem.query.filter_by(category='breed').all()] + [(request.form.get('breed'), request.form.get('breed'))]
    form.current_pen_id.choices = [(0, '---')] + [(p.id, p.name) for p in Pen.query.all()]
    form.mother_id.choices = [(0, '---')] + [(a.id, a.plastic_tag) for a in Animal.query.all()]
    form.father_id.choices = [(0, '---')] + [(a.id, a.plastic_tag) for a in Animal.query.all()]
    form.father_sperm_id.choices = [(0, '---')] + [(s.id, s.name) for s in Sperm.query.all()]

    if form.validate_on_submit():
        plastic_tag = normalize_digits(form.plastic_tag.data)
        serial_number = normalize_digits(form.serial_number.data)

        if Animal.query.filter_by(plastic_tag=plastic_tag).first():
            return jsonify({'success': False, 'message': 'شماره پلاستیکی وارد شده تکراری است.'})
        if Animal.query.filter_by(serial_number=serial_number).first():
            return jsonify({'success': False, 'message': 'شماره سریال وارد شده تکراری است.'})

        pen_id = form.current_pen_id.data if form.current_pen_id.data != 0 else None
        mother_id = form.mother_id.data if form.mother_id.data != 0 else None
        father_id = form.father_id.data if form.father_id.data != 0 else None
        father_sperm_id = form.father_sperm_id.data if form.father_sperm_id.data != 0 else None

        species_enum = Species[form.species.data.upper()]

        if mother_id:
            m_obj = db.session.get(Animal, mother_id)
            if not m_obj or m_obj.sex != Sex.FEMALE:
                return jsonify({'success': False, 'message': 'مادر انتخاب شده باید دام ماده باشد.'})
            if m_obj.species != species_enum:
                return jsonify({'success': False, 'message': 'گونه مادر و فرزند مطابقت ندارد.'})

        if father_id:
            f_obj = db.session.get(Animal, father_id)
            if not f_obj or f_obj.sex != Sex.MALE:
                return jsonify({'success': False, 'message': 'پدر انتخاب شده باید دام نر باشد.'})
            if f_obj.species != species_enum:
                return jsonify({'success': False, 'message': 'گونه پدر و فرزند مطابقت ندارد.'})

        animal = Animal(
            plastic_tag=plastic_tag,
            serial_number=serial_number,
            national_id=normalize_digits(form.national_id.data),
            metal_tag=normalize_digits(form.metal_tag.data),
            birth_date=form.birth_date.data,
            sex=Sex[form.sex.data.upper()],
            species=Species[form.species.data.upper()],
            breed=form.breed.data,
            parity=form.parity.data or 0,
            origin=Origin[form.origin.data.upper()],
            mother_id=mother_id,
            father_id=father_id,
            father_sperm_id=father_sperm_id,
            current_pen_id=pen_id,
            birth_weight=form.birth_weight.data,
            notes=form.notes.data,
            status=AnimalStatus.ALIVE
        )
        db.session.add(animal)
        db.session.flush()

        # Link to calving offspring if calving_id provided
        calving_id_raw = request.form.get('calving_id')
        if calving_id_raw and calving_id_raw.isdigit():
            from app.models.reproduction import CalvingOffspring
            co = CalvingOffspring(calving_id=int(calving_id_raw), animal_id=animal.id)
            db.session.add(co)

        db.session.commit()
        return jsonify({'success': True, 'message': 'دام با موفقیت ثبت شد.', 'reload': True})

    errors = {field: [str(err) for err in errs] for field, errs in form.errors.items()}
    return jsonify({'success': False, 'errors': errors})

@bp.route('/animals/search-quick')
@login_required
def search_quick():
    q = normalize_digits(request.args.get('q', '')).strip()
    animal = Animal.query.filter((Animal.plastic_tag == q) | (Animal.serial_number == q)).first()
    if animal:
        return redirect(url_for('animals.detail', id=animal.id))
    flash('دامی با این شماره پلاستیکی یا سریال پیدا نشد.', 'warning')
    return redirect(url_for('animals.list'))

@bp.route('/animals/<int:id>')
@login_required
def detail(id):
    animal = Animal.query.get_or_404(id)
    pedigree_tree = build_tree_node(animal)
    inbreeding_coeff = calculate_inbreeding_coefficient(animal)
    blood_purity = calculate_blood_purity(animal)
    sperms = Sperm.query.all()

    return render_template('animals/detail.html',
                           animal=animal,
                           pedigree_tree=pedigree_tree,
                           inbreeding_coeff=inbreeding_coeff,
                           blood_purity=blood_purity,
                           sperms=sperms,
                           Insemination=Insemination,
                           Measurement=Measurement,
                           MilkRecord=MilkRecord)

@bp.route('/animals/<int:id>/ready-for-removal', methods=['POST'])
@login_required
def ready_for_removal(id):
    animal = Animal.query.get_or_404(id)
    status_str = request.form.get('status', 'ready_for_removal')
    reason = request.form.get('removal_reason', '')

    if status_str == 'ready_for_removal':
        animal.status = AnimalStatus.READY_FOR_REMOVAL
    elif status_str == 'alive':
        animal.status = AnimalStatus.ALIVE

    animal.removal_reason = reason
    db.session.commit()
    return jsonify({'success': True, 'message': 'وضعیت دام با موفقیت بروزرسانی شد.', 'reload': True})

@bp.route('/animals/<int:id>/remove', methods=['POST'])
@login_required
def remove(id):
    animal = Animal.query.get_or_404(id)
    raw_date = request.form.get('removal_date')
    rem_date = from_jalali(raw_date) if raw_date else None

    animal.status = AnimalStatus.REMOVED
    animal.removal_date = rem_date
    animal.removal_reason = request.form.get('removal_reason')
    animal.removal_form_number = request.form.get('removal_form_number')
    animal.removal_buyer_name = request.form.get('removal_buyer_name')

    db.session.commit()
    return jsonify({'success': True, 'message': 'حذف قطعی دام با موفقیت ثبت شد.', 'reload': True})

@bp.route('/animals/female-status')
@login_required
def female_status():
    females = Animal.query.filter_by(sex=Sex.FEMALE, status=AnimalStatus.ALIVE).all()
    female_data = []
    for f in females:
        last_insem = f.inseminations.order_by(Insemination.date.desc()).first()
        is_pregnant = last_insem.led_to_pregnancy if last_insem else False
        f.last_insem = last_insem
        f.is_pregnant = is_pregnant
        female_data.append(f)

    return render_template('animals/female_status.html', females=female_data)

@bp.route('/animals/<int:id>/id-card')
@login_required
def id_card(id):
    animal = Animal.query.get_or_404(id)
    qr_b64 = generate_qr_code_base64(animal.plastic_tag)
    current_date_jalali = to_jalali(request.args.get('date') or None) or '1402/08/15'
    return render_template('animals/id_card.html', animal=animal, qr_b64=qr_b64, current_date_jalali=current_date_jalali)

@bp.route('/animals/<int:id>/id-card.pdf')
@login_required
def id_card_pdf(id):
    return redirect(url_for('animals.id_card', id=id))
