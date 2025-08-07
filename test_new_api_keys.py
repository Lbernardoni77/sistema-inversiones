#!/usr/bin/env python3
"""
Script para probar las nuevas API keys
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_new_api_keys():
    """Prueba las nuevas API keys"""
    
    print("🔑 Probando nuevas API keys...")
    
    # Configurar las nuevas API keys
    os.environ['ALPHA_VANTAGE_API_KEY'] = 'OQKLL0SS21H10SCW'
    os.environ['POLYGON_API_KEY'] = '3LpLDGUpYcWTrwuGFBZ0ntoFN72Lmkmx'
    os.environ['FINNHUB_API_KEY'] = 'd2agh3hr01qgk9ueof30d2agh3hr01qgk9ueof3g'
    
    from services.multi_source_service import MultiSourceService
    
    # Crear instancia del servicio
    multi_source = MultiSourceService()
    
    # Símbolos de prueba
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    
    print("\n📊 Probando precios:")
    for symbol in test_symbols:
        print(f"\n🔍 {symbol}:")
        try:
            price_data = multi_source.get_price(symbol)
            if price_data and 'price' in price_data:
                print(f"  ✅ Precio: ${price_data['price']}")
                print(f"  📊 Fuente: {price_data.get('source', 'N/A')}")
            else:
                print(f"  ❌ No se pudo obtener precio")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n📈 Probando klines:")
    for symbol in test_symbols:
        print(f"\n🔍 {symbol}:")
        try:
            klines = multi_source.get_klines(symbol, "1h", 10)
            if klines and len(klines) > 0:
                print(f"  ✅ Klines: {len(klines)} datos obtenidos")
                print(f"  📈 Último precio: {klines[-1][4]}")
                print(f"  📊 Fuente: {klines[-1][-1] if len(klines[-1]) > 5 else 'N/A'}")
            else:
                print(f"  ❌ No se pudieron obtener klines")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Cerrar conexiones
    multi_source.close()
    
    print("\n✅ Pruebas completadas")
    print("\n💡 Para configurar en Render:")
    print("   - Ve a tu proyecto en Render")
    print("   - En la pestaña 'Environment'")
    print("   - Agrega las variables:")
    print("     ALPHA_VANTAGE_API_KEY=OQKLL0SS21H10SCW")
    print("     POLYGON_API_KEY=3LpLDGUpYcWTrwuGFBZ0ntoFN72Lmkmx")
    print("     FINNHUB_API_KEY=d2agh3hr01qgk9ueof30d2agh3hr01qgk9ueof3g")

if __name__ == "__main__":
    test_new_api_keys()
