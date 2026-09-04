from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from app.forms.fields import JalaliDateField

class MeasurementForm(FlaskForm):
    date = JalaliDateField('تاریخ اندازه‌گیری', validators=[DataRequired()])
    measurement_type = SelectField('نوع اندازه‌گیری', choices=[
        ('weight', 'وزن'),
        ('body_temperature', 'دمای بدن'),
        ('body_length', 'طول بدن'),
        ('chest_girth', 'دور سینه'),
        ('withers_height', 'ارتفاع جدگاه'),
        ('sale_weight', 'وزن فروش')
    ], validators=[DataRequired()])
    value = FloatField('مقدار', validators=[DataRequired(message='مقدار الزامی است.')])
    unit = StringField('واحد', validators=[Optional()])
    submit = SubmitField('ثبت اندازه‌گیری')

class QuarterForm(FlaskForm):
    date = JalaliDateField('تاریخ ثبت', validators=[DataRequired()])
    quarter = SelectField('کارتیه (پستان)', choices=[
        ('front_left', 'جلو چپ'),
        ('front_right', 'جلو راست'),
        ('rear_left', 'عقب چپ'),
        ('rear_right', 'عقب راست')
    ], validators=[DataRequired()])
    issue_description = TextAreaField('شرح عارضه / وضعیت', validators=[Optional()])
    submit = SubmitField('ثبت وضعیت کارتیه')

class OneTimeEventForm(FlaskForm):
    date = JalaliDateField('تاریخ واقعه', validators=[DataRequired()])
    event_type = SelectField('نوع واقعه', choices=[], validate_choice=False, validators=[DataRequired(message='نوع واقعه الزامی است.')])
    description = TextAreaField('شرح واقعه', validators=[Optional()])
    submit = SubmitField('ثبت واقعه')

class BodyScoreForm(FlaskForm):
    date = JalaliDateField('تاریخ ارزیابی', validators=[DataRequired()])
    score = FloatField('نمره وضعیت بدنی (۱ تا ۵)', validators=[DataRequired(message='نمره بدنی الزامی است.')])
    submit = SubmitField('ثبت اسکور بدنی')

class MovementScoreForm(FlaskForm):
    date = JalaliDateField('تاریخ ارزیابی', validators=[DataRequired()])
    score = FloatField('نمره حرکتی (۱ تا ۵)', validators=[DataRequired(message='نمره حرکتی الزامی است.')])
    submit = SubmitField('ثبت اسکور حرکتی')

class SuggestedSpermForm(FlaskForm):
    date = JalaliDateField('تاریخ پیشنهادی', validators=[DataRequired()])
    parity_cycle = IntegerField('دوره / شکم', default=1, validators=[DataRequired()])
    sperm_1_id = SelectField('اسپرم اول (اولویت ۱)', choices=[], coerce=int, validators=[Optional()])
    sperm_2_id = SelectField('اسپرم دوم (اولویت ۲)', choices=[], coerce=int, validators=[Optional()])
    sperm_3_id = SelectField('اسپرم سوم (اولویت ۳)', choices=[], coerce=int, validators=[Optional()])
    sperm_4_id = SelectField('اسپرم چهارم (اولویت ۴)', choices=[], coerce=int, validators=[Optional()])
    submit = SubmitField('ثبت اسپرم پیشنهادی')

class HoofTrimmingForm(FlaskForm):
    date = JalaliDateField('تاریخ سم‌چینی', validators=[DataRequired()])
    front_left_status = SelectField('دست چپ', choices=[('healthy', 'سالم'), ('long', 'بلند'), ('problem', 'عارضه/بیماری')], validators=[DataRequired()])
    front_right_status = SelectField('دست راست', choices=[('healthy', 'سالم'), ('long', 'بلند'), ('problem', 'عارضه/بیماری')], validators=[DataRequired()])
    rear_left_status = SelectField('پای چپ', choices=[('healthy', 'سالم'), ('long', 'بلند'), ('problem', 'عارضه/بیماری')], validators=[DataRequired()])
    rear_right_status = SelectField('پای راست', choices=[('healthy', 'سالم'), ('long', 'بلند'), ('problem', 'عارضه/بیماری')], validators=[DataRequired()])
    submit = SubmitField('ثبت سم‌چینی')
