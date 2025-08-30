from flask_sqlalchemy import SQLAlchemy
from .user import db
from datetime import datetime
import json

class SavedSearch(db.Model):
    __tablename__ = 'saved_searches'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    parameters = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation avec l'utilisateur
    user = db.relationship('User', backref=db.backref('saved_searches', lazy=True))
    
    def __repr__(self):
        return f'<SavedSearch {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'parameters': json.loads(self.parameters),
            'created_at': self.created_at.isoformat()
        }
    
    def set_parameters(self, params_dict):
        """Convertit un dictionnaire en JSON string pour le stockage"""
        self.parameters = json.dumps(params_dict)
    
    def get_parameters(self):
        """Retourne les paramètres sous forme de dictionnaire"""
        return json.loads(self.parameters)

