#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models.user import db
from models.ticker import Ticker
from models.price import Price
from models.saved_search import SavedSearch

def create_app():
    """Créer l'application Flask pour l'initialisation"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///screening_actions.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    db.init_app(app)
    
    return app

def init_database():
    """Initialiser la base de données avec toutes les tables"""
    app = create_app()
    
    with app.app_context():
        print("Création des tables de la base de données...")
        
        # Supprimer toutes les tables existantes
        db.drop_all()
        print("Tables existantes supprimées")
        
        # Créer toutes les tables
        db.create_all()
        print("Nouvelles tables créées:")
        print("- users")
        print("- tickers") 
        print("- prices")
        print("- saved_searches")
        
        print("Base de données initialisée avec succès!")

if __name__ == "__main__":
    init_database()

