# templatetags/currency_tags.py
# Custom template tags pour la conversion de devises

from django import template
from django.utils.safestring import mark_safe
from ..currency_service import CurrencyConverter, get_user_currency

register = template.Library()

@register.simple_tag(takes_context=True)
def convert_price(context, amount, from_currency='EUR'):
    """
    Convertit un prix dans la devise de l'utilisateur
    Usage: {% convert_price 50 'EUR' %}
    """
    request = context.get('request')
    user = request.user if request else None
    
    to_currency = get_user_currency(user)
    
    try:
        result = CurrencyConverter.convert_price(amount, from_currency, to_currency)
        return result['formatted']
    except Exception as e:
        return f"{amount} {from_currency}"

@register.simple_tag(takes_context=True)
def price_tag(context, amount, from_currency='EUR'):
    """
    Génère un span HTML avec conversion automatique côté client
    Usage: {% price_tag 50 'EUR' %}
    """
    request = context.get('request')
    user = request.user if request else None
    
    to_currency = get_user_currency(user)
    
    try:
        result = CurrencyConverter.convert_price(amount, from_currency, to_currency)
        html = f'<span class="currency-price" data-base-amount="{amount}" data-base-currency="{from_currency}">{result["formatted"]}</span>'
        return mark_safe(html)
    except Exception as e:
        return f"{amount} {from_currency}"

@register.filter
def currency_symbol(currency_code):
    """
    Retourne le symbole d'une devise
    Usage: {{ 'EUR'|currency_symbol }}
    """
    currencies = CurrencyConverter.SUPPORTED_CURRENCIES
    return currencies.get(currency_code, {}).get('symbol', currency_code)

@register.filter
def format_currency(amount, currency_code='XOF'):
    """
    Formate un montant avec le symbole de devise
    Usage: {{ 50000|format_currency:'XOF' }}
    """
    currencies = CurrencyConverter.SUPPORTED_CURRENCIES
    symbol = currencies.get(currency_code, {}).get('symbol', currency_code)
    formatted_amount = f"{amount:,.2f}"
    return f"{symbol} {formatted_amount}"