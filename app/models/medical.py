import enum
from datetime import datetime, timezone
from app.extensions import db

class VisitType(enum.Enum):
    REPRODUCTIVE = 'reproductive'
    MEDICAL = 'medical'

class TreatmentReproduction(db.Model):
    __tablename__ = 'treatment_reproduction'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    visit_type = db.Column(db.Enum(VisitType), default=VisitType.MEDICAL, nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=True)
    doctor = db.Column(db.String(100), nullable=True)
    visit_reason = db.Column(db.String(255), nullable=True)
    diagnosis = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    treatment_end_date = db.Column(db.Date, nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    animal = db.relationship('Animal', backref=db.backref('treatments', cascade='all, delete-orphan', lazy='dynamic'))

class MedicineNoVisit(db.Model):
    __tablename__ = 'medicine_no_visit'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    prescribe_date = db.Column(db.Date, nullable=False)
    consume_date = db.Column(db.Date, nullable=False)
    medicine_name = db.Column(db.String(100), nullable=False)
    dose_amount = db.Column(db.Float, nullable=True)
    dose_unit = db.Column(db.String(50), nullable=True)
    consumption_method = db.Column(db.String(100), nullable=True)
    consume_time = db.Column(db.String(10), nullable=True)
    is_recurring = db.Column(db.Boolean, default=False, nullable=False)
    recurrence_days = db.Column(db.Integer, nullable=True)
    recurrence_interval = db.Column(db.Integer, nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('medicines_no_visit', cascade='all, delete-orphan', lazy='dynamic'))

class Vaccination(db.Model):
    __tablename__ = 'vaccination'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    dose_number = db.Column(db.String(20), nullable=True)
    vaccine_name = db.Column(db.String(100), nullable=False)
    agent_name = db.Column(db.String(100), nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('vaccinations', cascade='all, delete-orphan', lazy='dynamic'))
