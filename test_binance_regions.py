#!/usr/bin/env python3
"""
Script para probar acceso a Binance desde diferentes regiones
"""

import requests
import time

def test_binance_access():
    """Prueba el acceso a Binance API"""
    
    print("🧪 Probando acceso a Binance API...")
    
    # URL de prueba de Binance
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    
    try:
        print("📡 Intentando conexión a Binance...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conexión exitosa!")
            print(f"📊 BTCUSDT: ${data['price']}")
            return True
        elif response.status_code == 451:
            print("❌ Error 451: Restricción geográfica")
            print("🌍 Esta región tiene restricciones de Binance")
            return False
        else:
            print(f"⚠️ Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_klines_access():
    """Prueba el acceso a klines de Binance"""
    
    print("\n📈 Probando acceso a klines...")
    
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=5"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            klines = response.json()
            print(f"✅ Klines obtenidos: {len(klines)} velas")
            print(f"📊 Último precio: ${klines[-1][4]}")
            return True
        elif response.status_code == 451:
            print("❌ Error 451: Restricción geográfica para klines")
            return False
        else:
            print(f"⚠️ Error {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🌍 Test de Acceso a Binance por Región")
    print("=" * 50)
    
    # Test precio
    price_ok = test_binance_access()
    
    # Test klines
    klines_ok = test_klines_access()
    
    print("\n📋 Resumen:")
    print(f"   Precios: {'✅ OK' if price_ok else '❌ Bloqueado'}")
    print(f"   Klines: {'✅ OK' if klines_ok else '❌ Bloqueado'}")
    
    if price_ok and klines_ok:
        print("\n🎉 ¡Esta región puede usar Binance completamente!")
    elif price_ok:
        print("\n⚠️ Esta región puede usar precios pero no klines")
    else:
        print("\n🚫 Esta región tiene restricciones de Binance")
        print("💡 Recomendación: Migrar a Railway (región Singapore)")
