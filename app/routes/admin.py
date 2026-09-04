from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.admin import LookupItem, ProgramSettings, Staff
from app.models.user import User, UserRole
from app.forms.admin import LookupItemForm, ProgramSettingsForm, StaffForm, UserForm
from app.services.decorators import roles_required

bp = Blueprint('admin', __name__)

@bp.route('/admin/defaults', methods=['GET', 'POST'])
@login_required
def defaults():
    form = LookupItemForm()
    if form.validate_on_submit():
        item = LookupItem(category=form.category.data, value=form.value.data.strip())
        db.session.add(item)
        try:
            db.session.commit()
            flash('مقدار پیش‌فرض با موفقیت ثبت شد.', 'success')
        except Exception:
            db.session.rollback()
            flash('این مقدار قبلاً در این دسته‌بندی ثبت شده است.', 'warning')
        return redirect(url_for('admin.defaults'))

    items = LookupItem.query.order_by(LookupItem.category, LookupItem.value).all()
    return render_template('admin/defaults.html', form=form, items=items)

@bp.route('/admin/defaults/<int:id>/delete', methods=['POST'])
@login_required
def delete_lookup(id):
    item = LookupItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('مقدار پیش‌فرض حذف گردید.', 'info')
    return redirect(url_for('admin.defaults'))

@bp.route('/admin/program-settings', methods=['GET', 'POST'])
@login_required
def program_settings():
    form = ProgramSettingsForm()
    if request.method == 'GET':
        s1 = ProgramSettings.query.filter_by(key='min_milk_records').first()
        s2 = ProgramSettings.query.filter_by(key='max_gap_days').first()
        s3 = ProgramSettings.query.filter_by(key='default_pregnancy_days').first()

        form.min_milk_records.data = s1.value if s1 else '3'
        form.max_gap_days.data = s2.value if s2 else '10'
        form.default_pregnancy_days.data = s3.value if s3 else '150'

    if form.validate_on_submit():
        for key, val in [('min_milk_records', form.min_milk_records.data),
                          ('max_gap_days', form.max_gap_days.data),
                          ('default_pregnancy_days', form.default_pregnancy_days.data)]:
            s = ProgramSettings.query.filter_by(key=key).first()
            if not s:
                s = ProgramSettings(key=key)
            s.value = val
            db.session.add(s)

        db.session.commit()
        flash('تنظیمات برنامه با موفقیت ذخیره شد.', 'success')
        return redirect(url_for('admin.program_settings'))

    return render_template('admin/program_settings.html', form=form)

@bp.route('/admin/staff', methods=['GET', 'POST'])
@login_required
def staff():
    form = StaffForm()
    if form.validate_on_submit():
        st = Staff(
            full_name=form.full_name.data.strip(),
            role=form.role.data,
            phone=form.phone.data,
            is_active=form.is_active.data
        )
        db.session.add(st)
        db.session.commit()
        flash('پرونده پرسنلی با موفقیت ثبت شد.', 'success')
        return redirect(url_for('admin.staff'))

    staff_members = Staff.query.all()
    return render_template('admin/staff.html', form=form, staff_members=staff_members)

@bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def users():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
        if form.password.data:
            user.set_password(form.password.data.strip())
        user.full_name = form.full_name.data
        user.role = UserRole[form.role.data.upper()]
        user.is_active = form.is_active.data

        db.session.add(user)
        db.session.commit()
        flash('کاربر با موفقیت ثبت / ذخیره گردید.', 'success')
        return redirect(url_for('admin.users'))

    users_list = User.query.all()
    return render_template('admin/users.html', form=form, users=users_list)

@bp.route('/admin/support')
@login_required
def support():
    return render_template('admin/support.html')

@bp.route('/admin/server-connection', methods=['GET', 'POST'])
@login_required
def server_connection():
    if request.method == 'POST':
        flash('تنظیمات اتصال به سرور مرکزی ذخیره شد.', 'success')
        return redirect(url_for('admin.server_connection'))
    return render_template('admin/server_connection.html')
