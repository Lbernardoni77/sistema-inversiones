#!/usr/bin/env python3
"""
Script para probar la conexión a Binance desde Railway
"""

import httpx
import time
from datetime import datetime

def test_binance_connection():
    """Prueba la conexión a Binance y sus endpoints principales"""
    
    print("🔍 Probando conexión a Binance desde Railway...")
    
    # Headers comunes
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    # Lista de endpoints a probar
    endpoints = [
        {
            'name': 'Precio',
            'url': 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
        },
        {
            'name': 'Klines',
            'url': 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=10'
        },
        {
            'name': 'Profundidad',
            'url': 'https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=5'
        }
    ]
    
    results = []
    
    # Probar cada endpoint
    for endpoint in endpoints:
        print(f"\n🔄 Probando endpoint {endpoint['name']}...")
        
        try:
            start_time = time.time()
            with httpx.Client(timeout=10, headers=headers) as client:
                response = client.get(endpoint['url'])
                response.raise_for_status()
                data = response.json()
                end_time = time.time()
                
                result = {
                    'endpoint': endpoint['name'],
                    'status': 'success',
                    'response_time': end_time - start_time,
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }
                print(f"✅ {endpoint['name']}: OK ({result['response_time']:.2f}s)")
                
        except Exception as e:
            result = {
                'endpoint': endpoint['name'],
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ {endpoint['name']}: Error - {str(e)}")
        
        results.append(result)
        time.sleep(1)  # Esperar entre requests
    
    # Análisis final
    success_count = sum(1 for r in results if r['status'] == 'success')
    total_count = len(results)
    success_rate = (success_count / total_count) * 100
    
    print(f"\n📊 Resumen:")
    print(f"Total endpoints probados: {total_count}")
    print(f"Endpoints exitosos: {success_count}")
    print(f"Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n✅ Binance está completamente accesible desde Railway!")
    elif success_rate > 0:
        print("\n⚠️ Binance está parcialmente accesible desde Railway.")
    else:
        print("\n❌ Binance no está accesible desde Railway.")
    
    return results

if __name__ == "__main__":
    test_binance_connection()
