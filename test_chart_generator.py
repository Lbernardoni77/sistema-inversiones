#!/usr/bin/env python3
"""
Script de prueba para el generador de gráficos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_chart_generator():
    """Prueba el generador de gráficos"""
    
    print("🎨 Probando generador de gráficos...")
    
    try:
        from services.chart_generator import ChartGenerator
        from services.binance_service import BinanceService
        
        # Crear instancias
        chart_generator = ChartGenerator()
        binance_service = BinanceService()
        
        # Símbolos de prueba
        test_symbols = ['BTCUSDT', 'ETHUSDT']
        
        for symbol in test_symbols:
            print(f"\n📊 Probando {symbol}:")
            
            # Obtener klines
            print("  🔍 Obteniendo klines...")
            klines = binance_service.get_multi_source_klines(symbol, "1h", 50)
            
            if klines and len(klines) > 0:
                print(f"    ✅ {len(klines)} klines obtenidos")
                
                # Generar gráfico
                print("  🎨 Generando gráfico...")
                result = chart_generator.generate_candlestick_chart(
                    klines=klines,
                    symbol=symbol,
                    interval="1h",
                    show_indicators=True,
                    show_support_resistance=True,
                    width=800,
                    height=400
                )
                
                if "error" not in result:
                    print(f"    ✅ Gráfico generado exitosamente")
                    print(f"    📊 Datos: {result.get('data_points')} puntos")
                    print(f"    📅 Rango: {result.get('time_range', {}).get('start', 'N/A')} - {result.get('time_range', {}).get('end', 'N/A')}")
                    
                    if result.get('statistics'):
                        stats = result['statistics']
                        print(f"    💰 Precio actual: ${stats.get('current_price', 0):.2f}")
                        print(f"    📈 Cambio: {stats.get('price_change_percent', 0):.2f}%")
                        print(f"    📊 Volumen total: {stats.get('volume_total', 0):.0f}")
                    
                    # Verificar que la imagen se generó
                    if result.get('image_base64'):
                        print(f"    🖼️ Imagen generada: {len(result['image_base64'])} caracteres base64")
                    else:
                        print(f"    ❌ No se generó imagen")
                        
                else:
                    print(f"    ❌ Error: {result['error']}")
            else:
                print(f"    ❌ No se pudieron obtener klines")
                
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
    
    print("\n✅ Prueba completada")

if __name__ == "__main__":
    test_chart_generator()
