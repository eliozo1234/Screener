#!/usr/bin/env python3
"""
Script d'ingestion des données financières depuis Alpha Vantage
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alpha_vantage_client import AlphaVantageClient, SP500_SYMBOLS, EUROSTOXX_SYMBOLS
import time

# Imports des modèles
from models.user import db
from models.ticker import Ticker
from models.price import Price

# Configuration
API_KEY = "DHQESFCKN9JIMDD6"
DATABASE_URL = "sqlite:///screening_actions.db"

def setup_database():
    """Configure la base de données"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return engine, Session()

def ingest_ticker_data(client: AlphaVantageClient, session, symbol: str, index_name: str):
    """Ingère les données d'un ticker spécifique"""
    try:
        # Vérifier si le ticker existe déjà
        existing_ticker = session.query(Ticker).filter_by(ticker=symbol).first()
        
        if not existing_ticker:
            # Récupérer les informations de l'entreprise
            overview_data = client.get_company_overview(symbol)
            company_info = client.parse_company_overview(overview_data)
            
            if not company_info.get('symbol'):
                print(f"Aucune information trouvée pour {symbol}")
                return False
            
            # Créer le ticker
            ticker = Ticker(
                ticker=symbol,
                name=company_info.get('name', symbol),
                country=company_info.get('country', ''),
                sector=company_info.get('sector', ''),
                market_cap=company_info.get('market_cap', 0),
                currency=company_info.get('currency', 'USD'),
                exchange=company_info.get('exchange', ''),
                index_membership=index_name
            )
            
            session.add(ticker)
            session.commit()
            print(f"Ticker {symbol} ajouté à la base de données")
            
        else:
            ticker = existing_ticker
            print(f"Ticker {symbol} existe déjà")
        
        # Récupérer les données de prix
        daily_data = client.get_daily_adjusted(symbol, outputsize="full")
        price_data = client.parse_daily_data(daily_data, symbol)
        
        if not price_data:
            print(f"Aucune donnée de prix pour {symbol}")
            return False
        
        # Supprimer les anciens prix pour ce ticker
        session.query(Price).filter_by(ticker_id=ticker.id).delete()
        
        # Ajouter les nouveaux prix (limiter aux 5 dernières années)
        cutoff_date = datetime.now().date() - timedelta(days=5*365)
        prices_added = 0
        
        for price_info in price_data:
            if price_info['date'] >= cutoff_date:
                price = Price(
                    ticker_id=ticker.id,
                    date=price_info['date'],
                    adjusted_close=price_info['adjusted_close'],
                    volume=price_info['volume']
                )
                session.add(price)
                prices_added += 1
        
        session.commit()
        print(f"{prices_added} prix ajoutés pour {symbol}")
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'ingestion de {symbol}: {str(e)}")
        session.rollback()
        return False

def main():
    """Fonction principale d'ingestion"""
    print("Démarrage de l'ingestion des données Alpha Vantage...")
    print(f"Clé API: {API_KEY[:8]}...")
    
    # Configuration
    engine, session = setup_database()
    client = AlphaVantageClient(API_KEY)
    
    # Symboles à traiter (limité pour éviter les limites de rate)
    symbols_to_process = [
        # S&P 500 - échantillon représentatif
        ('AAPL', 'sp500'),
        ('MSFT', 'sp500'),
        ('GOOGL', 'sp500'),
        ('AMZN', 'sp500'),
        ('TSLA', 'sp500'),
        ('NVDA', 'sp500'),
        ('META', 'sp500'),
        ('NFLX', 'sp500'),
        ('JPM', 'sp500'),
        ('JNJ', 'sp500'),
        
        # Eurostoxx 600 - échantillon représentatif
        ('ASML.AS', 'eurostoxx600'),
        ('SAP.DE', 'eurostoxx600'),
        ('NESN.SW', 'eurostoxx600'),
        ('LVMH.PA', 'eurostoxx600'),
        ('TTE.PA', 'eurostoxx600'),
        ('OR.PA', 'eurostoxx600'),
        ('MC.PA', 'eurostoxx600'),
        ('SIE.DE', 'eurostoxx600'),
        ('INGA.AS', 'eurostoxx600'),
        ('BNP.PA', 'eurostoxx600')
    ]
    
    successful_ingestions = 0
    total_symbols = len(symbols_to_process)
    
    print(f"Traitement de {total_symbols} symboles...")
    
    for i, (symbol, index_name) in enumerate(symbols_to_process, 1):
        print(f"\n[{i}/{total_symbols}] Traitement de {symbol} ({index_name})...")
        
        try:
            success = ingest_ticker_data(client, session, symbol, index_name)
            if success:
                successful_ingestions += 1
            
            # Pause entre les symboles pour respecter le rate limit
            if i < total_symbols:
                print(f"Pause de {client.rate_limit_delay} secondes...")
                time.sleep(client.rate_limit_delay)
                
        except KeyboardInterrupt:
            print("\nInterruption par l'utilisateur")
            break
        except Exception as e:
            print(f"Erreur inattendue pour {symbol}: {str(e)}")
            continue
    
    session.close()
    
    print(f"\n=== Résumé de l'ingestion ===")
    print(f"Symboles traités avec succès: {successful_ingestions}/{total_symbols}")
    print(f"Taux de réussite: {(successful_ingestions/total_symbols)*100:.1f}%")
    print("Ingestion terminée!")

if __name__ == "__main__":
    main()

