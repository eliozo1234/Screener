# Conception de l'architecture de l'application Screening Actions

## 1. Architecture Générale

L'application "Screening Actions" sera conçue selon une architecture client-serveur, avec un frontend web interactif, un backend API robuste et une base de données relationnelle pour le stockage des données financières. Cette approche modulaire permettra une meilleure scalabilité, maintenabilité et flexibilité pour l'intégration future de nouvelles fonctionnalités.

### Composants Principaux :

*   **Frontend (Interface Utilisateur)** : Une application web basée sur React, offrant une interface riche et réactive pour les utilisateurs. Elle communiquera avec le backend via des appels API RESTful.
*   **Backend (API)** : Une API RESTful développée avec Flask (Python), responsable de la logique métier, de l'accès aux données, de l'exécution des screenings et de la gestion des utilisateurs. Elle exposera des endpoints pour la recherche, la sauvegarde des préférences, et potentiellement la gestion des alertes.
*   **Base de Données** : Une base de données PostgreSQL sera utilisée pour stocker les données historiques des cours ajustés, les métadonnées des actions (tickers, ISIN, nom, pays, secteur, market cap), les préférences de recherche des utilisateurs et les résultats des screenings.
*   **Moteur d'Ingestion de Données** : Un script Python indépendant (ou un service planifié) sera chargé de l'ingestion quotidienne des données financières provenant de fournisseurs tiers (APIs de données financières).

## 2. Flux de Données

1.  **Ingestion Quotidienne** : Le moteur d'ingestion récupère les cours ajustés et les constituants des indices (Eurostoxx 600, S&P 500) auprès des fournisseurs de données (ex: Alpha Vantage, Polygon, Finnhub) et les stocke dans la base de données.
2.  **Requête Utilisateur** : L'utilisateur interagit avec l'interface frontend pour définir ses critères de screening (indices, lookback, seuil %, pays, secteur, market cap, volume moyen, etc.).
3.  **Appel API Frontend-Backend** : Le frontend envoie une requête POST à l'API backend avec les critères de screening.
4.  **Traitement Backend** : Le backend reçoit la requête, interroge la base de données pour récupérer les données nécessaires, effectue les calculs (plus haut lookback, % du plus haut) et applique les filtres.
5.  **Réponse API Backend-Frontend** : Le backend renvoie les résultats du screening au frontend sous forme de JSON.
6.  **Affichage Frontend** : Le frontend affiche les résultats dans un tableau interactif, permettant le tri et l'exportation.
7.  **Gestion des Utilisateurs et Sauvegarde** : Les utilisateurs peuvent s'authentifier (simple authentification) et sauvegarder leurs recherches, qui sont stockées dans la base de données via l'API backend.
8.  **Alertes (Future)** : Un service d'alerte indépendant (potentiellement un autre script Python ou un microservice) interrogera périodiquement la base de données et enverra des notifications (email/push) si les conditions définies par l'utilisateur sont remplies.

## 3. Technologies Choisies

*   **Frontend** : React.js (avec Create React App pour le scaffolding initial)
*   **Backend** : Flask (Python) avec Flask-RESTful pour les APIs et SQLAlchemy pour l'ORM.
*   **Base de Données** : PostgreSQL
*   **Ingestion de Données** : Python (scripts avec bibliothèques `requests` et `pandas`)
*   **Fournisseurs de Données** : Alpha Vantage, Polygon.io, Finnhub (à évaluer plus en détail pour la couverture des indices et les limites d'utilisation).
*   **Authentification** : Simple système basé sur des tokens (Flask-Login ou équivalent).
*   **Déploiement** : Docker pour la conteneurisation, potentiellement un service cloud (ex: Google Cloud Run, AWS Elastic Beanstalk) pour le déploiement final.



## 4. Modèle de Données Détaillé

Le modèle de données sera structuré autour de plusieurs tables principales pour gérer les informations sur les actions, les prix historiques, les recherches des utilisateurs et les résultats des screenings.

### 4.1. Table `tickers`

Cette table stockera les métadonnées de base pour chaque action.

| Colonne           | Type de Données | Description                                     | Contraintes         |
| :---------------- | :-------------- | :---------------------------------------------- | :------------------ |
| `id`              | INTEGER         | Clé primaire, identifiant unique de l'action    | PRIMARY KEY, AUTOINC |
| `ticker`          | VARCHAR(10)     | Symbole boursier de l'action (ex: AAPL, ABC.DE) | UNIQUE, NOT NULL    |
| `isin`            | VARCHAR(12)     | Code ISIN de l'action (si disponible)          | UNIQUE, NULLABLE    |
| `name`            | VARCHAR(255)    | Nom complet de l'entreprise                     | NOT NULL            |
| `country`         | VARCHAR(50)     | Pays du siège social de l'entreprise            | NOT NULL            |
| `sector`          | VARCHAR(100)    | Secteur GICS de l'entreprise                    | NOT NULL            |
| `market_cap`      | BIGINT          | Capitalisation boursière actuelle (en USD)      | NULLABLE            |
| `currency`        | VARCHAR(3)      | Devise de cotation (ex: USD, EUR)               | NOT NULL            |
| `exchange`        | VARCHAR(10)     | Bourse principale de cotation                   | NOT NULL            |
| `ipo_date`        | DATE            | Date d'introduction en bourse                   | NULLABLE            |
| `is_suspended`    | BOOLEAN         | Indique si l'action est suspendue               | DEFAULT FALSE       |

### 4.2. Table `prices`

Cette table stockera les cours ajustés quotidiens pour chaque action.

| Colonne           | Type de Données | Description                                     | Contraintes         |
| :---------------- | :-------------- | :---------------------------------------------- | :------------------ |
| `ticker_id`       | INTEGER         | Clé étrangère vers la table `tickers`          | FOREIGN KEY         |
| `date`            | DATE            | Date du cours                                   | NOT NULL            |
| `adjusted_close`  | NUMERIC(18, 4)  | Prix de clôture ajusté (splits/dividendes)      | NOT NULL            |
| `volume`          | BIGINT          | Volume de transactions quotidien                | NOT NULL            |
| `high`            | NUMERIC(18, 4)  | Plus haut du jour                               | NOT NULL            |
| `low`             | NUMERIC(18, 4)  | Plus bas du jour                                | NOT NULL            |
| `open`            | NUMERIC(18, 4)  | Prix d'ouverture du jour                        | NOT NULL            |
| `timestamp`       | TIMESTAMP       | Horodatage de l'enregistrement                  | DEFAULT NOW()       |

**Clé Primaire Composée** : (`ticker_id`, `date`)

### 4.3. Table `users`

Cette table gérera les informations des utilisateurs pour l'authentification et la sauvegarde des recherches.

| Colonne           | Type de Données | Description                                     | Contraintes         |
| :---------------- | :-------------- | :---------------------------------------------- | :------------------ |
| `id`              | INTEGER         | Clé primaire, identifiant unique de l'utilisateur | PRIMARY KEY, AUTOINC |
| `username`        | VARCHAR(50)     | Nom d'utilisateur                               | UNIQUE, NOT NULL    |
| `password_hash`   | VARCHAR(255)    | Hash du mot de passe                            | NOT NULL            |
| `email`           | VARCHAR(255)    | Adresse email de l'utilisateur                  | UNIQUE, NOT NULL    |
| `created_at`      | TIMESTAMP       | Date de création du compte                      | DEFAULT NOW()       |

### 4.4. Table `saved_searches`

Cette table stockera les paramètres des recherches sauvegardées par les utilisateurs.

| Colonne           | Type de Données | Description                                     | Contraintes         |
| :---------------- | :-------------- | :---------------------------------------------- | :------------------ |
| `id`              | INTEGER         | Clé primaire, identifiant unique de la recherche | PRIMARY KEY, AUTOINC |
| `user_id`         | INTEGER         | Clé étrangère vers la table `users`            | FOREIGN KEY         |
| `name`            | VARCHAR(255)    | Nom donné à la recherche sauvegardée            | NOT NULL            |
| `parameters`      | JSONB           | Paramètres de la recherche (format JSON)        | NOT NULL            |
| `created_at`      | TIMESTAMP       | Date de sauvegarde de la recherche              | DEFAULT NOW()       |

### 4.5. Table `screening_results`

Cette table pourrait être utilisée pour stocker les résultats des screenings pour des raisons de performance ou d'historisation, bien que le MVP puisse calculer les résultats à la volée.

| Colonne           | Type de Données | Description                                     | Contraintes         |
| :---------------- | :-------------- | :---------------------------------------------- | :------------------ |
| `search_id`       | INTEGER         | Clé étrangère vers la table `saved_searches`   | FOREIGN KEY         |
| `ticker_id`       | INTEGER         | Clé étrangère vers la table `tickers`          | FOREIGN KEY         |
| `run_date`        | DATE            | Date d'exécution du screening                   | NOT NULL            |
| `pct_of_high`     | NUMERIC(5, 2)   | Pourcentage du plus haut lookback               | NOT NULL            |
| `lookback_high`   | NUMERIC(18, 4)  | Plus haut atteint sur la période lookback       | NOT NULL            |
| `lookback_high_date` | DATE            | Date du plus haut lookback                      | NOT NULL            |
| `current_price`   | NUMERIC(18, 4)  | Prix actuel de l'action                         | NOT NULL            |

**Clé Primaire Composée** : (`search_id`, `ticker_id`, `run_date`)

## 5. Technologies pour la Base de Données et l'Ingestion

*   **Base de Données** : PostgreSQL est choisi pour sa robustesse, sa conformité ACID, sa capacité à gérer de grands volumes de données et son support natif du type `JSONB` pour les paramètres de recherche.
*   **ORM** : SQLAlchemy sera utilisé côté Flask pour interagir avec la base de données, offrant une abstraction et une flexibilité pour les requêtes.
*   **Ingestion de Données** : Les scripts Python utiliseront la bibliothèque `psycopg2` (ou via SQLAlchemy Core) pour l'insertion efficace des données dans PostgreSQL. Les bibliothèques `requests` et `pandas` seront essentielles pour la récupération et la manipulation des données provenant des APIs financières.

Cette conception fournit une base solide pour le développement de l'application, en tenant compte des exigences de performance, de scalabilité et de maintenabilité.

