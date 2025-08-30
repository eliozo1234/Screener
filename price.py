from flask_sqlalchemy import SQLAlchemy
from .user import db
from datetime import datetime

class Price(db.Model):
    __tablename__ = 'prices'
    
    ticker_id = db.Column(db.Integer, db.ForeignKey('tickers.id'), primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    adjusted_close = db.Column(db.Numeric(18, 4), nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)
    high = db.Column(db.Numeric(18, 4), nullable=True)
    low = db.Column(db.Numeric(18, 4), nullable=True)
    open = db.Column(db.Numeric(18, 4), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Price {self.ticker_id} {self.date}>'
    
    def to_dict(self):
        return {
            'ticker_id': self.ticker_id,
            'date': self.date.isoformat(),
            'adjusted_close': float(self.adjusted_close),
            'volume': self.volume,
            'high': float(self.high),
            'low': float(self.low),
            'open': float(self.open),
            'timestamp': self.timestamp.isoformat()
        }

