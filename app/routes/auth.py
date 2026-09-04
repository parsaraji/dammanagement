from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.forms.auth import LoginForm
from app.services.jalali import to_jalali
from datetime import datetime

bp = Blueprint('auth', __name__)

@bp.context_processor
def inject_context():
    return {'current_date_jalali': to_jalali(datetime.now().date())}

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data.strip()):
            if not user.is_active:
                flash('حساب کاربری شما غیرفعال است.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('نام کاربری یا رمز عبور اشتباه است.', 'danger')

    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('شما با موفقیت از سیستم خارج شدید.', 'info')
    return redirect(url_for('auth.login'))
