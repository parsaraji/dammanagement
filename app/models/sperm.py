import enum
from datetime import datetime, timezone
from app.extensions import db

class StockTransactionType(enum.Enum):
    IN = 'in'
    OUT = 'out'

class Sperm(db.Model):
    __tablename__ = 'sperm'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    breed = db.Column(db.String(50), nullable=True)
    internal_reg_no = db.Column(db.String(50), nullable=True)
    external_reg_no = db.Column(db.String(50), nullable=True)
    is_sexed = db.Column(db.Boolean, default=False, nullable=False)
    stock_qty = db.Column(db.Integer, default=0, nullable=False)

    transactions = db.relationship('SpermTransaction', backref='sperm', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<Sperm {self.name} ({self.code})>'

class SpermTransaction(db.Model):
    __tablename__ = 'sperm_transaction'

    id = db.Column(db.Integer, primary_key=True)
    sperm_id = db.Column(db.Integer, db.ForeignKey('sperm.id', ondelete='CASCADE'), nullable=False)
    transaction_type = db.Column(db.Enum(StockTransactionType), nullable=False)
    date = db.Column(db.Date, nullable=False)
    form_number = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
