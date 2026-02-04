# test_currency.py
# Script de test pour vérifier les conversions de devises

from decimal import Decimal
from currency_service import CurrencyConverter

def test_conversions():
    """Test des conversions de base"""
    print("=" * 60)
    print("TEST DU SYSTÈME DE CONVERSION DE DEVISES")
    print("=" * 60)
    
    # Test 1: Conversion EUR vers XOF
    print("\n Test 1: EUR vers XOF")
    print("-" * 40)
    amount_eur = 50
    result = CurrencyConverter.convert_price(amount_eur, 'EUR', 'XOF')
    print(f"Montant: {amount_eur} EUR")
    print(f"Résultat: {result['formatted']}")
    print(f"Montant brut: {result['amount']}")
    
    # Test 2: Conversion USD vers XOF
    print("\n Test 2: USD vers XOF")
    print("-" * 40)
    amount_usd = 100
    result = CurrencyConverter.convert_price(amount_usd, 'USD', 'XOF')
    print(f"Montant: {amount_usd} USD")
    print(f"Résultat: {result['formatted']}")
    print(f"Montant brut: {result['amount']}")
    
    # Test 3: Conversion XOF vers EUR
    print("\n Test 3: XOF vers EUR")
    print("-" * 40)
    amount_xof = 50000
    result = CurrencyConverter.convert_price(amount_xof, 'XOF', 'EUR')
    print(f"Montant: {amount_xof} FCFA")
    print(f"Résultat: {result['formatted']}")
    print(f"Montant brut: {result['amount']}")
    
    # Test 4: Toutes les conversions
    print("\n Test 4: Toutes les conversions depuis 100 EUR")
    print("-" * 40)
    conversions = CurrencyConverter.get_all_conversions(100, 'EUR')
    for currency, data in conversions.items():
        print(f"{currency}: {data['formatted']}")
    
    # Test 5: Récupération des taux
    print("\n Test 5: Récupération des taux de change")
    print("-" * 40)
    rates_data = CurrencyConverter.get_exchange_rates('XOF')
    print(f"Base: {rates_data['base']}")
    print(f"Timestamp: {rates_data.get('timestamp', 'N/A')}")
    print("Taux:")
    for currency, rate in rates_data['rates'].items():
        if currency in ['XOF', 'USD', 'EUR']:
            print(f"  {currency}: {rate}")
    
    # Test 6: Formats de prix
    print("\n Test 6: Formats de prix")
    print("-" * 40)
    prices = [10, 50, 100, 500, 1000, 5000]
    for price in prices:
        result_xof = CurrencyConverter.convert_price(price, 'EUR', 'XOF')
        result_usd = CurrencyConverter.convert_price(price, 'EUR', 'USD')
        print(f"{price} EUR = {result_xof['formatted']} | {result_usd['formatted']}")
    
    print("\n" + "=" * 60)
    print(" TESTS TERMINÉS")
    print("=" * 60)

def test_edge_cases():
    """Test des cas limites"""
    print("\n" + "=" * 60)
    print("TEST DES CAS LIMITES")
    print("=" * 60)
    
    # Test avec 0
    print("\n Test avec montant 0:")
    result = CurrencyConverter.convert_price(0, 'EUR', 'XOF')
    print(f"0 EUR = {result['formatted']}")
    
    # Test avec décimales
    print("\n Test avec décimales:")
    result = CurrencyConverter.convert_price(19.99, 'EUR', 'XOF')
    print(f"19.99 EUR = {result['formatted']}")
    
    # Test conversion identique
    print("\n Test conversion vers même devise:")
    result = CurrencyConverter.convert_price(50, 'EUR', 'EUR')
    print(f"50 EUR = {result['formatted']}")
    
    # Test avec grands montants
    print("\n Test avec grands montants:")
    result = CurrencyConverter.convert_price(1000000, 'XOF', 'EUR')
    print(f"1,000,000 FCFA = {result['formatted']}")
    
    print("\n" + "=" * 60)

def print_currency_info():
    """Affiche les informations sur les devises supportées"""
    print("\n" + "=" * 60)
    print("DEVISES SUPPORTÉES")
    print("=" * 60)
    
    for code, info in CurrencyConverter.SUPPORTED_CURRENCIES.items():
        print(f"\n{info['flag']} {info['name']} ({code})")
        print(f"   Symbole: {info['symbol']}")
        print(f"   Devise par défaut: {'Oui' if info['is_default'] else 'Non'}")

if __name__ == '__main__':
    try:
        print_currency_info()
        test_conversions()
        test_edge_cases()
        
        print("\n Tous les tests sont passés avec succès!")
        
    except Exception as e:
        print(f"\n Erreur lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()