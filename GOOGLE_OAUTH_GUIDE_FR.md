# Guide de Configuration Google OAuth pour Obidon

##  Étapes accomplies

- ✓ Django-allauth installé et configuré
- ✓ Middleware d'authentification ajouté
- ✓ Base de données migrée
- ✓ Template de login mis à jour

##  Configurer Google OAuth

### Étape 1 : Créer une application Google Cloud

1. Accédez à [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet (nommez-le "Obidon")
3. Activez l'API Google+ :
   - Allez dans **APIs & Services** > **Library**
   - Recherchez "Google+ API"
   - Cliquez sur **Enable**

### Étape 2 : Créer les identifiants OAuth

1. Allez dans **APIs & Services** > **Credentials**
2. Cliquez sur **+ Create Credentials** > **OAuth 2.0 Client ID**
3. Vous serez peut-être invité à configurer l'écran de consentement OAuth d'abord
4. Pour l'écran de consentement :
   - Type d'utilisateur : External
   - Nom de l'application : Obidon
   - Support email : Votre email
   - Cliquez sur Create

5. De retour à Credentials, créez le Client ID :
   - Sélectionnez **Web application**
   - Donnez-lui un nom : "Obidon Development"

### Étape 3 : Configurer les URIs autorisés

Dans la section **Authorized JavaScript origins**, ajoutez :
```
http://localhost:8000
http://127.0.0.1:8000
```

Dans la section **Authorized redirect URIs**, ajoutez :
```
http://localhost:8000/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
```

### Étape 4 : Récupérer vos identifiants

Cliquez sur votre Client ID pour voir les détails :
- **Client ID** : Ressemble à `xxx.apps.googleusercontent.com`
- **Client Secret** : Une longue chaîne de caractères

**Gardez ces informations secrètes !**

### Étape 5 : Configurer dans Django

#### Option A : Via Django Admin (Recommandé)

1. **Démarrez le serveur Django** (s'il n'est pas déjà lancé) :
   ```bash
   python manage.py runserver
   ```

2. **Accédez à l'admin Django** :
   - URL : http://localhost:8000/admin
   - Si vous n'avez pas encore créé de superuser :
     ```bash
     python manage.py createsuperuser
     ```

3. **Configurez le Site Django** :
   - Allez dans **Sites**
   - Modifiez le site existant :
     - **Domain name** : `localhost:8000`
     - **Display name** : `Obidon`
   - Sauvegardez

4. **Ajoutez Google OAuth** :
   - Allez dans **Social applications**
   - Cliquez sur **Add Social Application**
   - Remplissez les champs :
     - **Provider** : Google
     - **Name** : Google OAuth (ou tout autre nom)
     - **Client id** : Votre Client ID
     - **Secret key** : Votre Client Secret
     - **Sites** : Sélectionnez "localhost:8000"
   - Sauvegardez

#### Option B : Via settings.py

Si vous préférez configurer directement dans le code, modifiez `config/settings.py` :

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': 'VOTRE_CLIENT_ID.apps.googleusercontent.com',
            'secret': 'VOTRE_CLIENT_SECRET',
            'key': ''
        }
    }
}
```

** WARNING** : Ne commitez pas les secrets dans Git ! Utilisez plutôt des variables d'environnement :

```python
import os

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        }
    }
}
```

### Étape 6 : Tester la connexion

1. Allez sur la page de connexion : `http://localhost:8000/login/`
2. Cliquez sur le bouton **"Google"**
3. Vous devriez être redirigé vers Google
4. Connectez-vous avec votre compte Google
5. Vous devriez être redirigé vers Obidon

## 🐛 Troubleshooting

### Erreur : "Redirect URI mismatch"
**Cause** : L'URI de redirection n'est pas exact

**Solution** :
- Vérifiez que l'URI exact est configuré dans Google Cloud
- Vérifiez la casse (majuscules/minuscules)
- Assurez-vous que le port est correct (8000)

### Erreur : "Client ID not found"
**Cause** : La Social Application n'est pas configurée dans Django

**Solution** :
- Allez dans Admin Django > Social Applications
- Vérifiez que Google OAuth est ajouté
- Vérifiez que le Site "localhost:8000" est sélectionné

### Les données d'email ne sont pas synchronisées
**Cause** : Configuration d'allauth

**Solution** :
- Vérifiez dans settings.py :
  ```python
  SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
  SOCIALACCOUNT_AUTO_SIGNUP = True
  ```

### "Page not found" lors du callback
**Cause** : URLs d'allauth non configurées

**Solution** :
- Vérifiez que dans `config/urls.py` vous avez :
  ```python
  path('accounts/', include('allauth.urls')),
  ```

## 🚀 Pour la Production

Avant de déployer, assurez-vous de :

1. **Utiliser HTTPS** : Les URLs doivent être en https
2. **Secrets sécurisés** : Utilisez des variables d'environnement
3. **Domaine correct** : Mettez à jour le domaine dans Django Sites
4. **DEBUG = False** : Mettez DEBUG à False dans settings.py
5. **ALLOWED_HOSTS** : Configurez les domaines autorisés

Exemple pour production :
```python
ALLOWED_HOSTS = ['obidon.com', 'www.obidon.com']

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        }
    }
}
```

## 📚 Ressources

- [Django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)

## ✨ Prochaines étapes

- [ ] Créer une page d'inscription (signup)
- [ ] Ajouter Facebook OAuth
- [ ] Personnaliser les pages de connexion allauth
- [ ] Ajouter 2FA (Two-Factor Authentication)
