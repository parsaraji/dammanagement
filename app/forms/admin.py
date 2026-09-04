from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Optional

class LookupItemForm(FlaskForm):
    category = SelectField('دسته‌بندی', choices=[
        ('breed', 'نژاد'),
        ('color', 'رنگ'),
        ('removal_reason', 'علت حذف'),
        ('vaccine_type', 'نوع واکسن'),
        ('medicine_category', 'دسته‌بندی دارو'),
        ('event_type', 'نوع واقعه')
    ], validators=[DataRequired()])
    value = StringField('عنوان / مقدار', validators=[DataRequired(message='مقدار الزامی است.')])
    submit = SubmitField('افزودن به مقادیر پیش‌فرض')

class ProgramSettingsForm(FlaskForm):
    min_milk_records = StringField('حداقل تعداد رکوردهای شیر برای محاسبه استاندارد', validators=[DataRequired()])
    max_gap_days = StringField('حداکثر فاصله مجاز بین دو رکورد شیر (روز)', validators=[DataRequired()])
    default_pregnancy_days = StringField('طول دوره بارداری فرض شده (روز)', validators=[DataRequired()])
    submit = SubmitField('ذخیره تنظیمات')

class StaffForm(FlaskForm):
    full_name = StringField('نام و نام خانوادگی', validators=[DataRequired(message='نام الزامی است.')])
    role = StringField('سمت / مسئولیت', validators=[Optional()])
    phone = StringField('شماره تماس', validators=[Optional()])
    is_active = BooleanField('فعال', default=True)
    submit = SubmitField('ثبت پرسنل')

class UserForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired(message='نام کاربری الزامی است.')])
    password = PasswordField('رمز عبور (در صورت نیاز به تغییر وارد کنید)', validators=[Optional()])
    full_name = StringField('نام کامل', validators=[Optional()])
    role = SelectField('نقش کاربر', choices=[
        ('admin', 'مدیر سیستم (Admin)'),
        ('vet', 'دامپزشک (Vet)'),
        ('breeding_specialist', 'کارشناس اصلاح نژاد (Breeder)'),
        ('data_entry', 'اپراتور ثبت داده (Data Entry)')
    ], validators=[DataRequired()])
    is_active = BooleanField('حساب فعال است', default=True)
    submit = SubmitField('ثبت کاربر')
