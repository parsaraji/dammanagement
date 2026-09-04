from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from app.forms.fields import JalaliDateField

class MedicineForm(FlaskForm):
    name = StringField('نام دارو / واکسن', validators=[DataRequired(message='نام دارو الزامی است.')])
    category = SelectField('دسته‌بندی', choices=[], validate_choice=False, validators=[Optional()])
    unit = StringField('واحد اندازه گیری', default='cc', validators=[DataRequired()])
    submit = SubmitField('ثبت دارو')

class MedicineTransactionForm(FlaskForm):
    transaction_type = SelectField('نوع تراکنش', choices=[('in', 'ورود به انبار'), ('out', 'خروج از انبار')], validators=[DataRequired()])
    date = JalaliDateField('تاریخ تراکنش', validators=[DataRequired()])
    quantity = FloatField('مقدار', validators=[DataRequired(message='مقدار الزامی است.')])
    invoice_number = StringField('شماره فاکتور / حواله', validators=[Optional()])
    supplier = StringField('تامین‌کننده / مصرف‌کننده', validators=[Optional()])
    consumed_for_animal_id = SelectField('مصرف برای دام (اختیاری)', choices=[], coerce=int, validators=[Optional()])
    submit = SubmitField('ثبت تراکنش دارویی')
