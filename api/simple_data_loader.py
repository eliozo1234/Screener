#!/usr/bin/env python3
"""
Script simplifié pour charger des données de test depuis Alpha Vantage
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models.user import db
from models.ticker import Ticker
from models.price import Price
from alpha_vantage_client import AlphaVantageClient
from datetime import datetime, timedelta
import time

def create_app():
    """Créer l'application Flask"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///screening_actions.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    db.init_app(app)
    return app

def load_sample_data():
    """Charger des données d'échantillon depuis Alpha Vantage"""
    app = create_app()
    
    with app.app_context():
        print("Chargement des données d'échantillon...")
        
        # Configuration Alpha Vantage
        client = AlphaVantageClient("DHQESFCKN9JIMDD6")
        
        # Symboles à charger (limité pour éviter les limites de rate)
        symbols = [
            ('AAPL', 'sp500', 'Apple Inc.'),
            ('MSFT', 'sp500', 'Microsoft Corporation'),
            ('TSLA', 'sp500', 'Tesla Inc.')
        ]
        
        for symbol, index_name, company_name in symbols:
            print(f"\nTraitement de {symbol}...")
            
            try:
                # Récupérer les informations de l'entreprise
                overview_data = client.get_company_overview(symbol)
                company_info = client.parse_company_overview(overview_data)
                
                if not company_info.get('symbol'):
                    print(f"Aucune information trouvée pour {symbol}")
                    continue
                
                # Créer ou mettre à jour le ticker
                ticker = Ticker.query.filter_by(ticker=symbol).first()
                if not ticker:
                    ticker = Ticker(
                        ticker=symbol,
                        name=company_info.get('name', company_name),
                        country=company_info.get('country', 'United States'),
                        sector=company_info.get('sector', 'Technology'),
                        market_cap=company_info.get('market_cap', 0),
                        currency=company_info.get('currency', 'USD'),
                        exchange=company_info.get('exchange', 'NASDAQ'),
                        index_membership=index_name
                    )
                    db.session.add(ticker)
                    db.session.commit()
                    print(f"Ticker {symbol} créé")
                else:
                    print(f"Ticker {symbol} existe déjà")
                
                # Récupérer les données de prix
                daily_data = client.get_daily_adjusted(symbol, outputsize="compact")
                price_data = client.parse_daily_data(daily_data, symbol)
                
                if not price_data:
                    print(f"Aucune donnée de prix pour {symbol}")
                    continue
                
                # Supprimer les anciens prix
                Price.query.filter_by(ticker_id=ticker.id).delete()
                
                # Ajouter les nouveaux prix (derniers 2 ans)
                cutoff_date = datetime.now().date() - timedelta(days=2*365)
                prices_added = 0
                
                for price_info in price_data:
                    if price_info['date'] >= cutoff_date:
                        price = Price(
                            ticker_id=ticker.id,
                            date=price_info['date'],
                            adjusted_close=price_info['adjusted_close'],
                            volume=price_info['volume'],
                            high=price_info['high'],
                            low=price_info['low'],
                            open=price_info['open']
                        )
                        db.session.add(price)
                        prices_added += 1
                
                db.session.commit()
                print(f"{prices_added} prix ajoutés pour {symbol}")
                
                # Pause pour respecter le rate limit
                print("Pause de 15 secondes...")
                time.sleep(15)
                
            except Exception as e:
                print(f"Erreur pour {symbol}: {str(e)}")
                db.session.rollback()
                continue
        
        print("\nChargement des données terminé!")

if __name__ == "__main__":
    load_sample_data()

