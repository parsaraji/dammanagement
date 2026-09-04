from flask import Blueprint, render_template
from flask_login import login_required
from app.extensions import db
from app.models.animal import Animal, AnimalStatus, Sex
from app.models.milk import MilkRecord
from app.models.reproduction import Insemination
from datetime import datetime

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def index():
    today = datetime.now().date()
    total_animals = Animal.query.filter_by(status=AnimalStatus.ALIVE).count()
    total_females = Animal.query.filter_by(status=AnimalStatus.ALIVE, sex=Sex.FEMALE).count()

    total_pregnant = db.session.query(db.func.count(db.distinct(Insemination.animal_id))).filter(Insemination.led_to_pregnancy == True).scalar() or 0

    today_milk_records = MilkRecord.query.filter_by(date=today).all()
    today_milk_total = round(sum(r.total_amount for r in today_milk_records), 2)

    return render_template('dashboard/index.html',
                           total_animals=total_animals,
                           total_females=total_females,
                           total_pregnant=total_pregnant,
                           today_milk_total=today_milk_total)
