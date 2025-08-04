#!/usr/bin/env python3
"""
Script de diagnóstico para el endpoint de detalle de tickers
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_ticker_detail():
    print("🔍 DIAGNÓSTICO DEL ENDPOINT DE DETALLE DE TICKERS")
    print("=" * 50)
    
    # Lista de tickers para probar
    tickers = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT"]
    
    for ticker in tickers:
        print(f"\n📊 Probando: {ticker}")
        print("-" * 30)
        
        try:
            # Probar endpoint de detalle
            url = f"{BASE_URL}/reporting/detalle/{ticker}"
            print(f"URL: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Respuesta exitosa")
                print(f"   - Símbolo: {data.get('simbolo', 'N/A')}")
                print(f"   - Total recomendaciones: {data.get('metricas_generales', {}).get('total_recomendaciones', 'N/A')}")
                print(f"   - Precisión: {data.get('metricas_generales', {}).get('precision', 'N/A')}")
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                print(f"   Respuesta: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("❌ Timeout - El servidor tardó demasiado en responder")
        except requests.exceptions.ConnectionError:
            print("❌ Error de conexión - No se puede conectar al servidor")
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            print(f"   Tipo de error: {type(e).__name__}")

def test_recommendation_endpoint():
    print("\n\n🎯 PROBANDO ENDPOINT DE RECOMENDACIÓN")
    print("=" * 40)
    
    try:
        # Probar endpoint de recomendación
        url = f"{BASE_URL}/binance/recommendation/BTCUSDT"
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Recomendación exitosa")
            print(f"   - Recomendación: {data.get('recomendacion', 'N/A')}")
            print(f"   - Horizonte: {data.get('horizonte', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_server_status():
    print("\n\n🏥 ESTADO DEL SERVIDOR")
    print("=" * 25)
    
    try:
        # Probar endpoint básico
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"✅ Servidor respondiendo - Status: {response.status_code}")
        
        # Probar endpoint de health check si existe
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            print(f"✅ Health check - Status: {response.status_code}")
        except:
            print("ℹ️  No hay endpoint de health check")
            
    except Exception as e:
        print(f"❌ Servidor no responde: {str(e)}")

if __name__ == "__main__":
    test_server_status()
    test_recommendation_endpoint()
    test_ticker_detail()
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 50)
    print("Si ves errores arriba, estos son los problemas más comunes:")
    print("1. ❌ Servidor no está corriendo")
    print("2. ❌ Error en la base de datos")
    print("3. ❌ Error en el código del endpoint")
    print("4. ❌ Problema de permisos o archivos")
    print("\n💡 Copia y pega los errores específicos para más ayuda.") 