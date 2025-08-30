# Documentation Utilisateur - Application Screening Actions

## Vue d'ensemble

L'application **Screening Actions** permet de rechercher et filtrer les actions des indices **Eurostoxx 600** et **S&P 500** selon différents critères financiers. L'objectif principal est d'identifier les actions dont le cours actuel est inférieur à un certain pourcentage de leur plus haut historique sur une période donnée.

## URL de l'application

🌐 **Application déployée** : https://y0h0i3cmozq5.manus.space

## Fonctionnalités principales

### 1. Filtres de recherche

#### Indices
- **S&P 500** : Indice des 500 plus grandes entreprises américaines
- **Eurostoxx 600** : Indice des 600 plus grandes entreprises européennes
- Possibilité de sélectionner un ou plusieurs indices

#### Période Lookback
- **1 an** : Recherche du plus haut sur les 12 derniers mois
- **3 ans** : Recherche du plus haut sur les 36 derniers mois
- **5 ans** : Recherche du plus haut sur les 60 derniers mois (par défaut)
- **10 ans** : Recherche du plus haut sur les 120 derniers mois

#### Seuil (% du plus haut)
- Définit le pourcentage maximum du plus haut historique
- Par défaut : 50% (actions à moins de 50% de leur plus haut)
- Exemple : Si une action a atteint 100€ et vaut actuellement 40€, elle est à 40% de son plus haut

#### Critères additionnels
- **Capitalisation minimale** : Filtre par taille d'entreprise (en USD)
- **Volume minimal quotidien** : Filtre par liquidité des actions
- **Tri** : Organise les résultats par % du plus haut, capitalisation ou prix actuel

### 2. Tableau de résultats

Le tableau affiche pour chaque action trouvée :
- **Ticker** : Code boursier de l'action
- **Nom** : Nom complet de l'entreprise
- **Pays** : Pays de domiciliation
- **Secteur** : Secteur d'activité (GICS)
- **Prix** : Prix actuel de l'action
- **% du plus haut** : Pourcentage du plus haut historique (indicateur clé)

### 3. Export des données

- **Export CSV** : Télécharge les résultats au format CSV
- Compatible avec Excel, Google Sheets et autres tableurs
- Contient toutes les colonnes visibles dans le tableau

### 4. Authentification et sauvegarde

#### Inscription
- Créez un compte avec nom d'utilisateur, email et mot de passe
- Permet de sauvegarder vos recherches favorites

#### Connexion
- Accédez à vos recherches sauvegardées
- Gérez vos critères de recherche personnalisés

#### Recherches sauvegardées
- Sauvegardez vos combinaisons de filtres favorites
- Rechargez rapidement vos recherches précédentes
- Supprimez les recherches obsolètes

## Guide d'utilisation

### Recherche simple

1. **Sélectionnez les indices** : Cochez S&P 500 et/ou Eurostoxx 600
2. **Choisissez la période** : Sélectionnez 1, 3, 5 ou 10 ans
3. **Définissez le seuil** : Entrez le pourcentage maximum (ex: 50)
4. **Lancez la recherche** : Cliquez sur "Lancer la recherche"
5. **Analysez les résultats** : Consultez le tableau des actions trouvées

### Recherche avancée

1. **Ajoutez des filtres** :
   - Capitalisation minimale (ex: 1000000000 pour 1 milliard USD)
   - Volume minimal quotidien (ex: 100000 pour 100k actions/jour)
2. **Choisissez le tri** : Organisez par % du plus haut, capitalisation ou prix
3. **Exportez les données** : Cliquez sur "Exporter CSV" pour télécharger

### Gestion des recherches

1. **Créez un compte** : Cliquez sur "Connexion" puis "Inscription"
2. **Sauvegardez une recherche** :
   - Configurez vos filtres
   - Connectez-vous à votre compte
   - Donnez un nom à votre recherche et sauvegardez
3. **Rechargez une recherche** : Sélectionnez dans vos recherches sauvegardées

## Exemples d'utilisation

### Recherche d'opportunités de valeur
- **Objectif** : Trouver des actions de qualité temporairement dépréciées
- **Configuration** :
  - Indices : S&P 500 + Eurostoxx 600
  - Période : 5 ans
  - Seuil : 60% du plus haut
  - Capitalisation min : 5 milliards USD
  - Volume min : 500 000

### Recherche d'actions en forte baisse
- **Objectif** : Identifier les actions ayant le plus chuté
- **Configuration** :
  - Indices : S&P 500
  - Période : 3 ans
  - Seuil : 30% du plus haut
  - Tri : % du plus haut (croissant)

### Screening sectoriel
- **Objectif** : Analyser un secteur spécifique
- **Configuration** :
  - Indices : Eurostoxx 600
  - Période : 1 an
  - Seuil : 70% du plus haut
  - Filtrer manuellement par secteur dans les résultats

## Limitations et notes importantes

### Données
- Les données sont mises à jour quotidiennement
- Les prix sont ajustés pour les splits et dividendes
- Les constituants des indices peuvent évoluer

### Performance
- Les recherches complexes peuvent prendre quelques secondes
- Limitez les critères pour des résultats plus rapides
- L'export CSV est limité aux résultats affichés

### Utilisation responsable
- Cette application est un outil d'aide à la décision
- Ne constitue pas un conseil en investissement
- Toujours effectuer ses propres analyses avant d'investir
- Les performances passées ne préjugent pas des performances futures

## Support technique

Pour toute question ou problème technique :
- Vérifiez votre connexion internet
- Actualisez la page en cas de problème d'affichage
- Les recherches sans résultats peuvent indiquer des critères trop restrictifs

## Évolutions futures

Fonctionnalités prévues :
- Alertes email automatiques
- Graphiques de performance
- Filtres sectoriels avancés
- Données fondamentales (P/E, dette, etc.)
- API publique pour développeurs

