import enum
from datetime import datetime
from app.extensions import db

class MeasurementType(enum.Enum):
    WEIGHT = 'weight'
    BODY_TEMPERATURE = 'body_temperature'
    BODY_LENGTH = 'body_length'
    CHEST_GIRTH = 'chest_girth'
    WITHERS_HEIGHT = 'withers_height'
    SALE_WEIGHT = 'sale_weight'

class QuarterEnum(enum.Enum):
    FRONT_LEFT = 'front_left'
    FRONT_RIGHT = 'front_right'
    REAR_LEFT = 'rear_left'
    REAR_RIGHT = 'rear_right'

class HoofStatusEnum(enum.Enum):
    HEALTHY = 'healthy'
    LONG = 'long'
    PROBLEM = 'problem'

class Measurement(db.Model):
    __tablename__ = 'measurement'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    measurement_type = db.Column(db.Enum(MeasurementType), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('measurements', cascade='all, delete-orphan', lazy='dynamic'))

class Quarter(db.Model):
    __tablename__ = 'quarter'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    quarter = db.Column(db.Enum(QuarterEnum), nullable=False)
    issue_description = db.Column(db.Text, nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('quarters', cascade='all, delete-orphan', lazy='dynamic'))

class OneTimeEvent(db.Model):
    __tablename__ = 'one_time_event'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('one_time_events', cascade='all, delete-orphan', lazy='dynamic'))

class BodyScore(db.Model):
    __tablename__ = 'body_score'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    score = db.Column(db.Float, nullable=False) # 1-5

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('body_scores', cascade='all, delete-orphan', lazy='dynamic'))

class MovementScore(db.Model):
    __tablename__ = 'movement_score'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    score = db.Column(db.Float, nullable=False) # 1-5

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('movement_scores', cascade='all, delete-orphan', lazy='dynamic'))

class SuggestedSperm(db.Model):
    __tablename__ = 'suggested_sperm'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    parity_cycle = db.Column(db.Integer, default=1, nullable=False)
    sperm_1_id = db.Column(db.Integer, db.ForeignKey('sperm.id', ondelete='SET NULL'), nullable=True)
    sperm_2_id = db.Column(db.Integer, db.ForeignKey('sperm.id', ondelete='SET NULL'), nullable=True)
    sperm_3_id = db.Column(db.Integer, db.ForeignKey('sperm.id', ondelete='SET NULL'), nullable=True)
    sperm_4_id = db.Column(db.Integer, db.ForeignKey('sperm.id', ondelete='SET NULL'), nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('suggested_sperms', cascade='all, delete-orphan', lazy='dynamic'))

class HoofTrimming(db.Model):
    __tablename__ = 'hoof_trimming'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    front_left_status = db.Column(db.Enum(HoofStatusEnum), default=HoofStatusEnum.HEALTHY, nullable=False)
    front_right_status = db.Column(db.Enum(HoofStatusEnum), default=HoofStatusEnum.HEALTHY, nullable=False)
    rear_left_status = db.Column(db.Enum(HoofStatusEnum), default=HoofStatusEnum.HEALTHY, nullable=False)
    rear_right_status = db.Column(db.Enum(HoofStatusEnum), default=HoofStatusEnum.HEALTHY, nullable=False)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('hoof_trimmings', cascade='all, delete-orphan', lazy='dynamic'))
