#!/usr/bin/env python3
"""
Script de test pour vérifier l'API Alpha Vantage
"""

from alpha_vantage_client import AlphaVantageClient
import json

def test_alpha_vantage():
    """Tester l'API Alpha Vantage"""
    client = AlphaVantageClient("DHQESFCKN9JIMDD6")
    
    print("Test de l'API Alpha Vantage...")
    
    # Test 1: Company Overview
    print("\n=== Test Company Overview ===")
    try:
        overview = client.get_company_overview("AAPL")
        print("Réponse brute:")
        print(json.dumps(overview, indent=2)[:500] + "...")
        
        parsed = client.parse_company_overview(overview)
        print("\nDonnées parsées:")
        print(json.dumps(parsed, indent=2))
        
    except Exception as e:
        print(f"Erreur Company Overview: {e}")
    
    # Test 2: Daily Data
    print("\n=== Test Daily Data ===")
    try:
        daily = client.get_daily_adjusted("AAPL", outputsize="compact")
        print("Clés de la réponse:", list(daily.keys()))
        
        if 'Time Series (Daily)' in daily:
            dates = list(daily['Time Series (Daily)'].keys())[:3]
            print(f"Premières dates: {dates}")
        elif 'Note' in daily:
            print(f"Note API: {daily['Note']}")
        elif 'Error Message' in daily:
            print(f"Erreur API: {daily['Error Message']}")
        else:
            print("Structure inattendue:")
            print(json.dumps(daily, indent=2)[:500] + "...")
        
    except Exception as e:
        print(f"Erreur Daily Data: {e}")

if __name__ == "__main__":
    test_alpha_vantage()

