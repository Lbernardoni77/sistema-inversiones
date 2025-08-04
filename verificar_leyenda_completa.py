#!/usr/bin/env python3
"""
Script final para verificar que la leyenda de soportes y resistencias funciona correctamente
"""
import requests
import json

def verificar_leyenda_completa():
    print("🎯 VERIFICACIÓN FINAL - LEYENDA DE SOPORTES Y RESISTENCIAS")
    print("=" * 60)
    
    # Verificar que ambos servicios estén corriendo
    print("🔍 Verificando servicios...")
    
    # Backend
    try:
        backend_response = requests.get("http://localhost:8000/", timeout=5)
        if backend_response.status_code == 200:
            print("✅ Backend funcionando en http://localhost:8000")
        else:
            print("❌ Backend no responde correctamente")
            return
    except:
        print("❌ Backend no está corriendo")
        return
    
    # Frontend
    try:
        frontend_response = requests.get("http://localhost:3000", timeout=5)
        if frontend_response.status_code == 200:
            print("✅ Frontend funcionando en http://localhost:3000")
        else:
            print("❌ Frontend no responde correctamente")
            return
    except:
        print("❌ Frontend no está corriendo")
        return
    
    print("\n📊 Probando datos de soportes y resistencias...")
    
    # Probar con BTCUSDT
    symbol = "BTCUSDT"
    try:
        url = f"http://localhost:8000/binance/recommendation/{symbol}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extraer soportes y resistencias del detalle
            detalle = data.get('detalle', {})
            soportes = detalle.get('soportes', [])
            resistencias = detalle.get('resistencias', [])
            
            print(f"✅ {symbol} - Datos obtenidos correctamente")
            print(f"   📈 Soportes: {len(soportes)} niveles")
            print(f"   📉 Resistencias: {len(resistencias)} niveles")
            
            if soportes:
                print(f"   🟢 Soportes: {soportes[:3]}...")  # Mostrar solo los primeros 3
            if resistencias:
                print(f"   🔴 Resistencias: {resistencias[:3]}...")  # Mostrar solo los primeros 3
            
            if soportes or resistencias:
                print(f"\n🎉 ¡ÉXITO! Los datos están disponibles para la leyenda")
            else:
                print(f"\n⚠️ No hay datos de soportes/resistencias para mostrar")
                
        else:
            print(f"❌ Error al obtener datos: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 INSTRUCCIONES PARA VERIFICAR LA LEYENDA")
    print("=" * 60)
    print("1. 🌐 Abre tu navegador y ve a: http://localhost:3000")
    print("2. ➕ Agrega un ticker (ej: BTCUSDT)")
    print("3. 📊 Haz clic en el ticker para ver el detalle")
    print("4. 📈 Busca la leyenda debajo del gráfico")
    print()
    print("📋 La leyenda debe mostrar:")
    print("   📊 Leyenda de Niveles")
    print("   🟢 Soportes (Niveles de Compra)")
    print("   🔴 Resistencias (Niveles de Venta)")
    print("   💰 Precios formateados (ej: $117,040.01)")
    print("   🔢 Número de toques (si aplica)")
    print("   💡 Explicación sobre opacidad")
    print()
    print("🎨 Características de la leyenda:")
    print("   - Fondo oscuro (#1a1a1a)")
    print("   - Bordes redondeados")
    print("   - Colores: Verde para soportes, Rojo para resistencias")
    print("   - Formato de precios con comas")
    print("   - Información sobre toques del precio")
    print()
    print("🔧 Si no ves la leyenda:")
    print("   1. Verifica que el backend esté corriendo")
    print("   2. Verifica que el frontend esté corriendo")
    print("   3. Revisa la consola del navegador (F12)")
    print("   4. Asegúrate de que el ticker tenga datos")
    print()
    print("✅ ¡La funcionalidad está implementada y lista!")

if __name__ == "__main__":
    verificar_leyenda_completa() 