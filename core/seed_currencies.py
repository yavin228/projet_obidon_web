"""
Script pour initialiser les devises et taux de change dans la base de données
À exécuter après les migrations
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Currency, ExchangeRate

def create_currencies():
    """Crée les devises de base"""
    print(" Création des devises...")
    
    # Créer ou mettre à jour les devises
    fcfa, created = Currency.objects.update_or_create(
        code='XOF',
        defaults={
            'name': 'Franc CFA',
            'symbol': 'FCFA',
            'flag': '🇨🇫',
            'is_default': True,
            'is_active': True
        }
    )
    print(f"✓ {fcfa}" + (" (créé)" if created else " (mis à jour)"))
    
    eur, created = Currency.objects.update_or_create(
        code='EUR',
        defaults={
            'name': 'Euro',
            'symbol': '€',
            'flag': '🇪🇺',
            'is_default': False,
            'is_active': True
        }
    )
    print(f"✓ {eur}" + (" (créé)" if created else " (mis à jour)"))
    
    usd, created = Currency.objects.update_or_create(
        code='USD',
        defaults={
            'name': 'Dollar américain',
            'symbol': '$',
            'flag': '🇺🇸',
            'is_default': False,
            'is_active': True
        }
    )
    print(f"✓ {usd}" + (" (créé)" if created else " (mis à jour)"))
    
    return fcfa, eur, usd

def create_exchange_rates(fcfa, eur, usd):
    """Crée les taux de change entre les devises"""
    print("\n Création des taux de change...")
    
    # FCFA → EUR: 1 FCFA = 0.001525 EUR
    rate1, created = ExchangeRate.objects.update_or_create(
        base_currency=fcfa,
        target_currency=eur,
        defaults={'rate': 0.001525, 'is_active': True}
    )
    print(f"✓ {rate1}" + (" (créé)" if created else " (mis à jour)"))
    
    # FCFA → USD: 1 FCFA = 0.001667 USD
    rate2, created = ExchangeRate.objects.update_or_create(
        base_currency=fcfa,
        target_currency=usd,
        defaults={'rate': 0.001667, 'is_active': True}
    )
    print(f"✓ {rate2}" + (" (créé)" if created else " (mis à jour)"))
    
    # EUR → FCFA: 1 EUR = 655.957 FCFA
    rate3, created = ExchangeRate.objects.update_or_create(
        base_currency=eur,
        target_currency=fcfa,
        defaults={'rate': 655.957, 'is_active': True}
    )
    print(f"✓ {rate3}" + (" (créé)" if created else " (mis à jour)"))
    
    # USD → FCFA: 1 USD = 599.85 FCFA
    rate4, created = ExchangeRate.objects.update_or_create(
        base_currency=usd,
        target_currency=fcfa,
        defaults={'rate': 599.85, 'is_active': True}
    )
    print(f"✓ {rate4}" + (" (créé)" if created else " (mis à jour)"))
    
    # EUR → USD
    rate5, created = ExchangeRate.objects.update_or_create(
        base_currency=eur,
        target_currency=usd,
        defaults={'rate': 1.08, 'is_active': True}
    )
    print(f"✓ {rate5}" + (" (créé)" if created else " (mis à jour)"))
    
    # USD → EUR
    rate6, created = ExchangeRate.objects.update_or_create(
        base_currency=usd,
        target_currency=eur,
        defaults={'rate': 0.9259, 'is_active': True}
    )
    print(f"✓ {rate6}" + (" (créé)" if created else " (mis à jour)"))

def main():
    """Fonction principale"""
    print("=" * 60)
    print(" Initialisation des devises et taux de change")
    print("=" * 60)
    
    try:
        fcfa, eur, usd = create_currencies()
        create_exchange_rates(fcfa, eur, usd)
        
        print("\n" + "=" * 60)
        print(" Initialisation terminée avec succès !")
        print("=" * 60)
        
        # Afficher un résumé
        print("\n Résumé :")
        print(f"  • Devises actives : {Currency.objects.filter(is_active=True).count()}")
        print(f"  • Taux de change actifs : {ExchangeRate.objects.filter(is_active=True).count()}")
        print(f"\n   Taux FCFA → EUR : 1 FCFA = {ExchangeRate.objects.get(base_currency__code='XOF', target_currency__code='EUR').rate} EUR")
        print(f"   Taux FCFA → USD : 1 FCFA = {ExchangeRate.objects.get(base_currency__code='XOF', target_currency__code='USD').rate} USD")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'initialisation : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()