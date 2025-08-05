#!/usr/bin/env python3
"""
Script para probar las API keys de Binance configuradas en Render
"""

import requests
import os

def test_binance_with_api_keys():
    """Probar Binance con API keys"""
    print("🔍 Probando Binance con API keys...")
    
    # API keys que deberían estar en Render
    api_key = "tu_api_key_aqui"  # Reemplazar con tu API key real
    secret_key = "tu_secret_key_aqui"  # Reemplazar con tu secret key real
    
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    headers = {
        'X-MBX-APIKEY': api_key,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito con API keys: ${data['price']}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error con API keys: {e}")
        return False

def test_without_api_keys():
    """Probar sin API keys para comparar"""
    print("\n🔍 Probando sin API keys...")
    
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito sin API keys: ${data['price']}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sin API keys: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Probando API keys de Binance")
    print("=" * 50)
    
    # Probar sin API keys primero
    without_keys = test_without_api_keys()
    
    # Probar con API keys
    with_keys = test_binance_with_api_keys()
    
    print("\n" + "=" * 50)
    print("📋 RESULTADOS")
    print("=" * 50)
    
    if without_keys:
        print("✅ Sin API keys: Funciona")
    else:
        print("❌ Sin API keys: No funciona")
    
    if with_keys:
        print("✅ Con API keys: Funciona")
    else:
        print("❌ Con API keys: No funciona")
    
    print("\n💡 INSTRUCCIONES:")
    print("1. Reemplaza 'tu_api_key_aqui' con tu API key real de Binance")
    print("2. Reemplaza 'tu_secret_key_aqui' con tu secret key real")
    print("3. Ejecuta el script nuevamente")
    print("4. Si funciona con API keys, configúralas en Render")

if __name__ == "__main__":
    main() 