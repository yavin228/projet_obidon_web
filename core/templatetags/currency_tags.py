from django import template
from core.currency_service import CurrencyConverter, format_price, get_user_currency

register = template.Library()

@register.filter
def fcfa(value):
    """
    Filtre pour formater un montant en FCFA
    Usage: {{ price|fcfa }}
    """
    if value is None:
        return "0 FCFA"
    try:
        # Formater avec des espaces comme séparateur de milliers
        return f"{value:,.0f} FCFA".replace(',', ' ')
    except (ValueError, TypeError):
        return "0 FCFA"

@register.filter
def format_price(value, currency_code='XOF'):
    """Formatte un prix avec la devise spécifiée"""
    return CurrencyConverter.format_price(value, currency_code)

@register.filter
def convert_price(value, args):
    """
    Convertit un prix d'une devise à une autre
    Usage: {{ price|convert_price:"XOF,EUR" }}
    """
    from_currency, to_currency = args.split(',')
    result = CurrencyConverter.convert_price(value, from_currency, to_currency)
    return result['formatted']

@register.simple_tag(takes_context=True)
def get_user_currency_tag(context):
    """Retourne la devise préférée de l'utilisateur"""
    request = context['request']
    return get_user_currency(request)

@register.simple_tag
def get_currencies():
    """Retourne toutes les devises supportées"""
    return CurrencyConverter.SUPPORTED_CURRENCIES

@register.filter
def in_currency(value, currency_code='XOF'):
    """
    Convertit et formate un prix dans la devise spécifiée
    Usage: {{ price|in_currency:"EUR" }}
    """
    if value is None:
        return ""
    result = CurrencyConverter.convert_price(value, 'XOF', currency_code)
    return result['formatted']