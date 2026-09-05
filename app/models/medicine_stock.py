from datetime import datetime, timezone
from app.extensions import db
from app.models.sperm import StockTransactionType

class Medicine(db.Model):
    __tablename__ = 'medicine'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=True)
    unit = db.Column(db.String(20), default='cc', nullable=False)

    stocks = db.relationship('MedicineStock', backref='medicine', cascade='all, delete-orphan', lazy='dynamic')

    @property
    def current_stock(self):
        in_qty = sum(s.quantity for s in self.stocks if s.transaction_type == StockTransactionType.IN)
        out_qty = sum(s.quantity for s in self.stocks if s.transaction_type == StockTransactionType.OUT)
        return in_qty - out_qty

    def __repr__(self):
        return f'<Medicine {self.name}>'

class MedicineStock(db.Model):
    __tablename__ = 'medicine_stock'

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.Enum(StockTransactionType), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    invoice_number = db.Column(db.String(50), nullable=True)
    supplier = db.Column(db.String(100), nullable=True)
    consumed_for_animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', ondelete='SET NULL'), nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    animal = db.relationship('Animal')
