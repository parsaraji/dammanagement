import enum
from datetime import datetime
from app.extensions import db

class Sex(enum.Enum):
    MALE = 'male'
    FEMALE = 'female'

class Species(enum.Enum):
    SHEEP = 'sheep'
    GOAT = 'goat'

class Origin(enum.Enum):
    BORN_IN_FARM = 'born_in_farm'
    PURCHASED = 'purchased'

class AnimalStatus(enum.Enum):
    ALIVE = 'alive'
    READY_FOR_REMOVAL = 'ready_for_removal'
    REMOVED = 'removed'

class Animal(db.Model):
    __tablename__ = 'animal'

    id = db.Column(db.Integer, primary_key=True)
    plastic_tag = db.Column(db.String(50), unique=True, nullable=False, index=True)
    serial_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    national_id = db.Column(db.String(50), nullable=True)
    metal_tag = db.Column(db.String(50), nullable=True)
    birth_date = db.Column(db.Date, nullable=False)
    sex = db.Column(db.Enum(Sex), nullable=False)
    species = db.Column(db.Enum(Species), default=Species.SHEEP, nullable=False)
    breed = db.Column(db.String(50), nullable=True)
    parity = db.Column(db.Integer, default=0, nullable=False)
    origin = db.Column(db.Enum(Origin), default=Origin.BORN_IN_FARM, nullable=False)

    mother_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='SET NULL'), nullable=True)
    father_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='SET NULL'), nullable=True)
    father_sperm_id = db.Column(db.Integer, db.ForeignKey('sperm.id', ondelete='SET NULL'), nullable=True)

    current_pen_id = db.Column(db.Integer, db.ForeignKey('pen.id', ondelete='RESTRICT'), nullable=True)
    status = db.Column(db.Enum(AnimalStatus), default=AnimalStatus.ALIVE, nullable=False)

    removal_date = db.Column(db.Date, nullable=True)
    removal_reason = db.Column(db.String(255), nullable=True)
    removal_group = db.Column(db.String(100), nullable=True)
    removal_form_number = db.Column(db.String(50), nullable=True)
    removal_buyer_name = db.Column(db.String(100), nullable=True)

    birth_weight = db.Column(db.Float, nullable=True)
    photo_path = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    mother = db.relationship('Animal', remote_side=[id], foreign_keys=[mother_id], backref=db.backref('offspring_mother', lazy='dynamic'))
    father = db.relationship('Animal', remote_side=[id], foreign_keys=[father_id], backref=db.backref('offspring_father', lazy='dynamic'))

    def __repr__(self):
        return f'<Animal {self.plastic_tag} ({self.species.value if hasattr(self.species, "value") else self.species})>'
