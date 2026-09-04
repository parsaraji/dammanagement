from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.pen import Pen
from app.models.animal import Animal, AnimalStatus
from app.models.logistics import PenMovement
from app.forms.pen import PenForm, PenMovementForm
from app.services.jalali import from_jalali

bp = Blueprint('pens', __name__)

@bp.route('/pens')
@login_required
def list():
    pens = Pen.query.all()
    form = PenForm()
    move_form = PenMovementForm()
    move_form.animal_id.choices = [(a.id, f"{a.plastic_tag} ({a.serial_number})") for a in Animal.query.filter_by(status=AnimalStatus.ALIVE).all()]
    move_form.to_pen_id.choices = [(p.id, p.name) for p in pens]

    return render_template('pens/list.html', pens=pens, form=form, move_form=move_form)

@bp.route('/pens/new', methods=['POST'])
@login_required
def new():
    form = PenForm()
    if form.validate_on_submit():
        if Pen.query.filter_by(code=form.code.data.strip()).first():
            flash('کد بهاربند تکراری است.', 'danger')
            return redirect(url_for('pens.list'))

        pen = Pen(
            name=form.name.data.strip(),
            code=form.code.data.strip(),
            capacity=form.capacity.data or 0,
            pen_type=form.pen_type.data,
            notes=form.notes.data
        )
        db.session.add(pen)
        db.session.commit()
        flash('بهاربند جدید با موفقیت اضافه شد.', 'success')
    else:
        flash('خطا در ثبت بهاربند. لطفاً اطلاعات را بررسی کنید.', 'danger')

    return redirect(url_for('pens.list'))

@bp.route('/pens/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    pen = Pen.query.get_or_404(id)
    if pen.animals.count() > 0:
        flash('امکان حذف بهاربندی که دام در آن قرار دارد وجود ندارد. لطفاً ابتدا دام‌ها را منتقل کنید.', 'danger')
        return redirect(url_for('pens.list'))

    db.session.delete(pen)
    db.session.commit()
    flash('بهاربند با موفقیت حذف شد.', 'info')
    return redirect(url_for('pens.list'))

@bp.route('/pen-movements', methods=['POST'])
@login_required
def move():
    move_form = PenMovementForm()
    move_form.animal_id.choices = [(a.id, a.plastic_tag) for a in Animal.query.all()]
    move_form.to_pen_id.choices = [(p.id, p.name) for p in Pen.query.all()]

    if move_form.validate_on_submit():
        animal = Animal.query.get(move_form.animal_id.data)
        if animal:
            old_pen_id = animal.current_pen_id
            animal.current_pen_id = move_form.to_pen_id.data

            pm = PenMovement(
                animal_id=animal.id,
                date=move_form.date.data,
                from_pen_id=old_pen_id,
                to_pen_id=move_form.to_pen_id.data,
                reason=move_form.reason.data,
                created_by_user_id=current_user.id
            )
            db.session.add(pm)
            db.session.commit()
            flash('جابجایی دام با موفقیت ثبت گردید.', 'success')
    else:
        flash('خطا در ثبت جابجایی دام.', 'danger')

    return redirect(url_for('pens.list'))
