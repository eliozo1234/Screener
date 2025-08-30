import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AlphaVantageClient:
    """Client pour l'API Alpha Vantage"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit_delay = 12  # 5 calls per minute = 12 seconds between calls
        
    def _make_request(self, params: Dict) -> Dict:
        """Effectue une requête à l'API Alpha Vantage avec gestion du rate limiting"""
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Vérifier les erreurs de l'API
            if 'Error Message' in data:
                raise Exception(f"API Error: {data['Error Message']}")
            
            if 'Note' in data:
                # Rate limit atteint
                print(f"Rate limit warning: {data['Note']}")
                time.sleep(60)  # Attendre 1 minute
                return self._make_request(params)
            
            return data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_daily_adjusted(self, symbol: str, outputsize: str = "full") -> Dict:
        """Récupère les données de prix quotidiennes ajustées"""
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'outputsize': outputsize
        }
        
        print(f"Fetching daily data for {symbol}...")
        data = self._make_request(params)
        
        # Attendre entre les requêtes pour respecter le rate limit
        time.sleep(self.rate_limit_delay)
        
        return data
    
    def get_company_overview(self, symbol: str) -> Dict:
        """Récupère les informations générales de l'entreprise"""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        
        print(f"Fetching company overview for {symbol}...")
        data = self._make_request(params)
        
        # Attendre entre les requêtes pour respecter le rate limit
        time.sleep(self.rate_limit_delay)
        
        return data
    
    def search_endpoint(self, keywords: str) -> Dict:
        """Recherche des symboles par mots-clés"""
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': keywords
        }
        
        print(f"Searching symbols for: {keywords}")
        data = self._make_request(params)
        
        time.sleep(self.rate_limit_delay)
        
        return data
    
    def parse_daily_data(self, data: Dict, symbol: str) -> List[Dict]:
        """Parse les données quotidiennes en format standardisé"""
        if 'Time Series (Daily)' not in data:
            print(f"No daily data found for {symbol}")
            return []
        
        time_series = data['Time Series (Daily)']
        parsed_data = []
        
        for date_str, values in time_series.items():
            try:
                parsed_data.append({
                    'symbol': symbol,
                    'date': datetime.strptime(date_str, '%Y-%m-%d').date(),
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'adjusted_close': float(values['5. adjusted close']),
                    'volume': int(values['6. volume']),
                    'dividend_amount': float(values['7. dividend amount']),
                    'split_coefficient': float(values['8. split coefficient'])
                })
            except (ValueError, KeyError) as e:
                print(f"Error parsing data for {symbol} on {date_str}: {e}")
                continue
        
        # Trier par date (plus récent en premier)
        parsed_data.sort(key=lambda x: x['date'], reverse=True)
        
        return parsed_data
    
    def parse_company_overview(self, data: Dict) -> Dict:
        """Parse les informations de l'entreprise"""
        if not data or 'Symbol' not in data:
            return {}
        
        try:
            return {
                'symbol': data.get('Symbol', ''),
                'name': data.get('Name', ''),
                'description': data.get('Description', ''),
                'exchange': data.get('Exchange', ''),
                'currency': data.get('Currency', ''),
                'country': data.get('Country', ''),
                'sector': data.get('Sector', ''),
                'industry': data.get('Industry', ''),
                'market_cap': int(data.get('MarketCapitalization', 0)) if data.get('MarketCapitalization', '').isdigit() else 0,
                'pe_ratio': float(data.get('PERatio', 0)) if data.get('PERatio', '') not in ['None', '-'] else 0,
                'dividend_yield': float(data.get('DividendYield', 0)) if data.get('DividendYield', '') not in ['None', '-'] else 0,
                'beta': float(data.get('Beta', 0)) if data.get('Beta', '') not in ['None', '-'] else 0,
                'week_52_high': float(data.get('52WeekHigh', 0)) if data.get('52WeekHigh', '') not in ['None', '-'] else 0,
                'week_52_low': float(data.get('52WeekLow', 0)) if data.get('52WeekLow', '') not in ['None', '-'] else 0
            }
        except (ValueError, TypeError) as e:
            print(f"Error parsing company overview: {e}")
            return {}

# Liste des symboles populaires pour les indices S&P 500 et Eurostoxx 600
SP500_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK.B', 'UNH', 'JNJ',
    'V', 'PG', 'JPM', 'HD', 'MA', 'NFLX', 'DIS', 'PYPL', 'ADBE', 'CRM',
    'NVDA', 'CMCSA', 'PFE', 'VZ', 'KO', 'NKE', 'WMT', 'MRK', 'T', 'PEP',
    'ABT', 'COST', 'TMO', 'AVGO', 'ACN', 'TXN', 'LLY', 'MDT', 'NEE', 'DHR'
]

EUROSTOXX_SYMBOLS = [
    'ASML.AS', 'SAP.DE', 'LVMH.PA', 'NESN.SW', 'INGA.AS', 'SIE.DE', 'TTE.PA',
    'OR.PA', 'MC.PA', 'AIR.PA', 'SAN.MC', 'IBE.MC', 'BNP.PA', 'ENEL.MI',
    'ADYEN.AS', 'SHELL.AS', 'DTE.DE', 'ALV.DE', 'BBVA.MC', 'ITX.MC'
]

