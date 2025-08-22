# Documentation des Templates - Système de Gestion de Commandes

## Vue d'ensemble

Ce document décrit l'architecture et l'utilisation des templates créés pour le système de gestion de commandes Commandly. L'interface utilisateur est construite avec Bootstrap 5 et utilise des composants réutilisables pour assurer une cohérence visuelle.

## Architecture des Templates

### Structure de Base

```
templates/
├── base/
│   └── base.html                 # Template de base avec Bootstrap 5
├── components/                   # Composants réutilisables
│   ├── navbar.html              # Barre de navigation principale
│   ├── footer.html              # Pied de page
│   ├── messages.html            # Affichage des messages flash
│   ├── pagination.html          # Composant de pagination
│   ├── search_form.html         # Formulaire de recherche générique
│   ├── action_buttons.html      # Boutons d'actions (CRUD)
│   └── status_badge.html        # Badges de statut dynamiques
└── [modules]/                   # Templates spécifiques par module
    └── templates/[module]/
        ├── [module]_list.html
        ├── [module]_detail.html
        ├── [module]_form.html
        └── [module]_confirm_delete.html
```

## Templates par Module

### 1. Dashboard (`dashboard/templates/dashboard/`)

#### `home.html`
- **Description** : Page d'accueil avec statistiques et actions rapides
- **Fonctionnalités** :
  - Cartes de statistiques avec gradients animés
  - Actions rapides vers les principales fonctionnalités
  - Commandes récentes et alertes
  - Design responsive avec animations CSS

### 2. Clients (`customers/templates/customers/`)

#### `customer_list.html`
- **Description** : Liste paginée des clients avec recherche avancée
- **Fonctionnalités** :
  - Statistiques en temps réel (total, actifs, entreprises, particuliers)
  - Formulaire de recherche avec filtres multiples
  - Vue tableau avec actions rapides
  - Pagination intelligente
  - Gestion du statut actif/inactif via AJAX

#### `customer_detail.html`
- **Description** : Profil détaillé d'un client
- **Fonctionnalités** :
  - En-tête avec gradient et informations principales
  - Onglets pour commandes, factures et paiements associés
  - Statistiques du client (total commandes, montant dépensé)
  - Actions contextuelles (modifier, activer/désactiver)

#### `customer_form.html`
- **Description** : Formulaire de création/modification de client
- **Fonctionnalités** :
  - Sections organisées (informations personnelles, contact, adresse)
  - Validation côté client avec JavaScript
  - Champ entreprise conditionnel selon le type de client
  - Aide contextuelle et validation du format téléphone sénégalais

#### `customer_confirm_delete.html`
- **Description** : Page de confirmation de suppression
- **Fonctionnalités** :
  - Vérification des dépendances (commandes, factures, paiements)
  - Alternative de désactivation si suppression impossible
  - Double confirmation avec saisie de texte

### 3. Produits (`products/templates/products/`)

#### `product_list.html`
- **Description** : Catalogue des produits avec gestion du stock
- **Fonctionnalités** :
  - Statistiques détaillées (total, actifs, stock faible, ruptures)
  - Recherche avancée par nom, SKU, catégorie, prix, stock
  - Vue tableau et vue cartes commutable
  - Indicateurs visuels de stock (couleurs)
  - Actions rapides avec gestion du statut

#### `product_detail.html`
- **Description** : Fiche produit complète
- **Fonctionnalités** :
  - Informations produit avec image placeholder
  - Gestion du stock pour produits physiques
  - Modal de mise à jour rapide du stock
  - Historique des commandes contenant le produit
  - Statistiques de vente

#### `product_form.html`
- **Description** : Formulaire produit/service
- **Fonctionnalités** :
  - Sections adaptatives (stock masqué pour services)
  - Validation des prix et quantités
  - Auto-formatage des champs numériques
  - Aide contextuelle selon le type de produit

#### `category_list.html`
- **Description** : Gestion des catégories de produits
- **Fonctionnalités** :
  - Vue grille avec cartes visuelles
  - Vue tableau alternative
  - Compteur de produits par catégorie
  - Actions conditionnelles (suppression si vide)

### 4. Commandes (`orders/templates/orders/`)

#### `order_list.html`
- **Description** : Suivi des commandes clients
- **Fonctionnalités** :
  - Statistiques par statut avec code couleur
  - Changement de statut direct depuis la liste
  - Recherche par numéro, client, statut, période
  - Affichage du montant total et date de livraison
  - Menu déroulant pour changement de statut rapide

### 5. Factures (`invoices/templates/invoices/`)

#### `invoice_list.html`
- **Description** : Gestion des factures et encaissements
- **Fonctionnalités** :
  - Statistiques financières (total, payé, reste à payer)
  - Badges de statut colorés selon l'état de paiement
  - Liens vers génération PDF
  - Tri par date et échéance

### 6. Paiements (`payments/templates/payments/`)

#### `payment_list.html`
- **Description** : Suivi des encaissements
- **Fonctionnalités** :
  - Statistiques globales des paiements
  - Affichage des méthodes de paiement
  - Liens vers factures associées
  - Références de paiement en police monospace

## Composants Réutilisables

### 1. `pagination.html`
- **Usage** : `{% include 'components/pagination.html' with page_obj=page_obj %}`
- **Fonctionnalités** :
  - Navigation intelligente avec ellipses
  - Préservation des paramètres de recherche
  - Informations contextuelles (page X sur Y)
  - Design responsive

### 2. `search_form.html`
- **Usage** : `{% include 'components/search_form.html' with form=search_form action_url='module:list_view' %}`
- **Fonctionnalités** :
  - Génération automatique des champs
  - Résumé des filtres actifs avec suppression individuelle
  - Boutons de recherche et d'effacement
  - Style cohérent avec validation

### 3. `action_buttons.html`
- **Usage** : `{% include 'components/action_buttons.html' with object=item actions='view,edit,delete' module='customers' %}`
- **Actions supportées** :
  - `view` : Voir les détails
  - `edit` : Modifier
  - `delete` : Supprimer
  - `toggle` : Activer/désactiver
  - `duplicate` : Dupliquer
  - `pdf` : Générer PDF
  - `email` : Envoyer par email
  - `print` : Imprimer
  - `export` : Menu d'export (PDF, Excel, CSV)

### 4. `status_badge.html`
- **Usage** : `{% include 'components/status_badge.html' with status=object.status type='order' %}`
- **Types supportés** :
  - `order` : Statuts de commande
  - `invoice` : Statuts de facture
  - `payment` : Statuts de paiement
  - `customer` : Statuts client
  - `product` : Statuts produit
  - `stock` : Niveaux de stock
  - `priority` : Niveaux de priorité

## Fonctionnalités Transversales

### Design System

1. **Couleurs et Gradients** :
   - Gradients animés pour les cartes importantes
   - Palette de couleurs cohérente basée sur Bootstrap
   - Codes couleur spécifiques par statut

2. **Animations** :
   - Hover effects sur les cartes et boutons
   - Animations d'apparition au scroll
   - Transitions fluides sur les changements d'état

3. **Responsive Design** :
   - Grilles adaptatives Bootstrap
   - Composants optimisés mobile
   - Navigation collapsed sur petits écrans

### JavaScript et Interactivité

1. **AJAX** :
   - Changement de statut sans rechargement
   - Mise à jour des stocks
   - Recherche en temps réel

2. **Validation** :
   - Validation côté client des formulaires
   - Formatage automatique des champs
   - Messages d'erreur contextuels

3. **UX** :
   - Confirmations de suppression renforcées
   - Tooltips informatifs
   - Indicateurs de chargement

## Personnalisation

### Ajout d'un Nouveau Module

1. Créer le dossier `templates/[module]/`
2. Implémenter les templates de base :
   - `[module]_list.html`
   - `[module]_detail.html`
   - `[module]_form.html`
   - `[module]_confirm_delete.html`
3. Utiliser les composants réutilisables
4. Ajouter les liens dans la navbar

### Modification des Styles

1. Les styles sont définis dans chaque template via `{% block extra_css %}`
2. Utiliser les classes Bootstrap comme base
3. Ajouter des styles personnalisés pour les spécificités

### Extension des Composants

1. Les composants acceptent des paramètres pour la personnalisation
2. Possibilité d'override via les templates enfants
3. JavaScript modulaire pour les fonctionnalités avancées

## Bonnes Pratiques

1. **Réutilisabilité** : Utiliser les composants partagés
2. **Cohérence** : Suivre les patterns établis
3. **Performance** : Optimiser les images et CSS
4. **Accessibilité** : Utiliser les attributs ARIA et la navigation au clavier
5. **SEO** : Titres de page descriptifs et structure sémantique

## Maintenance

1. **Mise à jour Bootstrap** : Vérifier la compatibilité des composants
2. **Tests** : Valider sur différents navigateurs et tailles d'écran
3. **Documentation** : Maintenir cette documentation à jour
4. **Performance** : Optimiser régulièrement les assets CSS/JS
