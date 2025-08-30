#!/usr/bin/env python3
"""
Script pour vérifier la structure de la base de données
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models.user import db
from models.ticker import Ticker
from models.price import Price
from sqlalchemy import inspect

def create_app():
    """Créer l'application Flask"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///screening_actions.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    db.init_app(app)
    return app

def check_database():
    """Vérifier la structure de la base de données"""
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        
        print("=== Structure de la base de données ===")
        
        # Vérifier les tables
        tables = inspector.get_table_names()
        print(f"Tables: {tables}")
        
        # Vérifier la structure de la table tickers
        if 'tickers' in tables:
            print("\n=== Structure de la table 'tickers' ===")
            columns = inspector.get_columns('tickers')
            for col in columns:
                print(f"- {col['name']}: {col['type']}")
        
        # Vérifier les données
        print("\n=== Données dans la table 'tickers' ===")
        tickers = Ticker.query.all()
        print(f"Nombre de tickers: {len(tickers)}")
        
        for ticker in tickers[:3]:  # Afficher les 3 premiers
            print(f"- {ticker.ticker}: {ticker.name} ({ticker.index_membership})")
        
        print("\n=== Données dans la table 'prices' ===")
        prices_count = Price.query.count()
        print(f"Nombre total de prix: {prices_count}")
        
        if prices_count > 0:
            sample_price = Price.query.first()
            print(f"Exemple: Ticker ID {sample_price.ticker_id}, Date {sample_price.date}, Prix {sample_price.adjusted_close}")

if __name__ == "__main__":
    check_database()

