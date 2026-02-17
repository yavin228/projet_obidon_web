# management/commands/convert_prices_to_fcfa.py
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from core.models import Product, Currency
from core.currency_service import CurrencyConverter

class Command(BaseCommand):
    help = 'Convertit tous les prix existants en FCFA'
    
    def handle(self, *args, **kwargs):
        # Assurer que la devise FCFA existe dans la base
        xof_currency, created = Currency.objects.get_or_create(
            code='XOF',
            defaults={
                'name': 'Franc CFA',
                'symbol': 'FCFA',
                'flag': '🇹🇬',
                'is_default': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(' Devise XOF (FCFA) créée dans la base de données'))
        
        # Convertir tous les produits
        total_products = Product.objects.count()
        self.stdout.write(f"\n Conversion de {total_products} produits en FCFA...")
        
        converted_count = 0
        with transaction.atomic():
            for product in Product.objects.all():
                try:
                    # Convertir le prix normal (supposant que c'est en EUR)
                    if product.price:
                        product.price_fcfa = CurrencyConverter.convert(
                            float(product.price),
                            from_currency='EUR',
                            to_currency='XOF'
                        )
                    
                    # Convertir le prix réduit (supposant que c'est en EUR)
                    if product.discount_price:
                        product.discount_price_fcfa = CurrencyConverter.convert(
                            float(product.discount_price),
                            from_currency='EUR',
                            to_currency='XOF'
                        )
                    
                    # Sauvegarder uniquement les champs modifiés
                    update_fields = []
                    if hasattr(product, 'price_fcfa') and product.price_fcfa:
                        update_fields.append('price_fcfa')
                    if hasattr(product, 'discount_price_fcfa'):
                        update_fields.append('discount_price_fcfa')
                    
                    if update_fields:
                        product.save(update_fields=update_fields)
                        converted_count += 1
                        
                        # Afficher la progression
                        if converted_count % 10 == 0:
                            self.stdout.write(f"   Converti {converted_count}/{total_products} produits...")
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f" Erreur lors de la conversion du produit {product.id}: {e}")
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Conversion terminée ! {converted_count}/{total_products} produits convertis en FCFA.'
            )
        )
        
        # Afficher un exemple de prix converti
        if converted_count > 0:
            sample_product = Product.objects.filter(price_fcfa__gt=0).first()
            if sample_product:
                self.stdout.write(f"\n Exemple de conversion:")
                self.stdout.write(f"   Produit: {sample_product.name}")
                self.stdout.write(f"   Prix original: {sample_product.price} EUR")
                self.stdout.write(f"   Prix en FCFA: {sample_product.price_fcfa:,.0f} FCFA".replace(',', ' '))