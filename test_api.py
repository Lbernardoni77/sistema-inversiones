#!/usr/bin/env python3
"""
Script para probar las APIs del dashboard directamente
"""

import requests
import json

def test_dashboard_apis():
    """Prueba las APIs del dashboard"""
    base_url = "http://localhost:8080"
    
    print("🔍 Probando APIs del dashboard...")
    
    # Probar API de estado
    print("\n📊 Probando /api/status...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Datos recibidos:")
            print(f"      - Configuración: {len(data.get('config', {}).get('source_order', []))} fuentes")
            print(f"      - Benchmark: {len(data.get('last_benchmark', {}).get('performance_ranking', []))} fuentes")
            print(f"      - Timestamp: {data.get('current_time', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error conectando: {e}")
    
    # Probar API de benchmark
    print("\n📊 Probando /api/benchmark...")
    try:
        response = requests.get(f"{base_url}/api/benchmark", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Datos recibidos:")
            print(f"      - Historial: {len(data.get('history', []))} archivos")
            print(f"      - Total archivos: {data.get('total_files', 0)}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error conectando: {e}")
    
    # Probar página principal
    print("\n📊 Probando página principal...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            print(f"   ✅ Página cargada correctamente")
            print(f"   📄 Tamaño: {len(response.text)} caracteres")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error conectando: {e}")

if __name__ == "__main__":
    test_dashboard_apis()
    print("\n✅ Pruebas completadas") 