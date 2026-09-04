from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, IntegerField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional
from app.forms.fields import JalaliDateField

class TreatmentReproductionForm(FlaskForm):
    visit_type = SelectField('نوع ویزیت', choices=[('medical', 'درمانی / عمومی'), ('reproductive', 'تولیدمثلی')], validators=[DataRequired()])
    date = JalaliDateField('تاریخ ویزیت', validators=[DataRequired(message='تاریخ ویزیت الزامی است.')])
    time = StringField('ساعت', validators=[Optional()])
    doctor = StringField('دامپزشک', validators=[Optional()])
    visit_reason = StringField('علت ویزیت', validators=[Optional()])
    diagnosis = TextAreaField('تشخیص', validators=[Optional()])
    notes = TextAreaField('توضیحات و درمان', validators=[Optional()])
    treatment_end_date = JalaliDateField('تاریخ پایان درمان', validators=[Optional()])
    submit = SubmitField('ثبت ویزیت / درمان')

class MedicineNoVisitForm(FlaskForm):
    prescribe_date = JalaliDateField('تاریخ تجویز', validators=[DataRequired()])
    consume_date = JalaliDateField('تاریخ مصرف', validators=[DataRequired()])
    medicine_name = StringField('نام دارو', validators=[DataRequired(message='نام دارو الزامی است.')])
    dose_amount = FloatField('مقدار دوز', validators=[Optional()])
    dose_unit = StringField('واحد دوز (cc / گرم)', default='cc', validators=[Optional()])
    consumption_method = StringField('روش مصرف (تزریقی/خوراکی)', validators=[Optional()])
    consume_time = StringField('زمان مصرف', validators=[Optional()])
    is_recurring = BooleanField('مصرف دوره ای / تکرارشونده', default=False)
    recurrence_days = IntegerField('تعداد روزهای تکرار', validators=[Optional()])
    recurrence_interval = IntegerField('فاصله تکرار (روز)', validators=[Optional()])
    submit = SubmitField('ثبت مصرف دارو')

class VaccinationForm(FlaskForm):
    date = JalaliDateField('تاریخ تزریق واکسن', validators=[DataRequired()])
    dose_number = StringField('شماره دوز (نوبت)', validators=[Optional()])
    vaccine_name = SelectField('نام واکسن', choices=[], validate_choice=False, validators=[DataRequired(message='انتخاب نام واکسن الزامی است.')])
    agent_name = StringField('واکسیناتور / مأمور', validators=[Optional()])
    submit = SubmitField('ثبت واکسیناسیون')
