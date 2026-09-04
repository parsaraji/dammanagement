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

def calculate_4pct_fcm(milk_yield_kg: float, fat_percent: float) -> float:
    """
    Gaines formula for 4% Fat-Corrected Milk (FCM):
    FCM_4% (kg) = (0.4 * milk_yield_kg) + (15 * fat_yield_kg)
    where fat_yield_kg = milk_yield_kg * (fat_percent / 100)
    """
    if not milk_yield_kg or milk_yield_kg <= 0:
        return 0.0
    if fat_percent is None or fat_percent <= 0:
        return round(milk_yield_kg, 2)

    fat_yield_kg = milk_yield_kg * (fat_percent / 100.0)
    fcm = (0.4 * milk_yield_kg) + (15.0 * fat_yield_kg)
    return round(fcm, 2)

def compute_tim_cumulative_yield(records):
    """
    ICAR Test Interval Method (TIM) for cumulative lactation yield estimation:
    interval_yield = ((a_i + a_(i+1)) / 2) * d_i
    """
    if not records or len(records) == 0:
        return 0.0

    if len(records) == 1:
        return round(records[0].total_amount or 0.0, 2)

    total_tim_yield = 0.0
    for i in range(len(records) - 1):
        r1 = records[i]
        r2 = records[i+1]
        a1 = r1.total_amount or 0.0
        a2 = r2.total_amount or 0.0
        d_days = (r2.date - r1.date).days
        interval_yield = ((a1 + a2) / 2.0) * d_days
        total_tim_yield += interval_yield

    return round(total_tim_yield, 2)

def compute_standardized_milk(animal_id, parity_cycle=None):
    """
    Calculates standardized daily milk yield, ICAR TIM cumulative yield, and 4% FCM yield.
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

    for i in range(1, len(records)):
        gap = (records[i].date - records[i-1].date).days
        if gap > max_gap_days:
            return {
                "success": False,
                "message": "تعداد یا فاصله رکوردها برای محاسبه استاندارد کافی نیست",
                "max_gap_found": gap,
                "max_allowed_gap": max_gap_days
            }

    # Daily average
    total_yield = sum(r.total_amount for r in records if r.total_amount)
    avg_yield = round(total_yield / len(records), 2)

    # ICAR TIM cumulative yield
    tim_cumulative = compute_tim_cumulative_yield(records)

    # 4% FCM for records with fat %
    fcm_records = []
    for r in records:
        fcm_val = calculate_4pct_fcm(r.total_amount or 0.0, r.fat_percent)
        fcm_records.append({'date': r.date, 'raw': r.total_amount, 'fat': r.fat_percent, 'fcm_4pct': fcm_val})

    # Cache or update StandardizedMilk record
    std_record = StandardizedMilk.query.filter_by(animal_id=animal_id, parity_cycle=parity_cycle or 1).first()
    if not std_record:
        std_record = StandardizedMilk(
            animal_id=animal_id,
            parity_cycle=parity_cycle or 1,
            calc_date=datetime.now().date(),
            standardized_daily_avg=avg_yield,
            method_notes=f"محاسبه علمی TIM و avg بر اساس {len(records)} رکورد معتبر"
        )
        db.session.add(std_record)
    else:
        std_record.calc_date = datetime.now().date()
        std_record.standardized_daily_avg = avg_yield
        std_record.method_notes = f"محاسبه علمی TIM و avg بر اساس {len(records)} رکورد معتبر"

    db.session.commit()

    return {
        "success": True,
        "avg": avg_yield,
        "tim_cumulative": tim_cumulative,
        "fcm_records": fcm_records,
        "record_count": len(records),
        "records": records
    }
