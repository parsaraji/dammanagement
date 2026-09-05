import enum
from datetime import datetime, timezone
from app.extensions import db

class MilkRecordType(enum.Enum):
    OFFICIAL = 'official'
    UNOFFICIAL = 'unofficial'

class MilkRecord(db.Model):
    __tablename__ = 'milk_record'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    record_type = db.Column(db.Enum(MilkRecordType), default=MilkRecordType.OFFICIAL, nullable=False)
    parity_cycle = db.Column(db.Integer, default=1, nullable=False)

    milking1_time = db.Column(db.String(10), nullable=True)
    milking1_amount = db.Column(db.Float, default=0.0, nullable=True)

    milking2_time = db.Column(db.String(10), nullable=True)
    milking2_amount = db.Column(db.Float, default=0.0, nullable=True)

    milking3_time = db.Column(db.String(10), nullable=True)
    milking3_amount = db.Column(db.Float, default=0.0, nullable=True)

    total_amount = db.Column(db.Float, default=0.0, nullable=False)
    fat_percent = db.Column(db.Float, nullable=True)
    protein_percent = db.Column(db.Float, nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    animal = db.relationship('Animal', backref=db.backref('milk_records', cascade='all, delete-orphan', lazy='dynamic'))

    def compute_total(self):
        m1 = self.milking1_amount or 0.0
        m2 = self.milking2_amount or 0.0
        m3 = self.milking3_amount or 0.0
        self.total_amount = round(m1 + m2 + m3, 2)
        return self.total_amount

class StandardizedMilk(db.Model):
    __tablename__ = 'standardized_milk'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    parity_cycle = db.Column(db.Integer, default=1, nullable=False)
    calc_date = db.Column(db.Date, nullable=False)
    standardized_daily_avg = db.Column(db.Float, nullable=False)
    method_notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('standardized_milks', cascade='all, delete-orphan', lazy='dynamic'))
