from flask_sqlalchemy import SQLAlchemy
from .user import db
from datetime import datetime

class Ticker(db.Model):
    __tablename__ = 'tickers'
    
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), unique=True, nullable=False)
    isin = db.Column(db.String(12), unique=True, nullable=True)
    name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    sector = db.Column(db.String(100), nullable=False)
    market_cap = db.Column(db.BigInteger, nullable=True)
    currency = db.Column(db.String(3), nullable=False)
    exchange = db.Column(db.String(10), nullable=False)
    index_membership = db.Column(db.String(50), nullable=True)  # sp500, eurostoxx600
    ipo_date = db.Column(db.Date, nullable=True)
    is_suspended = db.Column(db.Boolean, default=False)
    
    # Relation avec les prix
    prices = db.relationship('Price', backref='ticker_ref', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Ticker {self.ticker}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'isin': self.isin,
            'name': self.name,
            'country': self.country,
            'sector': self.sector,
            'market_cap': self.market_cap,
            'currency': self.currency,
            'exchange': self.exchange,
            'ipo_date': self.ipo_date.isoformat() if self.ipo_date else None,
            'is_suspended': self.is_suspended
        }

