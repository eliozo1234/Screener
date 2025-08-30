#!/usr/bin/env python3
"""
Script hybride : Alpha Vantage pour les infos entreprises + prix simulés réalistes
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
import random
import time

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
        'AMZN': {'daily_vol': 0.03, 'trend': 0.0001},
        'TSLA': {'daily_vol': 0.05, 'trend': 0.0005},
        'NVDA': {'daily_vol': 0.04, 'trend': 0.0004},
        'META': {'daily_vol': 0.035, 'trend': 0.0002},
        'NFLX': {'daily_vol': 0.03, 'trend': 0.0001},
        'JPM': {'daily_vol': 0.02, 'trend': 0.0001},
        'JNJ': {'daily_vol': 0.015, 'trend': 0.0001},
        'ASML.AS': {'daily_vol': 0.025, 'trend': 0.0002},
        'SAP.DE': {'daily_vol': 0.02, 'trend': 0.0001},
        'NESN.SW': {'daily_vol': 0.015, 'trend': 0.0001},
        'LVMH.PA': {'daily_vol': 0.025, 'trend': 0.0002},
        'TTE.PA': {'daily_vol': 0.025, 'trend': 0.0001}
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

def load_hybrid_data():
    """Charger des données hybrides (Alpha Vantage + prix simulés)"""
    app = create_app()
    
    with app.app_context():
        print("Chargement des données hybrides...")
        
        # Configuration Alpha Vantage
        client = AlphaVantageClient("DHQESFCKN9JIMDD6")
        
        # Symboles avec prix de départ réalistes
        symbols_data = [
            # S&P 500
            ('AAPL', 'sp500', 180.0),
            ('MSFT', 'sp500', 350.0),
            ('GOOGL', 'sp500', 140.0),
            ('AMZN', 'sp500', 145.0),
            ('TSLA', 'sp500', 250.0),
            ('NVDA', 'sp500', 450.0),
            ('META', 'sp500', 320.0),
            ('NFLX', 'sp500', 400.0),
            ('JPM', 'sp500', 150.0),
            ('JNJ', 'sp500', 160.0),
            
            # Eurostoxx 600 (prix en devise locale)
            ('ASML.AS', 'eurostoxx600', 650.0),
            ('SAP.DE', 'eurostoxx600', 120.0),
            ('NESN.SW', 'eurostoxx600', 110.0),
            ('LVMH.PA', 'eurostoxx600', 750.0),
            ('TTE.PA', 'eurostoxx600', 60.0)
        ]
        
        successful_loads = 0
        
        for symbol, index_name, start_price in symbols_data:
            print(f"\nTraitement de {symbol}...")
            
            try:
                # Récupérer les informations réelles depuis Alpha Vantage
                overview_data = client.get_company_overview(symbol)
                company_info = client.parse_company_overview(overview_data)
                
                if not company_info.get('symbol'):
                    print(f"Aucune information Alpha Vantage pour {symbol}, utilisation des données par défaut")
                    company_info = {
                        'symbol': symbol,
                        'name': symbol + ' Corporation',
                        'country': 'United States' if index_name == 'sp500' else 'Europe',
                        'sector': 'Technology',
                        'market_cap': 1000000000000,
                        'currency': 'USD' if index_name == 'sp500' else 'EUR',
                        'exchange': 'NASDAQ' if index_name == 'sp500' else 'EURONEXT'
                    }
                
                # Créer ou mettre à jour le ticker
                ticker = Ticker.query.filter_by(ticker=symbol).first()
                if not ticker:
                    ticker = Ticker(
                        ticker=symbol,
                        name=company_info.get('name', symbol),
                        country=company_info.get('country', 'Unknown'),
                        sector=company_info.get('sector', 'Technology'),
                        market_cap=company_info.get('market_cap', 0),
                        currency=company_info.get('currency', 'USD'),
                        exchange=company_info.get('exchange', 'NASDAQ'),
                        index_membership=index_name
                    )
                    db.session.add(ticker)
                    db.session.commit()
                    print(f"Ticker {symbol} créé avec données Alpha Vantage")
                else:
                    print(f"Ticker {symbol} existe déjà")
                
                # Générer des prix réalistes
                print(f"Génération de prix réalistes pour {symbol}...")
                price_data = generate_realistic_prices(symbol, start_price, 1000)
                
                # Supprimer les anciens prix
                Price.query.filter_by(ticker_id=ticker.id).delete()
                
                # Ajouter les nouveaux prix
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
                print(f"{prices_added} prix générés pour {symbol}")
                successful_loads += 1
                
                # Pause pour respecter le rate limit Alpha Vantage
                if symbol != symbols_data[-1][0]:  # Pas de pause pour le dernier
                    print("Pause de 15 secondes...")
                    time.sleep(15)
                
            except Exception as e:
                print(f"Erreur pour {symbol}: {str(e)}")
                db.session.rollback()
                continue
        
        print(f"\n=== Résumé ===")
        print(f"Symboles chargés avec succès: {successful_loads}/{len(symbols_data)}")
        print("Chargement des données hybrides terminé!")

if __name__ == "__main__":
    load_hybrid_data()

