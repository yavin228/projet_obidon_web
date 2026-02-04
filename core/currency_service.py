# currency_service.py - Service pour gérer les conversions de devises

import requests
from decimal import Decimal
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta

class CurrencyConverter:
    """Service de conversion de devises avec API ExchangeRate"""
    
    # API gratuite: https://www.exchangerate-api.com/
    API_URL = "https://api.exchangerate-api.com/v4/latest/"
    CACHE_TIMEOUT = 3600  # 1 heure
    
    # Configuration des devises supportées
    SUPPORTED_CURRENCIES = {
        'XOF': {
            'name': 'Franc CFA',
            'symbol': 'FCFA',
            'flag': '🇹🇬',
            'is_default': True
        },
        'USD': {
            'name': 'Dollar américain',
            'symbol': '$',
            'flag': '🇺🇸',
            'is_default': False
        },
        'EUR': {
            'name': 'Euro',
            'symbol': '€',
            'flag': '🇪🇺',
            'is_default': False
        }
    }
    
    @classmethod
    def get_exchange_rates(cls, base_currency='XOF'):
        """
        Récupère les taux de change depuis l'API
        Utilise le cache pour éviter trop de requêtes
        """
        cache_key = f'exchange_rates_{base_currency}'
        rates = cache.get(cache_key)
        
        if rates is None:
            try:
                # Appel à l'API
                response = requests.get(
                    f"{cls.API_URL}{base_currency}",
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                rates = {
                    'base': base_currency,
                    'rates': data.get('rates', {}),
                    'timestamp': data.get('time_last_updated', datetime.now().isoformat())
                }
                
                # Mise en cache
                cache.set(cache_key, rates, cls.CACHE_TIMEOUT)
                
            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la récupération des taux: {e}")
                # Retourner des taux par défaut en cas d'erreur
                rates = cls._get_fallback_rates(base_currency)
        
        return rates
    
    @classmethod
    def _get_fallback_rates(cls, base_currency='XOF'):
        """Taux de secours en cas d'échec de l'API"""
        # Taux approximatifs (à mettre à jour régulièrement)
        fallback_rates = {
            'XOF': {
                'XOF': 1.0,
                'USD': 0.0016,  # 1 FCFA ≈ 0.0016 USD
                'EUR': 0.0015,  # 1 FCFA ≈ 0.0015 EUR
            },
            'USD': {
                'XOF': 620.0,   # 1 USD ≈ 620 FCFA
                'USD': 1.0,
                'EUR': 0.92,    # 1 USD ≈ 0.92 EUR
            },
            'EUR': {
                'XOF': 655.96,  # 1 EUR ≈ 656 FCFA (taux fixe CFA)
                'USD': 1.09,    # 1 EUR ≈ 1.09 USD
                'EUR': 1.0,
            }
        }
        
        return {
            'base': base_currency,
            'rates': fallback_rates.get(base_currency, {}),
            'timestamp': datetime.now().isoformat(),
            'fallback': True
        }
    
    @classmethod
    def convert(cls, amount, from_currency='XOF', to_currency='USD'):
        """
        Convertit un montant d'une devise à une autre
        
        Args:
            amount: Montant à convertir
            from_currency: Devise source (XOF, USD, EUR)
            to_currency: Devise cible (XOF, USD, EUR)
        
        Returns:
            Decimal: Montant converti
        """
        if from_currency == to_currency:
            return Decimal(str(amount))
        
        # Récupérer les taux de change
        rates_data = cls.get_exchange_rates(from_currency)
        rates = rates_data.get('rates', {})
        
        if to_currency not in rates:
            raise ValueError(f"Devise {to_currency} non supportée")
        
        rate = Decimal(str(rates[to_currency]))
        converted_amount = Decimal(str(amount)) * rate
        
        return converted_amount.quantize(Decimal('0.01'))
    
    @classmethod
    def convert_price(cls, price, from_currency='XOF', to_currency='USD'):
        """
        Convertit un prix et le formate
        
        Returns:
            dict: {amount: Decimal, formatted: str, symbol: str}
        """
        converted = cls.convert(price, from_currency, to_currency)
        currency_info = cls.SUPPORTED_CURRENCIES.get(to_currency, {})
        
        return {
            'amount': converted,
            'formatted': f"{currency_info.get('symbol', '')} {converted:,.2f}",
            'symbol': currency_info.get('symbol', ''),
            'code': to_currency
        }
    
    @classmethod
    def get_all_conversions(cls, amount, base_currency='XOF'):
        """
        Retourne le montant converti dans toutes les devises supportées
        
        Returns:
            dict: {'XOF': {...}, 'USD': {...}, 'EUR': {...}}
        """
        conversions = {}
        
        for currency_code in cls.SUPPORTED_CURRENCIES.keys():
            conversions[currency_code] = cls.convert_price(
                amount, 
                base_currency, 
                currency_code
            )
        
        return conversions


# Fonctions utilitaires pour les templates
def format_price(amount, currency_code='XOF'):
    """Formate un prix avec le symbole de la devise"""
    currency_info = CurrencyConverter.SUPPORTED_CURRENCIES.get(currency_code, {})
    symbol = currency_info.get('symbol', currency_code)
    return f"{symbol} {amount:,.2f}"


def get_user_currency(user):
    """Récupère la devise préférée de l'utilisateur"""
    if user.is_authenticated:
        try:
            preference = user.currency_preference
            return preference.preferred_currency.code if preference.preferred_currency else 'XOF'
        except:
            pass
    return 'XOF'  # Devise par défaut