from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.animal import Animal, AnimalStatus, Sex, Species
from app.models.logistics import HerdComposition
from app.models.reproduction import Insemination
from app.services.jalali import from_jalali
from datetime import datetime

bp = Blueprint('herd_composition', __name__)

@bp.route('/herd-composition')
@login_required
def index():
    latest = HerdComposition.query.order_by(HerdComposition.date.desc()).first()
    history = HerdComposition.query.order_by(HerdComposition.date.desc()).all()
    return render_template('herd_composition/index.html', latest=latest, history=history)

@bp.route('/herd-composition/recalculate', methods=['POST'])
@login_required
def recalculate():
    raw_d = request.form.get('date')
    d = from_jalali(raw_d) if raw_d else datetime.now().date()

    males = Animal.query.filter_by(status=AnimalStatus.ALIVE, sex=Sex.MALE).count()
    females = Animal.query.filter_by(status=AnimalStatus.ALIVE, sex=Sex.FEMALE).count()
    total = males + females

    # Rough age / status calculations
    pregnant = Insemination.query.filter_by(led_to_pregnancy=True).distinct(Insemination.animal_id).count()

    hc = HerdComposition.query.filter_by(date=d).first()
    if not hc:
        hc = HerdComposition(date=d)

    hc.male_count = males
    hc.female_count = females
    hc.lamb_count = max(0, total - (males + females))
    hc.pregnant_count = pregnant
    hc.lactating_count = max(0, females - pregnant)
    hc.dry_count = 0
    hc.total_count = total
    hc.notes = f'محاسبه سیستمی در تاریخ {raw_d}'
    hc.created_by_user_id = current_user.id

    db.session.add(hc)
    db.session.commit()
    flash('ترکیب گله با موفقیت محاسبه و ثبت شد.', 'success')
    return redirect(url_for('herd_composition.index'))
