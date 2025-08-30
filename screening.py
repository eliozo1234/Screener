from flask import Blueprint, request, jsonify
from ..models.user import db
from ..models.ticker import Ticker
from ..models.price import Price
from ..models.saved_search import SavedSearch
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
import json

screening_bp = Blueprint('screening', __name__)

@screening_bp.route('/search', methods=['POST'])
def search_stocks():
    """
    Endpoint principal pour effectuer un screening d'actions
    """
    try:
        data = request.json
        
        # Paramètres par défaut
        indices = data.get('indices', ['sp500', 'eurostoxx600'])
        lookback_years = data.get('lookback_years', 5)
        threshold_pct = data.get('threshold_pct', 50)
        countries = data.get('countries', [])
        sectors = data.get('sectors', [])
        min_market_cap_usd = data.get('min_market_cap_usd', 0)
        min_volume = data.get('min_volume', 0)
        sort_by = data.get('sort_by', 'pct_of_high')
        
        # Calculer la date de début pour le lookback
        lookback_date = datetime.now().date() - timedelta(days=lookback_years * 365)
        
        # Construire la requête de base
        query = db.session.query(Ticker).join(Price)
        
        # Filtres sur les indices
        if 'sp500' in indices and 'eurostoxx600' not in indices:
            query = query.filter(Ticker.index_membership == 'sp500')
        elif 'eurostoxx600' in indices and 'sp500' not in indices:
            query = query.filter(Ticker.index_membership == 'eurostoxx600')
        elif 'sp500' in indices and 'eurostoxx600' in indices:
            query = query.filter(Ticker.index_membership.in_(['sp500', 'eurostoxx600']))
        # Si aucun indice spécifié, on prend tout
        
        # Filtres additionnels
        if countries:
            query = query.filter(Ticker.country.in_(countries))
        
        if sectors:
            query = query.filter(Ticker.sector.in_(sectors))
        
        if min_market_cap_usd > 0:
            query = query.filter(Ticker.market_cap >= min_market_cap_usd)
        
        # Filtrer les actions non suspendues
        query = query.filter(Ticker.is_suspended == False)
        
        # Obtenir les tickers uniques
        tickers = query.distinct().all()
        
        results = []
        
        for ticker in tickers:
            # Obtenir le prix actuel (le plus récent)
            current_price_record = db.session.query(Price).filter(
                Price.ticker_id == ticker.id
            ).order_by(desc(Price.date)).first()
            
            if not current_price_record:
                continue
            
            current_price = float(current_price_record.adjusted_close)
            
            # Obtenir le plus haut sur la période lookback
            high_record = db.session.query(Price).filter(
                and_(
                    Price.ticker_id == ticker.id,
                    Price.date >= lookback_date
                )
            ).order_by(desc(Price.high)).first()
            
            if not high_record:
                continue
            
            lookback_high = float(high_record.high)
            lookback_high_date = high_record.date
            
            # Calculer le pourcentage du plus haut
            pct_of_high = (current_price / lookback_high) * 100
            
            # Appliquer le filtre de seuil
            if pct_of_high <= threshold_pct:
                # Calculer le volume moyen (30 derniers jours)
                avg_volume_record = db.session.query(
                    func.avg(Price.volume).label('avg_volume')
                ).filter(
                    and_(
                        Price.ticker_id == ticker.id,
                        Price.date >= datetime.now().date() - timedelta(days=30)
                    )
                ).first()
                
                avg_volume = int(avg_volume_record.avg_volume) if avg_volume_record.avg_volume else 0
                
                # Filtrer par volume minimum
                if avg_volume >= min_volume:
                    results.append({
                        'ticker': ticker.ticker,
                        'name': ticker.name,
                        'pct_of_high': round(pct_of_high, 2),
                        'lookback_high': lookback_high,
                        'lookback_high_date': lookback_high_date.isoformat(),
                        'current_price': current_price,
                        'market_cap': ticker.market_cap,
                        'country': ticker.country,
                        'sector': ticker.sector,
                        'currency': ticker.currency,
                        'exchange': ticker.exchange,
                        'avg_volume_30d': avg_volume
                    })
        
        # Trier les résultats
        if sort_by == 'pct_of_high':
            results.sort(key=lambda x: x['pct_of_high'])
        elif sort_by == 'market_cap':
            results.sort(key=lambda x: x['market_cap'] or 0, reverse=True)
        elif sort_by == 'current_price':
            results.sort(key=lambda x: x['current_price'], reverse=True)
        
        return jsonify({
            'results': results,
            'total_count': len(results),
            'search_parameters': data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@screening_bp.route('/indices', methods=['GET'])
def get_indices():
    """
    Retourne la liste des indices disponibles
    """
    return jsonify({
        'indices': [
            {'id': 'sp500', 'name': 'S&P 500'},
            {'id': 'eurostoxx600', 'name': 'Eurostoxx 600'}
        ]
    })

@screening_bp.route('/countries', methods=['GET'])
def get_countries():
    """
    Retourne la liste des pays disponibles
    """
    countries = db.session.query(Ticker.country).distinct().all()
    return jsonify({
        'countries': [country[0] for country in countries]
    })

@screening_bp.route('/sectors', methods=['GET'])
def get_sectors():
    """
    Retourne la liste des secteurs disponibles
    """
    sectors = db.session.query(Ticker.sector).distinct().all()
    return jsonify({
        'sectors': [sector[0] for sector in sectors]
    })

@screening_bp.route('/tickers/<ticker_symbol>', methods=['GET'])
def get_ticker_details(ticker_symbol):
    """
    Retourne les détails d'un ticker spécifique
    """
    ticker = Ticker.query.filter_by(ticker=ticker_symbol.upper()).first_or_404()
    
    # Obtenir les 30 derniers prix
    recent_prices = db.session.query(Price).filter(
        Price.ticker_id == ticker.id
    ).order_by(desc(Price.date)).limit(30).all()
    
    return jsonify({
        'ticker': ticker.to_dict(),
        'recent_prices': [price.to_dict() for price in recent_prices]
    })

