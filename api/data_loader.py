"""
Script pour charger des données de test dans la base de données
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.models.ticker import Ticker
from src.models.price import Price
from src.main import app
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Crée des données d'exemple pour tester l'application"""
    
    with app.app_context():
        # Supprimer les données existantes
        Price.query.delete()
        Ticker.query.delete()
        db.session.commit()
        
        # Créer des tickers d'exemple
        sample_tickers = [
            # S&P 500 stocks
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc.',
                'country': 'United States',
                'sector': 'Technology',
                'market_cap': 3000000000000,
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'isin': 'US0378331005'
            },
            {
                'ticker': 'MSFT',
                'name': 'Microsoft Corporation',
                'country': 'United States',
                'sector': 'Technology',
                'market_cap': 2800000000000,
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'isin': 'US5949181045'
            },
            {
                'ticker': 'GOOGL',
                'name': 'Alphabet Inc.',
                'country': 'United States',
                'sector': 'Technology',
                'market_cap': 1700000000000,
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'isin': 'US02079K3059'
            },
            {
                'ticker': 'TSLA',
                'name': 'Tesla Inc.',
                'country': 'United States',
                'sector': 'Consumer Discretionary',
                'market_cap': 800000000000,
                'currency': 'USD',
                'exchange': 'NASDAQ',
                'isin': 'US88160R1014'
            },
            {
                'ticker': 'JPM',
                'name': 'JPMorgan Chase & Co.',
                'country': 'United States',
                'sector': 'Financials',
                'market_cap': 500000000000,
                'currency': 'USD',
                'exchange': 'NYSE',
                'isin': 'US46625H1005'
            },
            # Eurostoxx 600 stocks
            {
                'ticker': 'SAP.DE',
                'name': 'SAP SE',
                'country': 'Germany',
                'sector': 'Technology',
                'market_cap': 150000000000,
                'currency': 'EUR',
                'exchange': 'XETRA',
                'isin': 'DE0007164600'
            },
            {
                'ticker': 'ASML.AS',
                'name': 'ASML Holding N.V.',
                'country': 'Netherlands',
                'sector': 'Technology',
                'market_cap': 300000000000,
                'currency': 'EUR',
                'exchange': 'AEX',
                'isin': 'NL0010273215'
            },
            {
                'ticker': 'NESN.SW',
                'name': 'Nestlé S.A.',
                'country': 'Switzerland',
                'sector': 'Consumer Staples',
                'market_cap': 320000000000,
                'currency': 'CHF',
                'exchange': 'SIX',
                'isin': 'CH0038863350'
            },
            {
                'ticker': 'MC.PA',
                'name': 'LVMH Moët Hennessy Louis Vuitton',
                'country': 'France',
                'sector': 'Consumer Discretionary',
                'market_cap': 400000000000,
                'currency': 'EUR',
                'exchange': 'EPA',
                'isin': 'FR0000121014'
            },
            {
                'ticker': 'SHEL.L',
                'name': 'Shell plc',
                'country': 'United Kingdom',
                'sector': 'Energy',
                'market_cap': 200000000000,
                'currency': 'GBP',
                'exchange': 'LSE',
                'isin': 'GB00BP6MXD84'
            }
        ]
        
        # Insérer les tickers
        ticker_objects = []
        for ticker_data in sample_tickers:
            ticker = Ticker(**ticker_data)
            db.session.add(ticker)
            ticker_objects.append(ticker)
        
        db.session.commit()
        
        # Générer des données de prix historiques (5 ans)
        start_date = datetime.now().date() - timedelta(days=5*365)
        end_date = datetime.now().date()
        
        for ticker in ticker_objects:
            current_date = start_date
            base_price = random.uniform(50, 500)  # Prix de base aléatoire
            
            while current_date <= end_date:
                # Simuler une variation de prix réaliste
                daily_change = random.uniform(-0.05, 0.05)  # ±5% par jour max
                base_price *= (1 + daily_change)
                base_price = max(base_price, 1)  # Prix minimum de 1
                
                # Générer OHLC
                open_price = base_price * random.uniform(0.98, 1.02)
                close_price = base_price
                high_price = max(open_price, close_price) * random.uniform(1.0, 1.03)
                low_price = min(open_price, close_price) * random.uniform(0.97, 1.0)
                
                # Volume aléatoire
                volume = random.randint(100000, 10000000)
                
                price = Price(
                    ticker_id=ticker.id,
                    date=current_date,
                    adjusted_close=round(close_price, 2),
                    volume=volume,
                    high=round(high_price, 2),
                    low=round(low_price, 2),
                    open=round(open_price, 2)
                )
                
                db.session.add(price)
                current_date += timedelta(days=1)
        
        db.session.commit()
        print(f"Données créées avec succès: {len(ticker_objects)} tickers avec des prix historiques sur 5 ans")

if __name__ == '__main__':
    create_sample_data()

