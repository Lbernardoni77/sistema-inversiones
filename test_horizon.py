#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de horizonte
"""

import requests
import json

def test_horizon_functionality():
    """Prueba la funcionalidad de horizonte"""
    
    print("🧪 Probando funcionalidad de horizonte...")
    
    # 1. Probar recomendación con horizonte 1h
    print("\n1️⃣ Probando recomendación con horizonte 1h...")
    try:
        response = requests.get("http://localhost:8000/binance/recommendation/BTCUSDT?horizonte=1h")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Recomendación: {data.get('recomendacion')}")
            print(f"   ✅ Horizonte: {data.get('horizonte')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 2. Probar recomendación con horizonte 7d
    print("\n2️⃣ Probando recomendación con horizonte 7d...")
    try:
        response = requests.get("http://localhost:8000/binance/recommendation/BTCUSDT?horizonte=7d")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Recomendación: {data.get('recomendacion')}")
            print(f"   ✅ Horizonte: {data.get('horizonte')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 3. Probar endpoint de múltiples tickers
    print("\n3️⃣ Probando endpoint de múltiples tickers...")
    try:
        response = requests.get("http://localhost:8000/tickers/recommendations?horizonte=24h")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Horizonte: {data.get('horizonte')}")
            print(f"   ✅ Resultados: {len(data.get('resultados', []))} tickers")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    test_horizon_functionality() 