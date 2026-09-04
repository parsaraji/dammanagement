from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional
from app.forms.fields import JalaliDateField

class CIDRForm(FlaskForm):
    insert_date = JalaliDateField('تاریخ سیدرگذاری', validators=[DataRequired(message='تاریخ سیدرگذاری الزامی است.')])
    remove_date = JalaliDateField('تاریخ خارج کردن سیدر', validators=[Optional()])
    cidr_type = StringField('نوع سیدر', validators=[Optional()])
    cidr_number = StringField('شماره سیدر', validators=[Optional()])
    notes = TextAreaField('توضیحات', validators=[Optional()])
    submit = SubmitField('ثبت سیدرگذاری')

class InseminationForm(FlaskForm):
    date = JalaliDateField('تاریخ تلقیح', validators=[DataRequired(message='تاریخ تلقیح الزامی است.')])
    time = StringField('زمان / ساعت', validators=[Optional()])
    insemination_type = SelectField('نوع تلقیح', choices=[('artificial', 'مصنوعی'), ('natural', 'طبیعی')], validators=[DataRequired()])
    sperm_id = SelectField('اسپرم (تلقیح مصنوعی)', choices=[], coerce=int, validators=[Optional()])
    sire_animal_id = SelectField('پدر نر (جفت‌گیری طبیعی)', choices=[], coerce=int, validators=[Optional()])
    parity_cycle = IntegerField('دوره شیرواری / شکم', default=1, validators=[DataRequired()])
    led_to_pregnancy = BooleanField('منجر به آبستنی شد', default=False)
    notes = TextAreaField('توضیحات', validators=[Optional()])
    submit = SubmitField('ثبت تلقیح')

class HeatNoInseminationForm(FlaskForm):
    date = JalaliDateField('تاریخ فحلی', validators=[DataRequired(message='تاریخ فحلی الزامی است.')])
    time = StringField('ساعت', validators=[Optional()])
    heat_symptoms = StringField('علائم فحلی', validators=[Optional()])
    heat_detector = StringField('فحلی یاب / مامور', validators=[Optional()])
    heat_description = TextAreaField('توضیحات', validators=[Optional()])
    next_visit_date = JalaliDateField('تاریخ ویزیت بعدی', validators=[Optional()])
    doctor = StringField('دامپزشک', validators=[Optional()])
    visit_reason = StringField('دلیل ویزیت', validators=[Optional()])
    submit = SubmitField('ثبت فحلی بدون تلقیح')

class DryOffForm(FlaskForm):
    start_date = JalaliDateField('تاریخ شروع خشکی', validators=[DataRequired(message='تاریخ شروع خشکی الزامی است.')])
    end_date = JalaliDateField('تاریخ پایان خشکی', validators=[Optional()])
    notes = TextAreaField('توضیحات', validators=[Optional()])
    submit = SubmitField('ثبت خشکی')

class CalvingForm(FlaskForm):
    date = JalaliDateField('تاریخ زایش', validators=[DataRequired(message='تاریخ زایش الزامی است.')])
    calving_type = SelectField('نوع زایش', choices=[
        ('normal', 'طبیعی / زایمان آسان'),
        ('difficult', 'سخت‌زایی'),
        ('abortion', 'سقط جنین'),
        ('stillbirth', 'مرده‌زایی')
    ], validators=[DataRequired()])
    factors = StringField('عوامل منجر به سقط/مرده‌زایی', validators=[Optional()])
    offspring_count = IntegerField('تعداد بره / بزغاله', default=1, validators=[DataRequired()])
    submit = SubmitField('ثبت زایش')
