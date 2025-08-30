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
import yfinance as yf
import time

# Imports des modèles
from src.models.user import db
from src.models.ticker import Ticker
from src.models.price import Price

# Configuration

DATABASE_URL = "sqlite:///screening_actions.db"

def setup_database():
    """Configure la base de données"""
    from flask import Flask
    
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        return engine, Session(), app

def ingest_ticker_data(session, symbol: str, index_name: str):
    """Ingère les données d'un ticker spécifique en utilisant yfinance"""
    try:
        ticker_yf = yf.Ticker(symbol)
        info = ticker_yf.info

        if not info:
            print(f"Aucune information trouvée pour {symbol} via yfinance")
            return False

        # Vérifier si le ticker existe déjà
        existing_ticker = session.query(Ticker).filter_by(ticker=symbol).first()

        if not existing_ticker:
            # Créer le ticker
            ticker = Ticker(
                ticker=symbol,
                name=info.get('longName', info.get('shortName', symbol)),
                country=info.get('country', ''),
                sector=info.get('sector', ''),
                market_cap=info.get('marketCap', 0),
                currency=info.get('currency', 'USD'),
                exchange=info.get('exchange', ''),
                index_membership=index_name,
                ipo_date=datetime.fromtimestamp(info.get('firstTradeDateEpochUtc', 0)).date() if info.get('firstTradeDateEpochUtc') and info.get('firstTradeDateEpochUtc') > 0 else None,
                is_suspended=False # yfinance ne fournit pas directement cette info, on suppose non suspendu par défaut
            )

            session.add(ticker)
            session.commit()
            print(f"Ticker {symbol} ajouté à la base de données")

        else:
            ticker = existing_ticker
            print(f"Ticker {symbol} existe déjà")

        # Récupérer les données de prix ajustées
        # Période 'max' pour obtenir toutes les données disponibles
        # interval '1d' pour les données quotidiennes
        hist = ticker_yf.history(period="max", interval="1d")

        if hist.empty:
            print(f"Aucune donnée historique pour {symbol}")
            return False

        # Supprimer les anciens prix pour ce ticker
        session.query(Price).filter_by(ticker_id=ticker.id).delete()

        # Ajouter les nouveaux prix
        prices_added = 0
        for index, row in hist.iterrows():
            price = Price(
                ticker_id=ticker.id,
                date=index.date(),
                adjusted_close=row["Adj Close"],
                volume=row["Volume"],
                high=row["High"],
                low=row["Low"],
                open=row["Open"]
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
    print("Démarrage de l'ingestion des données yfinance...")
    
    # Configuration
    engine, session, app = setup_database()
    
    with app.app_context():
        # Symboles à traiter (échantillon représentatif)
        symbols_to_process = [
            # S&P 500
            ("AAPL", "sp500"), ("MSFT", "sp500"), ("GOOGL", "sp500"), ("AMZN", "sp500"), ("TSLA", "sp500"),
            ("NVDA", "sp500"), ("META", "sp500"), ("NFLX", "sp500"), ("JPM", "sp500"), ("JNJ", "sp500"),
            
            # Eurostoxx 600
            ("ASML.AS", "eurostoxx600"), ("SAP.DE", "eurostoxx600"), ("NESN.SW", "eurostoxx600"), ("LVMH.PA", "eurostoxx600"), ("TTE.PA", "eurostoxx600"),
            ("OR.PA", "eurostoxx600"), ("MC.PA", "eurostoxx600"), ("SIE.DE", "eurostoxx600"), ("INGA.AS", "eurostoxx600"), ("BNP.PA", "eurostoxx600")
        ]
        
        successful_ingestions = 0
        total_symbols = len(symbols_to_process)
        
        print(f"Traitement de {total_symbols} symboles...")
        
        for i, (symbol, index_name) in enumerate(symbols_to_process, 1):
            print(f"\n[{i}/{total_symbols}] Traitement de {symbol} ({index_name})...")
            
            try:
                success = ingest_ticker_data(session, symbol, index_name)
                if success:
                    successful_ingestions += 1
                
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

