#!/usr/bin/env python3
"""
Script para probar el sistema de cache
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_cache_performance():
    print("🚀 PROBANDO SISTEMA DE CACHE")
    print("=" * 50)
    
    # Test 1: Primera llamada (cache miss)
    print("\n1️⃣ Primera llamada (Cache Miss)")
    print("-" * 40)
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/binance/recommendation/BTCUSDT?horizonte=24h", timeout=60)
        end_time = time.time()
        print(f"   ⏱️  Tiempo: {end_time - start_time:.2f}s")
        print(f"   📊 Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   🎯 Recomendación: {data.get('recomendacion', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Segunda llamada (cache hit)
    print("\n2️⃣ Segunda llamada (Cache Hit)")
    print("-" * 40)
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/binance/recommendation/BTCUSDT?horizonte=24h", timeout=10)
        end_time = time.time()
        print(f"   ⏱️  Tiempo: {end_time - start_time:.2f}s")
        print(f"   📊 Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   🎯 Recomendación: {data.get('recomendacion', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Estadísticas del cache
    print("\n3️⃣ Estadísticas del Cache")
    print("-" * 40)
    try:
        response = requests.get(f"{BASE_URL}/cache/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"   📦 Total entradas: {stats.get('total_entries', 'N/A')}")
            print(f"   ✅ Entradas activas: {stats.get('active_entries', 'N/A')}")
            print(f"   ⏰ Duración cache: {stats.get('cache_duration_minutes', 'N/A')} minutos")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Múltiples símbolos
    print("\n4️⃣ Múltiples Símbolos")
    print("-" * 40)
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    start_time = time.time()
    
    for symbol in symbols:
        symbol_start = time.time()
        try:
            response = requests.get(f"{BASE_URL}/binance/recommendation/{symbol}?horizonte=24h", timeout=30)
            symbol_end = time.time()
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {symbol}: {data.get('recomendacion', 'N/A')} ({symbol_end - symbol_start:.2f}s)")
            else:
                print(f"   ❌ {symbol}: Error {response.status_code}")
        except Exception as e:
            print(f"   ❌ {symbol}: {e}")
    
    end_time = time.time()
    print(f"   ⏱️  Tiempo total: {end_time - start_time:.2f}s")
    
    # Test 5: Limpiar cache
    print("\n5️⃣ Limpiar Cache")
    print("-" * 40)
    try:
        response = requests.post(f"{BASE_URL}/cache/clear", timeout=5)
        if response.status_code == 200:
            print("   ✅ Cache limpiado exitosamente")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def show_cache_benefits():
    print("\n" + "=" * 50)
    print("💡 BENEFICIOS DEL CACHE")
    print("=" * 50)
    print("✅ Respuestas más rápidas (de 20s a <1s)")
    print("✅ Menos carga en APIs externas")
    print("✅ Mejor experiencia de usuario")
    print("✅ Reducción de timeouts")
    print("✅ Menos errores en el frontend")
    print()
    print("🔄 El cache se actualiza automáticamente cada 10 minutos")
    print("📦 Los datos se guardan en archivo para persistencia")
    print("🧹 Se limpia automáticamente cuando expira")

if __name__ == "__main__":
    test_cache_performance()
    show_cache_benefits() 