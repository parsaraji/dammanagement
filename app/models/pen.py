from app.extensions import db

class Pen(db.Model):
    __tablename__ = 'pen'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    capacity = db.Column(db.Integer, default=0, nullable=False)
    pen_type = db.Column(db.String(50), nullable=True) # e.g. زایمان, پرواربندی, نگهداری
    notes = db.Column(db.Text, nullable=True)

    animals = db.relationship('Animal', backref='current_pen', foreign_keys='Animal.current_pen_id', lazy='dynamic')

    def __repr__(self):
        return f'<Pen {self.name} ({self.code})>'
