# 🚀 Commandly - Système de Gestion de Commandes (MVP)

## 📋 Description

Commandly est un système de gestion de commandes développé avec Django, conçu pour gérer efficacement les commandes, clients, produits, factures et paiements d'une entreprise.

## 🎯 Fonctionnalités du MVP

### ✅ **Fonctionnalités implémentées**
- [x] Structure du projet Django avec applications modulaires
- [x] Interface utilisateur avec Bootstrap 5
- [x] Système d'authentification de base
- [x] Navigation et composants réutilisables
- [x] Tableau de bord avec statistiques
- [x] Architecture des vues pour toutes les applications

### 🔄 **Fonctionnalités en cours de développement**
- [ ] Modèles de données (CustomUser, Product, Customer, Order, Invoice, Payment)
- [ ] Formulaires CRUD pour chaque entité
- [ ] Templates pour toutes les vues
- [ ] Logique métier et validation
- [ ] Gestion des statuts et workflows
- [ ] Export PDF des factures

### 🚀 **Fonctionnalités prévues après MVP**
- [ ] Gestion avancée des stocks
- [ ] Intégration paiements en ligne
- [ ] Système de devis
- [ ] Rapports financiers avancés
- [ ] Multi-devises et multilingue
- [ ] Portail client

## 🏗️ Architecture du projet

```
gestion-commande/
├── commandly/                 # Configuration principale Django
│   ├── settings.py           # Paramètres du projet
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # Configuration WSGI
├── users/                     # Gestion des utilisateurs
│   ├── models/               # Modèles utilisateurs
│   ├── views/                # Vues d'authentification
│   ├── forms/                # Formulaires utilisateurs
│   └── templates/            # Templates utilisateurs
├── products/                  # Catalogue des produits
│   ├── models/               # Modèles produits
│   ├── views/                # Vues CRUD produits
│   ├── forms/                # Formulaires produits
│   └── templates/            # Templates produits
├── customers/                 # Gestion des clients
│   ├── models/               # Modèles clients
│   ├── views/                # Vues CRUD clients
│   ├── forms/                # Formulaires clients
│   └── templates/            # Templates clients
├── orders/                    # Gestion des commandes
│   ├── models/               # Modèles commandes
│   ├── views/                # Vues CRUD commandes
│   ├── forms/                # Formulaires commandes
│   └── templates/            # Templates commandes
├── invoices/                  # Gestion des factures
│   ├── models/               # Modèles factures
│   ├── views/                # Vues CRUD factures
│   ├── forms/                # Formulaires factures
│   └── templates/            # Templates factures
├── payments/                  # Gestion des paiements
│   ├── models/               # Modèles paiements
│   ├── views/                # Vues CRUD paiements
│   ├── forms/                # Formulaires paiements
│   └── templates/            # Templates paiements
├── dashboard/                 # Tableau de bord
│   ├── views/                # Vues du dashboard
│   └── templates/            # Templates du dashboard
├── templates/                 # Templates globaux
│   ├── base/                 # Template de base
│   └── components/           # Composants réutilisables
├── manage.py                  # Script de gestion Django
└── requirements.txt           # Dépendances Python
```

## 🛠️ Technologies utilisées

- **Backend :** Django 5.2.5
- **Frontend :** Bootstrap 5.3.0
- **Base de données :** SQLite (développement)
- **Authentification :** Django Auth System
- **Templates :** Django Template Language
- **Icons :** Bootstrap Icons

## 🚀 Installation et démarrage

### Prérequis
- Python 3.8+
- pip

### Installation
1. Cloner le projet
```bash
git clone <repository-url>
cd gestion-commande
```

2. Créer un environnement virtuel
```bash
python -m venv env
```

3. Activer l'environnement virtuel
```bash
# Windows
env\Scripts\activate

# Linux/Mac
source env/bin/activate
```

4. Installer les dépendances
```bash
pip install -r requirements.txt
```

5. Effectuer les migrations
```bash
python manage.py migrate
```

6. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

7. Lancer le serveur de développement
```bash
python manage.py runserver
```

8. Accéder à l'application
```
http://localhost:8000/
```

## 📱 Utilisation

### Connexion
- Accédez à `/users/login/` pour vous connecter
- Utilisez les identifiants du superutilisateur créé

### Navigation
- **Tableau de bord :** Vue d'ensemble et statistiques
- **Produits :** Gestion du catalogue
- **Clients :** Gestion de la clientèle
- **Commandes :** Suivi des commandes
- **Factures :** Gestion de la facturation
- **Paiements :** Suivi des paiements

## 🔧 Développement

### Structure des fichiers
- **Modèles :** Définis dans `app/models/`
- **Vues :** Définies dans `app/views/`
- **Formulaires :** Définis dans `app/forms/`
- **Templates :** Stockés dans `app/templates/`

### Conventions de nommage
- **Modèles :** PascalCase (ex: `Product`, `Customer`)
- **Vues :** PascalCase avec suffixe View (ex: `ProductListView`)
- **URLs :** snake_case (ex: `product_list`, `customer_create`)
- **Templates :** snake_case.html (ex: `product_list.html`)

### Ajout de nouvelles fonctionnalités
1. Créer les modèles dans `app/models/`
2. Créer les vues dans `app/views/`
3. Créer les formulaires dans `app/forms/`
4. Créer les templates dans `app/templates/`
5. Ajouter les URLs dans `app/urls.py`
6. Tester et valider

## 📊 État du projet

- **Phase actuelle :** MVP - Structure et architecture
- **Prochaine étape :** Implémentation des modèles de données
- **Progression :** 25% (Structure de base terminée)

## 🤝 Contribution

Ce projet suit les règles suivantes :
- Code modulaire et bien structuré
- Utilisation de Bootstrap pour l'interface
- Formulaires Django (Form/ModelForm)
- Templates réutilisables et composants
- Limite de 500 lignes par fichier
- Code simple et maintenable

## 📝 Licence

Ce projet est développé dans le cadre d'un cours DIT.

---

**Développé avec ❤️ et Django**
