import enum
from datetime import datetime
from app.extensions import db

class InseminationType(enum.Enum):
    NATURAL = 'natural'
    ARTIFICIAL = 'artificial'

class CalvingType(enum.Enum):
    NORMAL = 'normal'
    DIFFICULT = 'difficult'
    ABORTION = 'abortion'
    STILLBIRTH = 'stillbirth'

class CIDR(db.Model):
    __tablename__ = 'cidr'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    insert_date = db.Column(db.Date, nullable=False)
    remove_date = db.Column(db.Date, nullable=True)
    cidr_type = db.Column(db.String(50), nullable=True)
    cidr_number = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('cidrs', cascade='all, delete-orphan', lazy='dynamic'))

class Insemination(db.Model):
    __tablename__ = 'insemination'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=True)
    insemination_type = db.Column(db.Enum(InseminationType), default=InseminationType.ARTIFICIAL, nullable=False)
    sperm_id = db.Column(db.Integer, db.ForeignKey('sperm.id', ondelete='SET NULL'), nullable=True)
    sire_animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='SET NULL'), nullable=True)
    parity_cycle = db.Column(db.Integer, default=1, nullable=False)
    led_to_pregnancy = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', foreign_keys=[animal_id], backref=db.backref('inseminations', cascade='all, delete-orphan', lazy='dynamic'))
    sire_animal = db.relationship('Animal', foreign_keys=[sire_animal_id])
    sperm = db.relationship('Sperm')

class HeatNoInsemination(db.Model):
    __tablename__ = 'heat_no_insemination'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=True)
    heat_symptoms = db.Column(db.String(255), nullable=True)
    heat_detector = db.Column(db.String(100), nullable=True)
    heat_description = db.Column(db.Text, nullable=True)
    next_visit_date = db.Column(db.Date, nullable=True)
    doctor = db.Column(db.String(100), nullable=True)
    visit_reason = db.Column(db.String(255), nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('heats_no_insemination', cascade='all, delete-orphan', lazy='dynamic'))

class DryOff(db.Model):
    __tablename__ = 'dry_off'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('dry_offs', cascade='all, delete-orphan', lazy='dynamic'))

class Calving(db.Model):
    __tablename__ = 'calving'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    calving_type = db.Column(db.Enum(CalvingType), default=CalvingType.NORMAL, nullable=False)
    factors = db.Column(db.String(255), nullable=True)
    offspring_count = db.Column(db.Integer, default=1, nullable=False)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('calvings', cascade='all, delete-orphan', lazy='dynamic'))
    offsprings = db.relationship('CalvingOffspring', backref='calving', cascade='all, delete-orphan', lazy='dynamic')

class CalvingOffspring(db.Model):
    __tablename__ = 'calving_offspring'

    id = db.Column(db.Integer, primary_key=True)
    calving_id = db.Column(db.Integer, db.ForeignKey('calving.id', ondelete='CASCADE'), nullable=False)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)

    offspring_animal = db.relationship('Animal')
