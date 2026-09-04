from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SelectField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional
from app.forms.fields import JalaliDateField

class MilkRecordForm(FlaskForm):
    date = JalaliDateField('تاریخ رکوردگیری', validators=[DataRequired()])
    record_type = SelectField('نوع رکورد', choices=[('official', 'رسمی'), ('unofficial', 'غیررسمی')], validators=[DataRequired()])
    parity_cycle = IntegerField('شکم / دوره', default=1, validators=[DataRequired()])

    milking1_time = StringField('زمان نوبت ۱', validators=[Optional()])
    milking1_amount = FloatField('مقدار نوبت ۱ (کیلوگرم)', default=0.0, validators=[Optional()])

    milking2_time = StringField('زمان نوبت ۲', validators=[Optional()])
    milking2_amount = FloatField('مقدار نوبت ۲ (کیلوگرم)', default=0.0, validators=[Optional()])

    milking3_time = StringField('زمان نوبت ۳', validators=[Optional()])
    milking3_amount = FloatField('مقدار نوبت ۳ (کیلوگرم)', default=0.0, validators=[Optional()])

    fat_percent = FloatField('درصد چربی', validators=[Optional()])
    protein_percent = FloatField('درصد پروتئین', validators=[Optional()])

    submit = SubmitField('ثبت رکورد شیر')

class BulkMilkUploadForm(FlaskForm):
    excel_file = FileField('فایل اکسل رکوردها (.xlsx)', validators=[
        FileRequired(message='لطفاً فایل اکسل را انتخاب کنید.'),
        FileAllowed(['xlsx'], message='فقط فایل‌های اکسل با پسوند .xlsx مجاز هستند.')
    ])
    submit = SubmitField('آپلود و پردازش فایل')
