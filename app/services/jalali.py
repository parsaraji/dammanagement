import re
from datetime import date, datetime
import jdatetime

PERSIAN_DIGITS = '۰۱۲۳۴۵۶۷۸۹'
ARABIC_DIGITS = '٠١٢٣٤٥٦٧٨٩'
ASCII_DIGITS = '0123456789'

PERSIAN_TO_ASCII = str.maketrans(PERSIAN_DIGITS + ARABIC_DIGITS, ASCII_DIGITS * 2)

def normalize_digits(s: str) -> str:
    """Converts Persian and Arabic digits in a string to standard ASCII digits."""
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    return s.translate(PERSIAN_TO_ASCII).strip()

def to_jalali(val, fmt='%Y/%m/%d') -> str:
    """Converts a Gregorian date or datetime object to a Jalali formatted string."""
    if not val:
        return ""
    if isinstance(val, datetime):
        val = val.date()
    if isinstance(val, date):
        try:
            j_date = jdatetime.date.fromgregorian(date=val)
            return j_date.strftime(fmt)
        except Exception:
            return ""
    return str(val)

def from_jalali(j_str: str) -> date:
    """Parses a Jalali date string (e.g., '1402/08/15') into a Gregorian datetime.date object."""
    if not j_str:
        return None
    j_str = normalize_digits(j_str)
    # Match dates separated by /, -, or .
    parts = re.split(r'[/.-]', j_str)
    if len(parts) != 3:
        raise ValueError("فرمت تاریخ شمسی نامعتبر است. استفاده از YYYY/MM/DD الزامی است.")
    try:
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        j_date = jdatetime.date(year, month, day)
        return j_date.togregorian()
    except Exception as e:
        raise ValueError(f"تاریخ شمسی نامعتبر: {e}")
