from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.animal import Animal, AnimalStatus, Sex, Species
from app.models.logistics import HerdComposition
from app.services.jalali import from_jalali
from app.services.herd_composition_service import calculate_herd_composition
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
    try:
        d = from_jalali(raw_d) if raw_d else datetime.now().date()
    except Exception:
        d = datetime.now().date()

    comp = calculate_herd_composition(d)

    hc = HerdComposition.query.filter_by(date=d).first()
    if not hc:
        hc = HerdComposition(date=d)

    hc.male_count = comp['male_count']
    hc.female_count = comp['female_count']
    hc.lamb_count = comp['lamb_count']
    hc.pregnant_count = comp['pregnant_count']
    hc.lactating_count = comp['lactating_count']
    hc.dry_count = comp['dry_count']
    hc.total_count = comp['total_count']
    hc.notes = f'محاسبه دقیق سیستمی در تاریخ {raw_d or "امروز"}'
    hc.created_by_user_id = current_user.id

    db.session.add(hc)
    db.session.commit()
    flash('ترکیب گله بر اساس داده‌های واقعی با موفقیت محاسبه و ثبت شد.', 'success')
    return redirect(url_for('herd_composition.index'))
