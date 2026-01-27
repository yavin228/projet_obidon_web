#  Dashboard Admin Obidon - Guide de Démarrage

##  Base de Données Remplie

Félicitations! Votre base de données a été remplie avec des données de test complètes:

### Données Créées:
- **6 Catégories**: Cafés Arabes, Cafés dosses Français, Pains Complets, Machines Automatiques, Machines Manuelles
- **8 Produits**: Café Arabica Premium, Café Robusta, Pain Baguette, Machines Espresso, etc.
- **5 Commandes**: Avec détails complets (client, articles, montants, statuts)
- **Avis Clients**: Notes 4-5 étoiles avec commentaires

---

##  Accès Admin

### Compte Superuser
```
Email: admin@obidon.com
Mot de passe: admin123
```

### URLs d'Accès:
1. **Dashboard Custom** (Recommandé): http://localhost:8000/admin-dashboard/
   - Statistiques en temps réel
   - Graphiques et analytics
   - Vue d'ensemble complète

2. **Admin Django Standard**: http://localhost:8000/admin/
   - Gestion complète des modèles
   - Plus de contrôle détaillé
   - Configuration avancée

---

##  Dashboard Features

### Page Principale
- **Cartes Statistiques**: Produits, Catégories, Utilisateurs, Commandes, Revenu Total, Commandes En Attente
- **Commandes Récentes**: Tableau des 5 dernières commandes
- **Produits Populaires**: Produits avec le plus de commandes
- **Avis Récents**: Derniers avis clients
- **Statut des Commandes**: Graphique par statut (En attente, Confirmée, Expédiée, Livrée)
- **Revenu du Mois**: Montant total du mois courant

### Page Analytics
- **Metrics Clés**: Total clients, nouveaux clients, panier moyen
- **Produits Mieux Notés**: Classement par note (⭐)
- **Produits Commentés**: Classement par nombre d'avis
- **Conseils de Performance**: Tips pour optimiser les ventes

---

##  Gestion Admin Django

### Sections Disponibles:

#### 1. **Produits** (`/admin/core/product/`)
- Ajouter/Modifier/Supprimer des produits
- Gestion du stock
- Prix et réductions
- Images galerie
- Catégories
- Statut d'affichage (actif/inactif)
- Marquage comme "Produit en vedette"

#### 2. **Catégories** (`/admin/core/category/`)
- Créer des catégories
- Modifier les descriptions
- Voir le nombre de produits par catégorie
- Images par catégorie

#### 3. **Commandes** (`/admin/core/order/`)
- Voir toutes les commandes
- Filtrer par statut (En attente, Confirmée, Expédiée, etc.)
- Modifier le statut
- Consulter les adresses de livraison
- Ajouter des notes administrateur
- Voir les articles commandés

#### 4. **Avis Clients** (`/admin/core/review/`)
- Modérer les avis
- Marquer comme vérifiés
- Voir les notes (1-5 étoiles)
- Supprimer les avis inappropriés

#### 5. **Utilisateurs** (`/admin/auth/user/`)
- Gérer les comptes clients
- Modifier les informations
- Voir l'historique des commandes
- Activer/Désactiver les comptes

---

## 📝 Modèles de Données

### Category (Catégorie)
```python
- name: Nom de la catégorie
- slug: URL-friendly name
- description: Description
- image: Image de la catégorie
- is_active: Affichée sur le site?
- created_at: Date de création
```

### Product (Produit)
```python
- name: Nom du produit
- slug: URL-friendly name
- category: Catégorie associée
- product_type: cafe | pain | machine | accessoire
- description: Description courte
- detailed_description: Description détaillée
- price: Prix normal
- discount_price: Prix réduit (optionnel)
- image: Image principale
- gallery_images: Galerie (via ProductImage)
- stock: Nombre en stock
- rating: Note moyenne (1-5)
- reviews_count: Nombre d'avis
- is_featured: En vedette?
- is_active: Actif?
- created_at: Date de création
```

### Order (Commande)
```python
- order_number: Numéro unique
- user: Client
- status: pending | confirmed | shipped | delivered | cancelled | refunded
- total_amount: Montant total
- tax_amount: Montant des taxes
- shipping_cost: Frais de port
- shipping_address: Adresse de livraison
- billing_address: Adresse de facturation
- payment_method: card | transfer | paypal
- payment_status: pending | completed
- admin_notes: Notes internes
- created_at: Date de commande
```

### Review (Avis)
```python
- product: Produit évalué
- user: Auteur de l'avis
- rating: Note (1-5 étoiles)
- title: Titre de l'avis
- comment: Texte de l'avis
- is_verified: Achat vérifié?
- created_at: Date de l'avis
```

---

##  Prochaines Étapes

### 1. **Personnaliser les Produits**
- Aller à: `/admin/core/product/`
- Ajouter des images réelles
- Modifier les descriptions
- Ajuster les prix et stocks

### 2. **Configurer les Catégories**
- Ajouter des images de catégories
- Ajouter des sous-catégories si besoin

### 3. **Tester les Commandes**
- Aller à: `/`
- Parcourir les produits
- Créer une commande
- Voir apparaître dans le dashboard

### 4. **Gérer les Avis**
- Accéder à: `/admin/core/review/`
- Modérer les avis clients

---

## 💡 Tips Utiles

### Créer des Produits Rapidement
1. Aller à: `/admin/core/product/add/`
2. Remplir les informations de base
3. Ajouter une image (optionnel: les images de galerie)
4. Cliquer "Enregistrer et continuer"

### Gérer les Statuts de Commande
```
Cycle normal:
pending → confirmed → shipped → delivered

Autres états:
- cancelled: Annulée par le client
- refunded: Remboursée
```

### Voir les Statistiques
- Dashboard principal: vue d'ensemble
- Analytics: détail par produit/client
- Django Admin: vue complète des données

---

## 🔒 Sécurité

### Rappels Importants:
- ⚠️ Ne partagez JAMAIS vos identifiants admin
- ⚠️ Changez les mots de passe par défaut en production
- ⚠️ Utilisez HTTPS en production
- ⚠️ Faites des sauvegardes régulières

### Changer le Mot de Passe
1. Aller à: `/admin/auth/user/`
2. Cliquer sur votre compte
3. Cliquer "Changer le mot de passe"

---

## 📞 Support

### Commandes Utiles

```bash
# Voir tous les produits
python manage.py shell
>>> from core.models import Product
>>> Product.objects.all()

# Voir toutes les commandes
>>> from core.models import Order
>>> Order.objects.all()

# Créer un nouvel utilisateur admin
>>> from django.contrib.auth.models import User
>>> User.objects.create_superuser('newadmin', 'email@test.com', 'password')

# Exporter les données
python manage.py dumpdata > backup.json

# Importer les données
python manage.py loaddata backup.json
```

---

## ✨ Résumé

Votre système est maintenant **100% opérationnel** avec:
- ✅ Base de données remplie
- ✅ Dashboard admin fonctionnel
- ✅ Gestion complète des produits
- ✅ Suivi des commandes
- ✅ Modération des avis
- ✅ Analytics en temps réel

**Bon travail! 🎉 Votre plateforme Obidon est prête à fonctionner!**

---

*Dernière mise à jour: 21 janvier 2026*
