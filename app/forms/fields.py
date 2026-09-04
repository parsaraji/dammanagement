from wtforms import StringField, ValidationError
from app.services.jalali import from_jalali, to_jalali, normalize_digits

class JalaliDateField(StringField):
    """WTForms field for Jalali date input, converting to/from Python datetime.date."""
    def __init__(self, label=None, validators=None, **kwargs):
        super(JalaliDateField, self).__init__(label, validators, **kwargs)
        self.data = None

    def _value(self):
        if self.data:
            return to_jalali(self.data)
        return ""

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            raw_val = normalize_digits(valuelist[0])
            if not raw_val:
                self.data = None
                return
            try:
                self.data = from_jalali(raw_val)
            except ValueError as e:
                self.data = None
                raise ValidationError(str(e))
        else:
            self.data = None
