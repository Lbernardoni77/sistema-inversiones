#!/usr/bin/env python3
"""
Script para optimizar el rendimiento del backend
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_performance():
    print("🚀 OPTIMIZANDO RENDIMIENTO DEL BACKEND")
    print("=" * 50)
    
    # Test 1: Endpoint básico
    print("\n1️⃣ Probando endpoint básico...")
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        end_time = time.time()
        print(f"   ✅ Tiempo de respuesta: {end_time - start_time:.2f}s")
        print(f"   ✅ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Recomendación con timeout más largo
    print("\n2️⃣ Probando recomendación con timeout extendido...")
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/binance/recommendation/BTCUSDT?horizonte=24h", timeout=60)
        end_time = time.time()
        print(f"   ✅ Tiempo de respuesta: {end_time - start_time:.2f}s")
        print(f"   ✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Recomendación: {data.get('recomendacion', 'N/A')}")
    except requests.exceptions.Timeout:
        print("   ⚠️  Timeout después de 60 segundos")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Múltiples recomendaciones en paralelo
    print("\n3️⃣ Probando múltiples recomendaciones...")
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    start_time = time.time()
    
    import concurrent.futures
    
    def get_recommendation(symbol):
        try:
            response = requests.get(f"{BASE_URL}/binance/recommendation/{symbol}?horizonte=24h", timeout=30)
            return symbol, response.status_code, response.json() if response.status_code == 200 else None
        except Exception as e:
            return symbol, "ERROR", str(e)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(get_recommendation, symbols))
    
    end_time = time.time()
    print(f"   ✅ Tiempo total para {len(symbols)} símbolos: {end_time - start_time:.2f}s")
    
    for symbol, status, data in results:
        if status == 200:
            print(f"   ✅ {symbol}: {data.get('recomendacion', 'N/A')}")
        else:
            print(f"   ❌ {symbol}: {status}")
    
    # Test 4: Reportes
    print("\n4️⃣ Probando reportes...")
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/reporting/resumen", timeout=10)
        end_time = time.time()
        print(f"   ✅ Tiempo de respuesta: {end_time - start_time:.2f}s")
        print(f"   ✅ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def suggest_optimizations():
    print("\n" + "=" * 50)
    print("💡 SUGERENCIAS DE OPTIMIZACIÓN")
    print("=" * 50)
    print("1. 🔄 Cache de recomendaciones")
    print("   - Guardar recomendaciones por 5-10 minutos")
    print("   - Evitar recálculos innecesarios")
    print()
    print("2. ⚡ Optimizar llamadas externas")
    print("   - Usar timeouts más cortos para APIs externas")
    print("   - Implementar circuit breakers")
    print()
    print("3. 📊 Base de datos")
    print("   - Indexar tablas de recomendaciones")
    print("   - Optimizar consultas")
    print()
    print("4. 🌐 Frontend")
    print("   - Implementar retry automático")
    print("   - Mostrar loading states más informativos")
    print()
    print("5. 🔧 Backend")
    print("   - Usar workers asíncronos para cálculos pesados")
    print("   - Implementar rate limiting")

if __name__ == "__main__":
    test_performance()
    suggest_optimizations() 