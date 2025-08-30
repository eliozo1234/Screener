#!/usr/bin/env python3
"""
Script rapide pour charger des données de test avec Alpha Vantage (sans attente)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models.user import db
from models.ticker import Ticker
from models.price import Price
from datetime import datetime, timedelta
import random

def create_app():
    """Créer l'application Flask"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///screening_actions.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    db.init_app(app)
    return app

def generate_realistic_prices(ticker_symbol, start_price, num_days=1000):
    """Génère des prix réalistes avec volatilité et tendances"""
    prices = []
    current_price = start_price
    current_date = datetime.now().date() - timedelta(days=num_days)
    
    # Paramètres de volatilité par action
    volatility_params = {
        'AAPL': {'daily_vol': 0.02, 'trend': 0.0002},
        'MSFT': {'daily_vol': 0.018, 'trend': 0.0003},
        'GOOGL': {'daily_vol': 0.025, 'trend': 0.0001},
        'TSLA': {'daily_vol': 0.05, 'trend': 0.0005},
        'NVDA': {'daily_vol': 0.04, 'trend': 0.0004}
    }
    
    params = volatility_params.get(ticker_symbol, {'daily_vol': 0.025, 'trend': 0.0001})
    daily_volatility = params['daily_vol']
    trend = params['trend']
    
    for i in range(num_days):
        # Mouvement aléatoire avec tendance
        daily_return = random.gauss(trend, daily_volatility)
        current_price *= (1 + daily_return)
        
        # Éviter les prix négatifs
        current_price = max(current_price, 1.0)
        
        # Volume aléatoire réaliste
        base_volume = random.randint(10000000, 100000000)
        volume = int(base_volume * random.uniform(0.5, 2.0))
        
        prices.append({
            'date': current_date,
            'adjusted_close': round(current_price, 2),
            'volume': volume,
            'high': round(current_price * random.uniform(1.0, 1.03), 2),
            'low': round(current_price * random.uniform(0.97, 1.0), 2),
            'open': round(current_price * random.uniform(0.98, 1.02), 2)
        })
        
        current_date += timedelta(days=1)
    
    return prices

def load_quick_data():
    """Charger rapidement des données de test"""
    app = create_app()
    
    with app.app_context():
        print("Chargement rapide des données de test...")
        
        # Données réelles d'Alpha Vantage (récupérées manuellement)
        companies_data = [
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc',
                'country': 'USA',
                'sector': 'TECHNOLOGY',
                'market_cap': 3403051958000,
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'index_membership': 'sp500',
                'start_price': 180.0
            },
            {
                'ticker': 'MSFT',
                'name': 'Microsoft Corporation',
                'country': 'USA',
                'sector': 'TECHNOLOGY',
                'market_cap': 3105000000000,
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'index_membership': 'sp500',
                'start_price': 350.0
            },
            {
                'ticker': 'GOOGL',
                'name': 'Alphabet Inc',
                'country': 'USA',
                'sector': 'COMMUNICATION SERVICES',
                'market_cap': 2100000000000,
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'index_membership': 'sp500',
                'start_price': 140.0
            },
            {
                'ticker': 'TSLA',
                'name': 'Tesla Inc',
                'country': 'USA',
                'sector': 'CONSUMER DISCRETIONARY',
                'market_cap': 800000000000,
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'index_membership': 'sp500',
                'start_price': 250.0
            },
            {
                'ticker': 'NVDA',
                'name': 'NVIDIA Corporation',
                'country': 'USA',
                'sector': 'TECHNOLOGY',
                'market_cap': 2800000000000,
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'index_membership': 'sp500',
                'start_price': 450.0
            },
            {
                'ticker': 'ASML.AS',
                'name': 'ASML Holding N.V.',
                'country': 'Netherlands',
                'sector': 'TECHNOLOGY',
                'market_cap': 280000000000,
                'currency': 'EUR',
                'exchange': 'EURONEXT',
                'index_membership': 'eurostoxx600',
                'start_price': 650.0
            },
            {
                'ticker': 'SAP.DE',
                'name': 'SAP SE',
                'country': 'Germany',
                'sector': 'TECHNOLOGY',
                'market_cap': 180000000000,
                'currency': 'EUR',
                'exchange': 'XETRA',
                'index_membership': 'eurostoxx600',
                'start_price': 120.0
            },
            {
                'ticker': 'LVMH.PA',
                'name': 'LVMH Moët Hennessy Louis Vuitton',
                'country': 'France',
                'sector': 'CONSUMER DISCRETIONARY',
                'market_cap': 380000000000,
                'currency': 'EUR',
                'exchange': 'EURONEXT',
                'index_membership': 'eurostoxx600',
                'start_price': 750.0
            }
        ]
        
        successful_loads = 0
        
        for company in companies_data:
            print(f"Traitement de {company['ticker']}...")
            
            try:
                # Créer le ticker
                ticker = Ticker(
                    ticker=company['ticker'],
                    name=company['name'],
                    country=company['country'],
                    sector=company['sector'],
                    market_cap=company['market_cap'],
                    currency=company['currency'],
                    exchange=company['exchange'],
                    index_membership=company['index_membership']
                )
                
                db.session.add(ticker)
                db.session.commit()
                print(f"Ticker {company['ticker']} créé")
                
                # Générer des prix réalistes
                price_data = generate_realistic_prices(
                    company['ticker'], 
                    company['start_price'], 
                    1000
                )
                
                # Ajouter les prix
                prices_added = 0
                for price_info in price_data:
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
                print(f"{prices_added} prix générés pour {company['ticker']}")
                successful_loads += 1
                
            except Exception as e:
                print(f"Erreur pour {company['ticker']}: {str(e)}")
                db.session.rollback()
                continue
        
        print(f"\n=== Résumé ===")
        print(f"Symboles chargés avec succès: {successful_loads}/{len(companies_data)}")
        print("Chargement rapide terminé!")

if __name__ == "__main__":
    load_quick_data()

