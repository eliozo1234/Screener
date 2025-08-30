# Documentation Technique - Application Screening Actions

## Architecture générale

L'application **Screening Actions** est une application web full-stack composée de :

- **Frontend** : React.js avec interface utilisateur moderne
- **Backend** : Flask (Python) avec API REST
- **Base de données** : SQLite (développement) / PostgreSQL (production)
- **Déploiement** : Application unifiée déployée sur Manus

## URL de l'application

🌐 **Application déployée** : https://y0h0i3cmozq5.manus.space

## Structure du projet

```
screening_actions_api/
├── src/
│   ├── main.py                 # Point d'entrée Flask
│   ├── models/                 # Modèles de données SQLAlchemy
│   │   ├── ticker.py          # Modèle Ticker
│   │   ├── price.py           # Modèle Price
│   │   ├── user.py            # Modèle User
│   │   └── saved_search.py    # Modèle SavedSearch
│   ├── routes/                # Routes API
│   │   ├── screening.py       # Endpoints de screening
│   │   └── auth.py           # Endpoints d'authentification
│   ├── static/               # Frontend React buildé
│   └── data_loader.py        # Script de chargement des données
├── requirements.txt          # Dépendances Python
└── venv/                    # Environnement virtuel
```

## Modèle de données

### Ticker
```python
class Ticker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100))
    sector = db.Column(db.String(100))
    market_cap = db.Column(db.BigInteger)
    currency = db.Column(db.String(10))
    exchange = db.Column(db.String(50))
    index_membership = db.Column(db.String(100))  # sp500, eurostoxx600
```

### Price
```python
class Price(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker_id = db.Column(db.Integer, db.ForeignKey('ticker.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    adjusted_close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.BigInteger)
```

### User
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
```

### SavedSearch
```python
class SavedSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    search_params = db.Column(db.Text, nullable=False)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## API REST

### Endpoints de screening

#### POST /api/search
Effectue une recherche d'actions selon les critères spécifiés.

**Paramètres de requête :**
```json
{
  "indices": ["sp500", "eurostoxx600"],
  "lookback_years": 5,
  "threshold_pct": 50,
  "min_market_cap": 1000000000,
  "min_avg_volume": 100000,
  "sort_by": "pct_of_high"
}
```

**Réponse :**
```json
{
  "results": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "country": "United States",
      "sector": "Technology",
      "current_price": 150.25,
      "pct_of_high": 85.3,
      "lookback_high": 176.15,
      "lookback_high_date": "2023-01-15",
      "market_cap": 2500000000000,
      "avg_volume_30d": 75000000,
      "currency": "USD",
      "exchange": "NASDAQ"
    }
  ],
  "total_count": 1,
  "search_params": {...}
}
```

### Endpoints d'authentification

#### POST /api/auth/register
Inscription d'un nouvel utilisateur.

#### POST /api/auth/login
Connexion d'un utilisateur existant.

#### POST /api/auth/logout
Déconnexion de l'utilisateur actuel.

#### GET /api/auth/me
Récupération des informations de l'utilisateur connecté.

#### GET /api/auth/saved-searches
Récupération des recherches sauvegardées de l'utilisateur.

#### POST /api/auth/saved-searches
Sauvegarde d'une nouvelle recherche.

#### DELETE /api/auth/saved-searches/{id}
Suppression d'une recherche sauvegardée.

## Algorithme de screening

### Calcul du pourcentage du plus haut

```python
def calculate_pct_of_high(ticker_id, lookback_years, current_date):
    # 1. Récupérer les prix sur la période lookback
    start_date = current_date - timedelta(days=lookback_years * 365)
    prices = Price.query.filter(
        Price.ticker_id == ticker_id,
        Price.date >= start_date,
        Price.date <= current_date
    ).all()
    
    # 2. Trouver le plus haut et le prix actuel
    lookback_high = max(price.adjusted_close for price in prices)
    current_price = prices[-1].adjusted_close  # Prix le plus récent
    
    # 3. Calculer le pourcentage
    pct_of_high = (current_price / lookback_high) * 100
    
    return {
        'current_price': current_price,
        'lookback_high': lookback_high,
        'pct_of_high': pct_of_high,
        'lookback_high_date': date_of_high
    }
```

### Filtrage et tri

```python
def apply_filters(results, filters):
    filtered = []
    
    for result in results:
        # Filtre par seuil
        if result['pct_of_high'] > filters['threshold_pct']:
            continue
            
        # Filtre par capitalisation
        if filters.get('min_market_cap') and result['market_cap'] < filters['min_market_cap']:
            continue
            
        # Filtre par volume
        if filters.get('min_avg_volume') and result['avg_volume_30d'] < filters['min_avg_volume']:
            continue
            
        filtered.append(result)
    
    # Tri des résultats
    sort_key = filters.get('sort_by', 'pct_of_high')
    reverse = sort_key in ['market_cap', 'current_price']
    
    return sorted(filtered, key=lambda x: x[sort_key], reverse=reverse)
```

## Frontend React

### Structure des composants

```
src/
├── App.jsx                    # Composant principal
├── components/
│   ├── SearchFilters.jsx     # Filtres de recherche
│   ├── ResultsTable.jsx      # Tableau de résultats
│   ├── AuthModal.jsx         # Modal d'authentification
│   └── SavedSearches.jsx     # Gestion des recherches sauvegardées
└── App.css                   # Styles CSS
```

### Gestion d'état

L'application utilise les hooks React pour la gestion d'état :

```javascript
const [results, setResults] = useState([])
const [isLoading, setIsLoading] = useState(false)
const [user, setUser] = useState(null)
const [currentFilters, setCurrentFilters] = useState({})
const [searchParams, setSearchParams] = useState({})
```

### Communication avec l'API

```javascript
const handleSearch = async (filters) => {
  setIsLoading(true)
  setCurrentFilters(filters)
  setSearchParams(filters)
  
  try {
    const response = await fetch('/api/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(filters),
    })
    
    if (response.ok) {
      const data = await response.json()
      setResults(data.results)
    }
  } catch (error) {
    console.error('Erreur lors de la recherche:', error)
  } finally {
    setIsLoading(false)
  }
}
```

## Déploiement

### Configuration de production

```python
# main.py
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### Build du frontend

```bash
cd screening-actions-frontend
pnpm run build
cp -r dist/* ../screening_actions_api/src/static/
```

### Dépendances

```txt
# requirements.txt
Flask==3.1.1
flask-cors==6.0.0
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.41
Werkzeug==3.1.3
```

## Données de test

L'application inclut des données de test pour démonstration :

```python
# Exemples d'actions avec données réalistes
test_tickers = [
    {
        'ticker': 'AAPL',
        'name': 'Apple Inc.',
        'country': 'United States',
        'sector': 'Technology',
        'market_cap': 2800000000000,
        'index_membership': 'sp500'
    },
    # ... autres actions
]
```

## Performance et optimisation

### Indexation de la base de données

```sql
CREATE INDEX idx_price_ticker_date ON price(ticker_id, date);
CREATE INDEX idx_ticker_index ON ticker(index_membership);
CREATE INDEX idx_price_date ON price(date);
```

### Mise en cache

- Les résultats de recherche peuvent être mis en cache côté client
- Les données de prix sont mises à jour quotidiennement
- Utilisation de SQLAlchemy pour l'optimisation des requêtes

### Limitations actuelles

- Base de données SQLite pour le développement (limites de concurrence)
- Données de test limitées (8 actions)
- Pas de mise à jour automatique des données en temps réel
- Authentification basique sans JWT

## Évolutions techniques prévues

### Court terme
- Migration vers PostgreSQL en production
- Ajout de tests unitaires et d'intégration
- Amélioration de la gestion d'erreurs
- Logging structuré

### Moyen terme
- Authentification JWT
- API de données financières en temps réel
- Cache Redis pour les performances
- Monitoring et métriques

### Long terme
- Microservices pour la scalabilité
- Pipeline CI/CD automatisé
- Containerisation Docker
- API publique documentée avec OpenAPI

## Sécurité

### Mesures implémentées
- Hachage des mots de passe avec Werkzeug
- Validation des entrées utilisateur
- CORS configuré pour la sécurité
- Sessions sécurisées Flask

### Améliorations futures
- Authentification à deux facteurs
- Rate limiting sur les API
- Chiffrement des données sensibles
- Audit trail des actions utilisateur

## Monitoring et logs

### Logs applicatifs
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/search', methods=['POST'])
def search():
    logger.info(f"Search request: {request.json}")
    # ... traitement
    logger.info(f"Search completed: {len(results)} results")
```

### Métriques de performance
- Temps de réponse des API
- Nombre de requêtes par minute
- Taux d'erreur
- Utilisation mémoire et CPU

