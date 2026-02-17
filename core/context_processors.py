# context_processors.py
from core.currency_service import CurrencyConverter

def currency_context(request):
    """Injecte le contexte de devise dans tous les templates"""
    try:
        # Récupérer la devise par défaut (FCFA)
        default_currency = CurrencyConverter.SUPPORTED_CURRENCIES['XOF']
        
        # Fonction utilitaire pour formater les prix
        def format_fcfa(amount):
            """Formate un montant en FCFA avec séparateur de milliers"""
            try:
                if not amount:
                    return "0 FCFA"
                
                # Convertir en Decimal si nécessaire
                from decimal import Decimal
                if isinstance(amount, (int, float, str)):
                    amount = Decimal(str(amount))
                
                # Formater avec séparateur de milliers
                formatted = f"{amount:,.0f}".replace(',', ' ')
                return f"{formatted} FCFA"
            except:
                return f"{amount} FCFA"
        
        return {
            'CURRENCY': default_currency,
            'CURRENCY_CODE': 'XOF',
            'CURRENCY_SYMBOL': 'FCFA',
            'CURRENCY_FLAG': '🇹🇬',
            'CURRENCY_NAME': 'Franc CFA',
            'SUPPORTED_CURRENCIES': CurrencyConverter.SUPPORTED_CURRENCIES,
            'format_fcfa': format_fcfa,
            'is_fcfa_currency': True,  # Flag pour vérifier si on utilise FCFA
        }
    except Exception as e:
        # Fallback en cas d'erreur
        return {
            'CURRENCY_CODE': 'XOF',
            'CURRENCY_SYMBOL': 'FCFA',
            'CURRENCY_NAME': 'Franc CFA',
            'format_fcfa': lambda amount: f"{amount} FCFA" if amount else "0 FCFA",
            'is_fcfa_currency': True,
        }
        
        