from django.core.management.base import BaseCommand
from core.models import Currency
from core.currency_service import CurrencyConverter

class Command(BaseCommand):
    help = 'Initialize currencies in the database'

    def handle(self, *args, **options):
        self.stdout.write('Initializing currencies...')
        
        for code, info in CurrencyConverter.SUPPORTED_CURRENCIES.items():
            currency, created = Currency.objects.get_or_create(
                code=code,
                defaults={
                    'name': info['name'],
                    'symbol': info['symbol'],
                    'flag': info['flag'],
                    'is_default': info['is_default']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created currency: {code} - {info["name"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Currency already exists: {code}')
                )
        
        self.stdout.write(self.style.SUCCESS('Currency initialization complete!'))