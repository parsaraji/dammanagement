from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from app.forms.fields import JalaliDateField

class SpermForm(FlaskForm):
    name = StringField('نام / عنوان اسپرم', validators=[DataRequired(message='نام اسپرم الزامی است.')])
    code = StringField('کد اسپرم', validators=[DataRequired(message='کد اسپرم الزامی است.')])
    breed = SelectField('نژاد', choices=[], validate_choice=False, validators=[Optional()])
    internal_reg_no = StringField('شماره ثبت داخلی', validators=[Optional()])
    external_reg_no = StringField('شماره ثبت بین‌المللی', validators=[Optional()])
    is_sexed = BooleanField('تعیین جنسیت شده (Sexed)', default=False)
    submit = SubmitField('ثبت اسپرم')

class SpermTransactionForm(FlaskForm):
    transaction_type = SelectField('نوع تراکنش', choices=[('in', 'ورود به انبار'), ('out', 'خروج از انبار')], validators=[DataRequired()])
    date = JalaliDateField('تاریخ تراکنش', validators=[DataRequired()])
    form_number = StringField('شماره برگه / حواله', validators=[Optional()])
    quantity = IntegerField('تعداد (پایِت)', validators=[DataRequired(message='تعداد الزامی است.')])
    description = TextAreaField('توضیحات', validators=[Optional()])
    submit = SubmitField('ثبت تراکنش')
