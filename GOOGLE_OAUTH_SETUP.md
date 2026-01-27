# Configuration de Google OAuth pour Obidon

## Étapes pour configurer Google OAuth

### 1. Créer une application Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet : "Obidon"
3. Activez l'API Google+ (ou Google Identity)

### 2. Créer les identifiants OAuth

1. Allez dans **Credentials** (Identifiants)
2. Cliquez sur **Create Credentials** > **OAuth 2.0 Client ID**
3. Sélectionnez **Web application**
4. Configurez les **Authorized JavaScript origins** :
   - `http://localhost:8000`
   - `http://127.0.0.1:8000`

5. Configurez les **Authorized redirect URIs** :
   - `http://localhost:8000/accounts/google/login/callback/`
   - `http://127.0.0.1:8000/accounts/google/login/callback/`

### 3. Récupérer vos identifiants

- Copiez votre **Client ID**
- Copiez votre **Client Secret**

### 4. Configurer Django

#### Option 1 : Via Django Admin (Recommandé)

1. Accédez à l'admin Django : `http://localhost:8000/admin`
2. Allez dans **Sites** et modifiez le domaine :
   - Domain name: `localhost:8000`
   - Display name: `Obidon`

3. Allez dans **Social applications** et cliquez sur "Add Social Application"
4. Remplissez les champs :
   - **Provider**: Google
   - **Name**: Google OAuth
   - **Client id**: Votre Client ID
   - **Secret key**: Votre Client Secret
   - **Sites**: Sélectionnez localhost:8000

5. Sauvegardez

#### Option 2 : Via settings.py

Si vous préférez configurer via settings.py, modifiez le dictionnaire SOCIALACCOUNT_PROVIDERS :

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
            'client_id': 'VOTRE_CLIENT_ID_ICI',
            'secret': 'VOTRE_CLIENT_SECRET_ICI',
            'key': ''
        }
    }
}
```

### 5. Créer les tables de base de données

Exécutez les migrations :
```bash
python manage.py migrate
```

### 6. Tester la connexion

1. Redémarrez votre serveur Django
2. Allez sur la page de connexion : `http://localhost:8000/login/`
3. Cliquez sur le bouton "Google"

## Troubleshooting

### Erreur "Redirect URI mismatch"
- Vérifiez que l'URI exact est configuré dans Google Cloud Console
- Assurez-vous que le domaine dans Django Sites correspond

### Erreur "Client ID not found"
- Vérifiez que vous avez sauvegardé la Social Application dans l'admin
- Vérifiez le SITE_ID dans settings.py (doit être 1)

### Les données d'email ne sont pas reçues
- Assurez-vous que `SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'`
- Vérifiez que 'email' est dans les SCOPE

## Notes

- Pour la production, mettez à jour le domaine dans Django Sites
- Utilisez des variables d'environnement pour les secrets
- Activez HTTPS pour la production


# Niveau de python
# Créer un superuser
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver

# Tester l'authentification :
# - http://localhost:8000/login/ (se connecter)
# - http://localhost:8000/account/ (voir la page de compte)

# Nouveau Dashboard Admin
Dashboard Principal: http://localhost:8000/admin-dashboard/
Analytics: http://localhost:8000/admin-dashboard/analytics/
