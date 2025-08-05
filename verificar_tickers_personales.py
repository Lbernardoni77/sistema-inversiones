#!/usr/bin/env python3
"""
Script para verificar que los tickers personales estén funcionando correctamente
"""

import requests
import json
import time

# URLs de los servicios
BACKEND_URL = "https://sistema-inversiones.onrender.com"
FRONTEND_URL = "https://sistema-inversiones-frontend.onrender.com"

# Tickers que el usuario ha estado probando
TICKERS_PERSONALES = [
    "BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", 
    "SANDUSDT", "THETAUSDT", "MANAUSDT", "SHIBUSDT"
]

def verificar_backend():
    """Verificar que el backend esté funcionando"""
    print("🔍 Verificando backend...")
    try:
        response = requests.get(f"{BACKEND_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ Backend funcionando correctamente")
            return True
        else:
            print(f"❌ Backend respondió con código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return False

def verificar_frontend():
    """Verificar que el frontend esté funcionando"""
    print("🔍 Verificando frontend...")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend funcionando correctamente")
            return True
        else:
            print(f"❌ Frontend respondió con código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al frontend: {e}")
        return False

def probar_ticker(symbol):
    """Probar un ticker específico"""
    print(f"\n🔍 Probando {symbol}...")
    
    # Probar endpoint de precio
    try:
        response = requests.get(f"{BACKEND_URL}/binance/price/{symbol}?period=1d", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Precio obtenido: ${data.get('price', 'N/A')} ({data.get('source', 'N/A')})")
            
            # Verificar formato del precio
            price = data.get('price')
            if isinstance(price, (int, float)):
                print(f"✅ Precio es numérico: {price}")
            elif isinstance(price, str):
                print(f"⚠️  Precio es string: {price}")
                # Intentar convertir
                try:
                    precio_numerico = float(price.replace(',', '.'))
                    print(f"✅ Conversión exitosa: {precio_numerico}")
                except:
                    print(f"❌ No se pudo convertir el precio")
            else:
                print(f"❌ Tipo de precio inesperado: {type(price)}")
            
            return True
        else:
            print(f"❌ Error obteniendo precio: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en precio: {e}")
        return False

def probar_recomendacion(symbol):
    """Probar endpoint de recomendación"""
    try:
        response = requests.get(f"{BACKEND_URL}/binance/recommendation/{symbol}?horizonte=24h", timeout=15)
        if response.status_code == 200:
            data = response.json()
            recomendacion = data.get('recomendacion', 'N/A')
            print(f"✅ Recomendación: {recomendacion}")
            
            # Verificar soportes y resistencias
            detalle = data.get('detalle', {})
            soportes = detalle.get('soportes', [])
            resistencias = detalle.get('resistencias', [])
            print(f"✅ Soportes: {len(soportes)}, Resistencias: {len(resistencias)}")
            
            return True
        else:
            print(f"❌ Error obteniendo recomendación: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en recomendación: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando Sistema de Inversiones")
    print("=" * 50)
    
    # Verificar servicios
    backend_ok = verificar_backend()
    frontend_ok = verificar_frontend()
    
    if not backend_ok or not frontend_ok:
        print("\n❌ Los servicios no están funcionando correctamente")
        return
    
    print("\n📊 Probando tickers personales...")
    print("=" * 50)
    
    resultados = {}
    
    for ticker in TICKERS_PERSONALES:
        print(f"\n🎯 {ticker}")
        print("-" * 30)
        
        precio_ok = probar_ticker(ticker)
        recomendacion_ok = probar_recomendacion(ticker)
        
        resultados[ticker] = {
            'precio': precio_ok,
            'recomendacion': recomendacion_ok,
            'total': precio_ok and recomendacion_ok
        }
        
        # Pausa entre requests para evitar rate limiting
        time.sleep(1)
    
    # Resumen
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE RESULTADOS")
    print("=" * 50)
    
    exitosos = 0
    total = len(TICKERS_PERSONALES)
    
    for ticker, resultado in resultados.items():
        status = "✅" if resultado['total'] else "❌"
        print(f"{status} {ticker}: Precio={resultado['precio']}, Recomendación={resultado['recomendacion']}")
        if resultado['total']:
            exitosos += 1
    
    print(f"\n📊 Resultado final: {exitosos}/{total} tickers funcionando correctamente")
    
    if exitosos == total:
        print("🎉 ¡Todos los tickers están funcionando perfectamente!")
        print("💡 El frontend debería poder agregar tickers sin problemas")
    else:
        print("⚠️  Algunos tickers tienen problemas")
        print("💡 Revisa los logs para más detalles")

if __name__ == "__main__":
    main() 