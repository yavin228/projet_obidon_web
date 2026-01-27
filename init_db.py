#!/usr/bin/env python
"""
Script pour initialiser la base de données et configurer Obidon
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sites.models import Site
from django.core.management import call_command

def init_database():
    """Initialise la base de données"""
    print("Exécution des migrations...")
    call_command('migrate')
    
    print("Configuration du site...")
    try:
        site = Site.objects.get(pk=1)
        site.domain = 'localhost:8000'
        site.name = 'Obidon'
        site.save()
        print(f"✓ Site configuré: {site.domain}")
    except Site.DoesNotExist:
        site = Site.objects.create(
            pk=1,
            domain='localhost:8000',
            name='Obidon'
        )
        print(f"✓ Site créé: {site.domain}")
    
    print("\n✓ Base de données initialisée avec succès!")
    print("\nProchaines étapes:")
    print("1. Accédez à http://localhost:8000/admin")
    print("2. Allez dans 'Social applications'")
    print("3. Ajoutez votre configuration Google OAuth")
    print("\nPour plus d'infos, consultez GOOGLE_OAUTH_SETUP.md")

if __name__ == '__main__':
    init_database()
