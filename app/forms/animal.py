from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from app.forms.fields import JalaliDateField
from app.models.animal import Sex, Species, Origin, AnimalStatus

class AnimalForm(FlaskForm):
    plastic_tag = StringField('شماره پلاستیکی', validators=[DataRequired(message='شماره پلاستیکی الزامی است.')])
    serial_number = StringField('شماره سریال', validators=[DataRequired(message='شماره سریال الزامی است.')])
    national_id = StringField('شناسه ملی', validators=[Optional()])
    metal_tag = StringField('گوش فلزی', validators=[Optional()])
    birth_date = JalaliDateField('تاریخ تولد', validators=[DataRequired(message='تاریخ تولد الزامی است.')])
    sex = SelectField('جنسیت', choices=[('female', 'ماده'), ('male', 'نر')], validators=[DataRequired()])
    species = SelectField('گونه', choices=[('sheep', 'گوسفند'), ('goat', 'بز')], validators=[DataRequired()])
    breed = SelectField('نژاد', choices=[], validate_choice=False, validators=[Optional()])
    parity = IntegerField('تکرار بدن / شکم', default=0, validators=[Optional()])
    origin = SelectField('منشأ', choices=[('born_in_farm', 'متولد مزرعه'), ('purchased', 'خریداری شده')], validators=[DataRequired()])
    mother_id = SelectField('مادر', choices=[], coerce=int, validators=[Optional()])
    father_id = SelectField('پدر (دام)', choices=[], coerce=int, validators=[Optional()])
    father_sperm_id = SelectField('پدر (اسپرم)', choices=[], coerce=int, validators=[Optional()])
    current_pen_id = SelectField('بهاربند فعلی', choices=[], coerce=int, validators=[Optional()])
    birth_weight = FloatField('وزن تولد (کیلوگرم)', validators=[Optional()])
    notes = TextAreaField('توضیحات', validators=[Optional()])
    submit = SubmitField('ثبت دام')

class QuickRemovalForm(FlaskForm):
    status = SelectField('وضعیت جدید', choices=[('ready_for_removal', 'آماده حذف'), ('removed', 'حذف شده')], validators=[DataRequired()])
    removal_reason = StringField('دلیل تغییر وضعیت', validators=[Optional()])
    submit = SubmitField('بروزرسانی وضعیت')

class FullRemovalForm(FlaskForm):
    removal_date = JalaliDateField('تاریخ حذف', validators=[DataRequired(message='تاریخ حذف الزامی است.')])
    removal_group = SelectField('دلیل گروهی', choices=[], validate_choice=False, validators=[Optional()])
    removal_reason = StringField('دلیل دقیق حذف', validators=[DataRequired(message='دلیل دقیق حذف الزامی است.')])
    removal_form_number = StringField('شماره فرم / برگه خروج', validators=[Optional()])
    removal_buyer_name = StringField('نام خریدار / تحویل گیرنده', validators=[Optional()])
    submit = SubmitField('ثبت خروج / حذف دام')
