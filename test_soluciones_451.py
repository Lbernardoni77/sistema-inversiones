#!/usr/bin/env python3
"""
Script para probar diferentes soluciones al error 451 de Binance
"""

import os
import requests
import httpx
import time
from typing import Dict, Any

# URLs de prueba
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
TEST_SYMBOL = "BTCUSDT"

def test_direct_binance():
    """Probar acceso directo a Binance"""
    print("🔍 Probando acceso directo a Binance...")
    try:
        response = requests.get(f"{BINANCE_API_URL}?symbol={TEST_SYMBOL}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito directo: ${data['price']}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error directo: {e}")
        return False

def test_with_user_agent():
    """Probar con User-Agent de navegador"""
    print("\n🔍 Probando con User-Agent de navegador...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(f"{BINANCE_API_URL}?symbol={TEST_SYMBOL}", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito con User-Agent: ${data['price']}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error con User-Agent: {e}")
        return False

def test_with_api_keys():
    """Probar con API keys de Binance"""
    print("\n🔍 Probando con API keys de Binance...")
    api_key = os.getenv('BINANCE_API_KEY')
    if not api_key:
        print("⚠️  No hay API key configurada")
        return False
    
    headers = {
        'X-MBX-APIKEY': api_key,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(f"{BINANCE_API_URL}?symbol={TEST_SYMBOL}", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito con API key: ${data['price']}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error con API key: {e}")
        return False

def test_with_proxy(proxy_url: str):
    """Probar con proxy específico"""
    print(f"\n🔍 Probando con proxy: {proxy_url}")
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    try:
        response = requests.get(f"{BINANCE_API_URL}?symbol={TEST_SYMBOL}", proxies=proxies, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito con proxy: ${data['price']}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error con proxy: {e}")
        return False

def test_alternative_apis():
    """Probar APIs alternativas"""
    print("\n🔍 Probando APIs alternativas...")
    
    # CoinGecko
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10)
        if response.status_code == 200:
            data = response.json()
            price = data['bitcoin']['usd']
            print(f"✅ CoinGecko: ${price}")
        else:
            print(f"❌ CoinGecko error: {response.status_code}")
    except Exception as e:
        print(f"❌ CoinGecko error: {e}")
    
    # CoinMarketCap (requiere API key)
    cmc_key = os.getenv('CMC_API_KEY')
    if cmc_key:
        try:
            headers = {'X-CMC_PRO_API_KEY': cmc_key}
            response = requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=BTC", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                price = data['data']['BTC']['quote']['USD']['price']
                print(f"✅ CoinMarketCap: ${price}")
            else:
                print(f"❌ CoinMarketCap error: {response.status_code}")
        except Exception as e:
            print(f"❌ CoinMarketCap error: {e}")

def test_public_proxies():
    """Probar proxies públicos gratuitos"""
    print("\n🔍 Probando proxies públicos...")
    
    # Lista de proxies públicos gratuitos (pueden no funcionar)
    public_proxies = [
        "http://185.199.229.156:7492",
        "http://185.199.228.220:7492",
        "http://185.199.231.45:7492",
        "http://188.74.210.207:6286",
        "http://188.74.183.10:8279"
    ]
    
    for proxy in public_proxies:
        print(f"Probando proxy: {proxy}")
        if test_with_proxy(proxy):
            print(f"🎉 ¡Proxy funcionando: {proxy}")
            return proxy
        time.sleep(1)  # Pausa entre intentos
    
    print("❌ Ningún proxy público funcionó")
    return None

def main():
    """Función principal"""
    print("🚀 Probando soluciones para el error 451 de Binance")
    print("=" * 60)
    
    # Probar diferentes métodos
    results = {
        'directo': test_direct_binance(),
        'user_agent': test_with_user_agent(),
        'api_keys': test_with_api_keys()
    }
    
    # Probar APIs alternativas
    test_alternative_apis()
    
    # Probar proxies públicos (opcional)
    print("\n" + "=" * 60)
    print("¿Quieres probar proxies públicos? (puede tomar tiempo)")
    response = input("S/N: ").lower().strip()
    if response == 's':
        working_proxy = test_public_proxies()
        if working_proxy:
            results['proxy'] = True
            print(f"\n💡 Proxy funcionando: {working_proxy}")
            print("💡 Puedes configurar esta variable de entorno:")
            print(f"export PROXY_URL='{working_proxy}'")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    for method, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {method.upper()}")
    
    working_methods = [method for method, success in results.items() if success]
    
    if working_methods:
        print(f"\n🎉 Métodos funcionando: {', '.join(working_methods)}")
        print("\n💡 RECOMENDACIONES:")
        if 'api_keys' in working_methods:
            print("- Usar API keys de Binance es la mejor opción")
        elif 'user_agent' in working_methods:
            print("- Configurar User-Agent puede ayudar")
        elif 'proxy' in working_methods:
            print("- Configurar proxy puede sortear restricciones geográficas")
    else:
        print("\n❌ Ningún método directo funcionó")
        print("💡 Usar CoinGecko como fallback es la mejor opción")

if __name__ == "__main__":
    main() 