from app.models.milk import MilkRecord, StandardizedMilk
from app.models.admin import ProgramSettings
from app.extensions import db
from datetime import datetime

def get_program_setting(key, default_value):
    setting = ProgramSettings.query.filter_by(key=key).first()
    if setting and setting.value is not None:
        try:
            return type(default_value)(setting.value)
        except Exception:
            return default_value
    return default_value

def compute_standardized_milk(animal_id, parity_cycle=None):
    """
    Calculates standardized daily milk yield for an animal in a given parity cycle.
    Validates MIN_RECORDS and MAX_GAP_DAYS.
    """
    min_records = get_program_setting('min_milk_records', 3)
    max_gap_days = get_program_setting('max_gap_days', 10)

    query = MilkRecord.query.filter_by(animal_id=animal_id)
    if parity_cycle is not None:
        query = query.filter_by(parity_cycle=parity_cycle)

    records = query.order_by(MilkRecord.date.asc()).all()

    if len(records) < min_records:
        return {
            "success": False,
            "message": "تعداد یا فاصله رکوردها برای محاسبه استاندارد کافی نیست",
            "count": len(records),
            "min_required": min_records
        }

    # Check gap days between consecutive records
    for i in range(1, len(records)):
        gap = (records[i].date - records[i-1].date).days
        if gap > max_gap_days:
            return {
                "success": False,
                "message": "تعداد یا فاصله رکوردها برای محاسبه استاندارد کافی نیست",
                "max_gap_found": gap,
                "max_allowed_gap": max_gap_days
            }

    # Compute daily average
    total_yield = sum(r.total_amount for r in records if r.total_amount)
    avg_yield = round(total_yield / len(records), 2)

    # Cache or update StandardizedMilk record
    std_record = StandardizedMilk.query.filter_by(animal_id=animal_id, parity_cycle=parity_cycle or 1).first()
    if not std_record:
        std_record = StandardizedMilk(
            animal_id=animal_id,
            parity_cycle=parity_cycle or 1,
            calc_date=datetime.now().date(),
            standardized_daily_avg=avg_yield,
            method_notes=f"محاسبه بر اساس {len(records)} رکورد معتبر"
        )
        db.session.add(std_record)
    else:
        std_record.calc_date = datetime.now().date()
        std_record.standardized_daily_avg = avg_yield
        std_record.method_notes = f"محاسبه بر اساس {len(records)} رکورد معتبر"

    db.session.commit()

    return {
        "success": True,
        "avg": avg_yield,
        "record_count": len(records),
        "records": records
    }
