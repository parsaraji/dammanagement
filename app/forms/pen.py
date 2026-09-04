from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional
from app.forms.fields import JalaliDateField

class PenForm(FlaskForm):
    name = StringField('نام بهاربند', validators=[DataRequired(message='نام بهاربند الزامی است.')])
    code = StringField('کد بهاربند', validators=[DataRequired(message='کد بهاربند الزامی است.')])
    capacity = IntegerField('ظرفیت (رأس)', default=0, validators=[DataRequired()])
    pen_type = SelectField('نوع بهاربند', choices=[
        ('زایمان', 'زایمان'),
        ('پرواربندی', 'پرواربندی'),
        ('نگهداری', 'نگهداری / عمومی'),
        ('قرنطینه', 'قرنطینه'),
        ('بیمارستان', 'بیمارستان')
    ], validators=[DataRequired()])
    notes = TextAreaField('توضیحات', validators=[Optional()])
    submit = SubmitField('ثبت بهاربند')

class PenMovementForm(FlaskForm):
    date = JalaliDateField('تاریخ جابجایی', validators=[DataRequired()])
    animal_id = SelectField('دام', choices=[], coerce=int, validators=[DataRequired(message='انتخاب دام الزامی است.')])
    to_pen_id = SelectField('بهاربند مقصد', choices=[], coerce=int, validators=[DataRequired(message='انتخاب بهاربند مقصد الزامی است.')])
    reason = StringField('علت جابجایی', validators=[Optional()])
    submit = SubmitField('ثبت جابجایی')
