#!/usr/bin/env python3
"""
Script de prueba para verificar las nuevas fuentes de klines
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.multi_source_service import MultiSourceService

def test_new_klines_sources():
    """Prueba las nuevas fuentes de klines"""
    
    print("🧪 Probando nuevas fuentes de klines...")
    
    # Símbolos de prueba
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    
    # Crear instancia del servicio
    multi_source = MultiSourceService()
    
    for symbol in test_symbols:
        print(f"\n📊 Probando {symbol}:")
        
        # Probar Alpha Vantage
        print("  🔍 Alpha Vantage...")
        try:
            klines = multi_source.get_alpha_vantage_klines(symbol, "1h", 10)
            if klines and len(klines) > 0:
                print(f"    ✅ Alpha Vantage: {len(klines)} klines obtenidos")
                print(f"    📈 Último precio: {klines[-1][4]}")
            else:
                print("    ❌ Alpha Vantage: No se obtuvieron datos")
        except Exception as e:
            print(f"    ❌ Alpha Vantage: Error - {e}")
        
        # Probar Polygon
        print("  🔍 Polygon...")
        try:
            klines = multi_source.get_polygon_klines(symbol, "1h", 10)
            if klines and len(klines) > 0:
                print(f"    ✅ Polygon: {len(klines)} klines obtenidos")
                print(f"    📈 Último precio: {klines[-1][4]}")
            else:
                print("    ❌ Polygon: No se obtuvieron datos")
        except Exception as e:
            print(f"    ❌ Polygon: Error - {e}")
        
        # Probar Finnhub
        print("  🔍 Finnhub...")
        try:
            klines = multi_source.get_finnhub_klines(symbol, "1h", 10)
            if klines and len(klines) > 0:
                print(f"    ✅ Finnhub: {len(klines)} klines obtenidos")
                print(f"    📈 Último precio: {klines[-1][4]}")
            else:
                print("    ❌ Finnhub: No se obtuvieron datos")
        except Exception as e:
            print(f"    ❌ Finnhub: Error - {e}")
    
    # Cerrar conexiones
    multi_source.close()
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    test_new_klines_sources()
