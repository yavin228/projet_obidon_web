# core/management/commands/init_currencies.py
from django.core.management.base import BaseCommand
from core.models import Currency

class Command(BaseCommand):
    help = 'Initialise les devises par défaut'

    def handle(self, *args, **kwargs):
        currencies = [
            {'code': 'XOF', 'name': 'Franc CFA', 'symbol': 'FCFA', 'flag': '🇹🇬', 'is_default': True},
            {'code': 'USD', 'name': 'Dollar américain', 'symbol': '$', 'flag': '🇺🇸', 'is_default': False},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'flag': '🇪🇺', 'is_default': False},
        ]
        
        for currency_data in currencies:
            currency, created = Currency.objects.get_or_create(
                code=currency_data['code'],
                defaults=currency_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Devise créée: {currency.code}'))
            else:
                self.stdout.write(self.style.WARNING(f'Devise existante: {currency.code}'))