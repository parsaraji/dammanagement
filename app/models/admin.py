from app.extensions import db

class LookupItem(db.Model):
    __tablename__ = 'lookup_item'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False, index=True) # e.g. breed, color, removal_reason, vaccine_type, medicine_category, event_type
    value = db.Column(db.String(100), nullable=False)

    __table_args__ = (db.UniqueConstraint('category', 'value', name='_category_value_uc'),)

    def __repr__(self):
        return f'<LookupItem {self.category}:{self.value}>'

class ProgramSettings(db.Model):
    __tablename__ = 'program_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<ProgramSettings {self.key}={self.value}>'

class Staff(db.Model):
    __tablename__ = 'staff'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(64), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<Staff {self.full_name}>'
