from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.sperm import Sperm, SpermTransaction, StockTransactionType
from app.models.admin import LookupItem
from app.forms.sperm import SpermForm, SpermTransactionForm
from app.services.jalali import from_jalali

bp = Blueprint('sperm_bank', __name__)

@bp.route('/sperm-bank')
@login_required
def list():
    sperms = Sperm.query.all()
    form = SpermForm()
    form.breed.choices = [(l.value, l.value) for l in LookupItem.query.filter_by(category='breed').all()]
    tx_form = SpermTransactionForm()
    recent_transactions = SpermTransaction.query.order_by(SpermTransaction.date.desc(), SpermTransaction.id.desc()).limit(10).all()

    return render_template('sperm_bank/list.html', sperms=sperms, form=form, tx_form=tx_form, recent_transactions=recent_transactions)

@bp.route('/sperm-bank/new', methods=['POST'])
@login_required
def new():
    form = SpermForm()
    form.breed.choices = [(l.value, l.value) for l in LookupItem.query.filter_by(category='breed').all()] + [(request.form.get('breed'), request.form.get('breed'))]

    if form.validate_on_submit():
        if Sperm.query.filter_by(code=form.code.data.strip()).first():
            flash('کد اسپرم وارد شده تکراری است.', 'danger')
            return redirect(url_for('sperm_bank.list'))

        sp = Sperm(
            name=form.name.data.strip(),
            code=form.code.data.strip(),
            breed=form.breed.data,
            is_sexed=form.is_sexed.data
        )
        db.session.add(sp)
        db.session.commit()
        flash('اسپرم جدید با موفقیت اضافه شد.', 'success')
    else:
        flash('خطا در ثبت اطلاعات اسپرم.', 'danger')

    return redirect(url_for('sperm_bank.list'))

@bp.route('/sperm-bank/<int:id>/transaction', methods=['POST'])
@login_required
def transaction(id):
    try:
        sperm = db.session.get(Sperm, id)
        if not sperm:
            flash('اسپرم یافت نشد.', 'danger')
            return redirect(url_for('sperm_bank.list'))

        tx_type_str = request.form.get('transaction_type', 'in')
        raw_date = request.form.get('date')
        try:
            d = from_jalali(raw_date) if raw_date else None
        except ValueError:
            flash('تاریخ شمسی وارد شده نامعتبر است.', 'danger')
            return redirect(url_for('sperm_bank.list'))

        try:
            qty = int(request.form.get('quantity', 0))
        except (ValueError, TypeError):
            qty = 0

        if not d or qty <= 0:
            flash('اطلاعات تراکنش یا مقدار وارد شده نامعتبر است.', 'danger')
            return redirect(url_for('sperm_bank.list'))

        tx_type = StockTransactionType.IN if tx_type_str == 'in' else StockTransactionType.OUT

        # Perform atomic inventory check
        if tx_type == StockTransactionType.OUT and sperm.stock_qty < qty:
            flash('موجودی اسپرم برای این میزان خروج کافی نیست.', 'danger')
            return redirect(url_for('sperm_bank.list'))

        tx = SpermTransaction(
            sperm_id=sperm.id,
            transaction_type=tx_type,
            date=d,
            quantity=qty,
            description=request.form.get('description'),
            created_by_user_id=current_user.id
        )

        if tx_type == StockTransactionType.IN:
            sperm.stock_qty += qty
        else:
            sperm.stock_qty -= qty

        db.session.add(tx)
        db.session.commit()
        flash('تراکنش با موفقیت ثبت شد و موجودی بروزرسانی گردید.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطا در ثبت تراکنش اسپرم: {str(e)}', 'danger')

    return redirect(url_for('sperm_bank.list'))
