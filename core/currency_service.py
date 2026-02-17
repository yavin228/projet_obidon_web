"""
Service centralisé pour la gestion des devises et conversions
COMPATIBLE avec votre code existant
"""
from decimal import Decimal
from django.utils import timezone
from .models import Currency, ExchangeRate, UserCurrencyPreference

class CurrencyConverter:
    """Service de conversion compatible avec votre code existant"""
    
    # Devises supportées
    SUPPORTED_CURRENCIES = {
        'XOF': {'name': 'Franc CFA', 'symbol': 'FCFA', 'flag': '🇨🇫', 'rate_to_xof': 1},
        'EUR': {'name': 'Euro', 'symbol': '€', 'flag': '🇪🇺', 'rate_to_xof': 655.957},
        'USD': {'name': 'Dollar', 'symbol': '$', 'flag': '🇺🇸', 'rate_to_xof': 599.85},
    }
    
    @staticmethod
    def convert(amount, from_currency, to_currency):
        """
        Convertit un montant d'une devise à une autre
        :param amount: Montant à convertir
        :param from_currency: Code devise source
        :param to_currency: Code devise cible
        :return: Montant converti (Decimal)
        """
        if from_currency == to_currency:
            return Decimal(str(amount))
        
        try:
            # Tenter de récupérer le taux direct
            rate = ExchangeRate.objects.get(
                base_currency__code=from_currency,
                target_currency__code=to_currency,
                is_active=True
            )
            return Decimal(str(amount)) * rate.rate
        except ExchangeRate.DoesNotExist:
            # Tenter de récupérer le taux inverse
            try:
                inverse_rate = ExchangeRate.objects.get(
                    base_currency__code=to_currency,
                    target_currency__code=from_currency,
                    is_active=True
                )
                return Decimal(str(amount)) / inverse_rate.rate
            except ExchangeRate.DoesNotExist:
                # Fallback sur les taux par défaut
                return _fallback_convert(amount, from_currency, to_currency)
    
    @staticmethod
    def convert_price(amount, from_currency, to_currency):
        """
        Convertit un prix et retourne un dictionnaire formaté
        COMPATIBLE avec votre views.py
        """
        converted_amount = CurrencyConverter.convert(amount, from_currency, to_currency)
        
        # Obtenir le symbole et le code
        currency_info = CurrencyConverter.SUPPORTED_CURRENCIES.get(to_currency, {})
        symbol = currency_info.get('symbol', to_currency)
        code = to_currency
        
        # Formater le montant
        if to_currency == 'XOF':
            formatted = f"{converted_amount:,.0f} {symbol}".replace(',', ' ')
        else:
            formatted = f"{converted_amount:.2f} {symbol}"
        
        return {
            'amount': converted_amount,
            'formatted': formatted,
            'symbol': symbol,
            'code': code
        }
    
    @staticmethod
    def get_exchange_rates(base_currency='XOF'):
        """
        Retourne tous les taux de change depuis une devise de base
        COMPATIBLE avec votre views.py
        """
        rates = {}
        
        for currency_code in CurrencyConverter.SUPPORTED_CURRENCIES.keys():
            if currency_code == base_currency:
                rates[currency_code] = 1.0
            else:
                try:
                    rate_obj = ExchangeRate.objects.get(
                        base_currency__code=base_currency,
                        target_currency__code=currency_code,
                        is_active=True
                    )
                    rates[currency_code] = float(rate_obj.rate)
                except ExchangeRate.DoesNotExist:
                    # Fallback sur les taux par défaut
                    if base_currency == 'XOF' and currency_code == 'EUR':
                        rates[currency_code] = 0.001525
                    elif base_currency == 'XOF' and currency_code == 'USD':
                        rates[currency_code] = 0.001667
                    elif base_currency == 'EUR' and currency_code == 'XOF':
                        rates[currency_code] = 655.957
                    elif base_currency == 'USD' and currency_code == 'XOF':
                        rates[currency_code] = 599.85
                    else:
                        rates[currency_code] = 1.0
        
        return rates
    
    @staticmethod
    def format_price(amount, currency_code='XOF'):
        """Formate un prix avec le symbole approprié"""
        currency_info = CurrencyConverter.SUPPORTED_CURRENCIES.get(currency_code, {})
        symbol = currency_info.get('symbol', currency_code)
        
        amount = Decimal(str(amount))
        if currency_code == 'XOF':
            return f"{amount:,.0f} {symbol}".replace(',', ' ')
        else:
            return f"{amount:.2f} {symbol}"


def _fallback_convert(amount, from_currency, to_currency):
    """Conversion de secours avec taux fixes"""
    amount = Decimal(str(amount))
    
    # Convertir d'abord en FCFA (XOF)
    if from_currency == 'EUR':
        amount_in_xof = amount * Decimal('655.957')
    elif from_currency == 'USD':
        amount_in_xof = amount * Decimal('599.85')
    elif from_currency == 'XOF':
        amount_in_xof = amount
    else:
        return amount
    
    # Convertir de FCFA vers la devise cible
    if to_currency == 'EUR':
        return amount_in_xof / Decimal('655.957')
    elif to_currency == 'USD':
        return amount_in_xof / Decimal('599.85')
    elif to_currency == 'XOF':
        return amount_in_xof
    
    return amount


def get_user_currency(request):
    """
    Retourne le code de devise préféré de l'utilisateur
    COMPATIBLE avec votre views.py
    """
    # Pour les utilisateurs anonymes : utiliser la session
    if not request.user.is_authenticated:
        return request.session.get('preferred_currency', 'XOF')
    
    # Pour les utilisateurs connectés : utiliser leur préférence
    try:
        preference = UserCurrencyPreference.objects.get(user=request.user)
        if preference.preferred_currency:
            return preference.preferred_currency.code
    except UserCurrencyPreference.DoesNotExist:
        pass
    
    # Fallback sur FCFA
    return 'XOF'


def format_price(amount, currency_code='XOF'):
    """
    Fonction standalone pour formater un prix
    COMPATIBLE avec currency_tags.py
    """
    return CurrencyConverter.format_price(amount, currency_code)