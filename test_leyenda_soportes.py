#!/usr/bin/env python3
"""
Script para probar que los soportes y resistencias se devuelven correctamente
"""
import requests
import json

def test_soportes_resistencias():
    print("🧪 PROBANDO SOPORTES Y RESISTENCIAS")
    print("=" * 50)
    
    # URL del backend
    base_url = "http://localhost:8000"
    
    # Símbolos para probar
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    
    for symbol in symbols:
        print(f"\n📊 Probando {symbol}:")
        print("-" * 30)
        
        try:
            # Obtener recomendación
            url = f"{base_url}/binance/recommendation/{symbol}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extraer soportes y resistencias
                soportes = data.get('soportes', [])
                resistencias = data.get('resistencias', [])
                
                print(f"✅ {symbol} - Respuesta exitosa")
                print(f"   Soportes: {soportes}")
                print(f"   Resistencias: {resistencias}")
                print(f"   Total soportes: {len(soportes)}")
                print(f"   Total resistencias: {len(resistencias)}")
                
                # Verificar que hay datos
                if soportes or resistencias:
                    print(f"   ✅ {symbol} tiene datos de soportes/resistencias")
                else:
                    print(f"   ⚠️ {symbol} NO tiene datos de soportes/resistencias")
                    
            else:
                print(f"❌ {symbol} - Error HTTP {response.status_code}")
                print(f"   Respuesta: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {symbol} - Error de conexión: {e}")
        except Exception as e:
            print(f"❌ {symbol} - Error inesperado: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 INSTRUCCIONES PARA VERIFICAR LA LEYENDA")
    print("=" * 50)
    print("1. Asegúrate de que el backend esté corriendo:")
    print("   cd backend")
    print("   uvicorn main:app --reload")
    print()
    print("2. Asegúrate de que el frontend esté corriendo:")
    print("   cd frontend")
    print("   npm start")
    print()
    print("3. Ve a http://localhost:3000")
    print("4. Agrega un ticker (ej: BTCUSDT)")
    print("5. Haz clic en el ticker para ver el detalle")
    print("6. Verifica que debajo del gráfico aparezca la leyenda")
    print("7. La leyenda debe mostrar:")
    print("   - 🟢 Soportes (Niveles de Compra)")
    print("   - 🔴 Resistencias (Niveles de Venta)")
    print("   - Precios formateados con comas")
    print("   - Número de toques (si aplica)")
    print()
    print("💡 Si no ves la leyenda, verifica:")
    print("   - Que el backend devuelva soportes/resistencias")
    print("   - Que el frontend reciba los datos correctamente")
    print("   - Que no haya errores en la consola del navegador")

if __name__ == "__main__":
    test_soportes_resistencias() 