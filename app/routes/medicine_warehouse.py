from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.medicine_stock import Medicine, MedicineStock
from app.models.sperm import StockTransactionType
from app.models.admin import LookupItem
from app.forms.medicine import MedicineForm, MedicineTransactionForm
from app.services.jalali import from_jalali

bp = Blueprint('medicine_warehouse', __name__)

@bp.route('/medicine-warehouse')
@login_required
def list():
    medicines = Medicine.query.all()
    form = MedicineForm()
    form.category.choices = [(l.value, l.value) for l in LookupItem.query.filter_by(category='medicine_category').all()]
    tx_form = MedicineTransactionForm()
    recent_stocks = MedicineStock.query.order_by(MedicineStock.date.desc(), MedicineStock.id.desc()).limit(10).all()

    return render_template('medicine_warehouse/list.html', medicines=medicines, form=form, tx_form=tx_form, recent_stocks=recent_stocks)

@bp.route('/medicine-warehouse/new', methods=['POST'])
@login_required
def new():
    form = MedicineForm()
    form.category.choices = [(l.value, l.value) for l in LookupItem.query.filter_by(category='medicine_category').all()] + [(request.form.get('category'), request.form.get('category'))]

    if form.validate_on_submit():
        if Medicine.query.filter_by(name=form.name.data.strip()).first():
            flash('نام داروی وارد شده تکراری است.', 'danger')
            return redirect(url_for('medicine_warehouse.list'))

        med = Medicine(
            name=form.name.data.strip(),
            category=form.category.data,
            unit=form.unit.data.strip()
        )
        db.session.add(med)
        db.session.commit()
        flash('داروی جدید اضافه شد.', 'success')
    else:
        flash('خطا در ثبت دارو.', 'danger')

    return redirect(url_for('medicine_warehouse.list'))

@bp.route('/medicine-warehouse/<int:id>/transaction', methods=['POST'])
@login_required
def transaction(id):
    med = Medicine.query.get_or_404(id)
    tx_type_str = request.form.get('transaction_type', 'in')
    raw_date = request.form.get('date')
    d = from_jalali(raw_date) if raw_date else None
    qty = float(request.form.get('quantity', 0))

    if not d or qty <= 0:
        flash('اطلاعات تراکنش دارویی نامعتبر است.', 'danger')
        return redirect(url_for('medicine_warehouse.list'))

    tx_type = StockTransactionType.IN if tx_type_str == 'in' else StockTransactionType.OUT

    if tx_type == StockTransactionType.OUT and med.current_stock < qty:
        flash('موجودی انبار دارو برای این میزان خروج کافی نیست.', 'danger')
        return redirect(url_for('medicine_warehouse.list'))

    st = MedicineStock(
        medicine_id=med.id,
        date=d,
        transaction_type=tx_type,
        quantity=qty,
        supplier=request.form.get('supplier'),
        created_by_user_id=current_user.id
    )
    db.session.add(st)
    db.session.commit()
    flash('تراکنش دارویی ثبت شد.', 'success')
    return redirect(url_for('medicine_warehouse.list'))
