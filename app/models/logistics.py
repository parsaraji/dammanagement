from datetime import datetime
from app.extensions import db

class PenMovement(db.Model):
    __tablename__ = 'pen_movement'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='RESTRICT'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    from_pen_id = db.Column(db.Integer, db.ForeignKey('pen.id', ondelete='SET NULL'), nullable=True)
    to_pen_id = db.Column(db.Integer, db.ForeignKey('pen.id', ondelete='SET NULL'), nullable=True)
    reason = db.Column(db.String(255), nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    animal = db.relationship('Animal', backref=db.backref('pen_movements', cascade='all, delete-orphan', lazy='dynamic'))
    from_pen = db.relationship('Pen', foreign_keys=[from_pen_id])
    to_pen = db.relationship('Pen', foreign_keys=[to_pen_id])

class HerdComposition(db.Model):
    __tablename__ = 'herd_composition'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False, index=True)
    male_count = db.Column(db.Integer, default=0, nullable=False)
    female_count = db.Column(db.Integer, default=0, nullable=False)
    lamb_count = db.Column(db.Integer, default=0, nullable=False)
    pregnant_count = db.Column(db.Integer, default=0, nullable=False)
    lactating_count = db.Column(db.Integer, default=0, nullable=False)
    dry_count = db.Column(db.Integer, default=0, nullable=False)
    total_count = db.Column(db.Integer, default=0, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
