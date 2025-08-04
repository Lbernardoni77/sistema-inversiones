#!/usr/bin/env python3
"""
Script para probar todos los endpoints de reporting y mostrar reportes del aprendizaje
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_all_reports():
    print("📊 PROBANDO TODOS LOS REPORTES DEL SISTEMA DE APRENDIZAJE")
    print("=" * 60)
    
    # 1. Resumen Ejecutivo
    print("\n1️⃣ RESUMEN EJECUTIVO")
    print("-" * 30)
    try:
        response = requests.get(f"{BASE_URL}/reporting/resumen")
        if response.status_code == 200:
            data = response.json()
            resumen = data.get('resumen_ejecutivo', {})
            print(f"✅ Precisión Global: {resumen.get('precision_global', 'N/A')}")
            print(f"✅ Recomendaciones Exitosas: {resumen.get('recomendaciones_exitosas', 'N/A')}")
            print(f"✅ Recomendaciones Fallidas: {resumen.get('recomendaciones_fallidas', 'N/A')}")
            print(f"✅ Recomendaciones Pendientes: {resumen.get('recomendaciones_pendientes', 'N/A')}")
            
            optimizaciones = data.get('optimizaciones_recientes', [])
            print(f"✅ Optimizaciones Recientes: {len(optimizaciones)}")
            for opt in optimizaciones[:2]:  # Mostrar solo las 2 más recientes
                print(f"   - {opt.get('fecha', 'N/A')}: {opt.get('tipo', 'N/A')} - {opt.get('descripcion', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 2. Detalle por Símbolo
    print("\n2️⃣ DETALLE POR SÍMBOLO (BTCUSDT)")
    print("-" * 40)
    try:
        response = requests.get(f"{BASE_URL}/reporting/detalle/BTCUSDT")
        if response.status_code == 200:
            data = response.json()
            metricas = data.get('metricas_generales', {})
            print(f"✅ Total Recomendaciones: {metricas.get('total_recomendaciones', 'N/A')}")
            print(f"✅ Precisión: {metricas.get('precision', 'N/A')}")
            print(f"✅ Exitosas: {metricas.get('exitosas', 'N/A')}")
            print(f"✅ Fallidas: {metricas.get('fallidas', 'N/A')}")
            
            analisis = data.get('analisis_por_tipo', {})
            compras = analisis.get('compras', {})
            ventas = analisis.get('ventas', {})
            print(f"✅ Compras - Total: {compras.get('total', 'N/A')}, Precisión: {compras.get('precision', 'N/A')}")
            print(f"✅ Ventas - Total: {ventas.get('total', 'N/A')}, Precisión: {ventas.get('precision', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 3. Evolución de Pesos
    print("\n3️⃣ EVOLUCIÓN DE PESOS")
    print("-" * 25)
    try:
        response = requests.get(f"{BASE_URL}/reporting/evolucion")
        if response.status_code == 200:
            data = response.json()
            evolucion = data.get('evolucion_pesos', [])
            print(f"✅ Cambios de Pesos Registrados: {len(evolucion)}")
            
            for cambio in evolucion[:3]:  # Mostrar solo los 3 más recientes
                fecha = cambio.get('fecha', 'N/A')
                motivo = cambio.get('motivo_ajuste', 'Sin motivo')
                print(f"   - {fecha}: {motivo}")
                
                # Mostrar algunos pesos si están disponibles
                pesos_nuevos = cambio.get('pesos_nuevos', {})
                if pesos_nuevos:
                    print(f"     Pesos: RSI={pesos_nuevos.get('rsi', 'N/A')}, MACD={pesos_nuevos.get('macd', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 4. Exportación de Datos
    print("\n4️⃣ EXPORTACIÓN DE DATOS")
    print("-" * 25)
    try:
        response = requests.get(f"{BASE_URL}/reporting/exportar/json")
        if response.status_code == 200:
            data = response.json()
            archivo = data.get('archivo_generado', 'N/A')
            print(f"✅ Archivo JSON generado: {archivo}")
            
            metadata = data.get('metadata', {})
            print(f"✅ Total recomendaciones: {metadata.get('total_recomendaciones', 'N/A')}")
            print(f"✅ Total optimizaciones: {metadata.get('total_optimizaciones', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 CÓMO ACCEDER A LOS REPORTES:")
    print("=" * 60)
    print("1. Resumen Ejecutivo: http://localhost:8000/reporting/resumen")
    print("2. Detalle BTCUSDT: http://localhost:8000/reporting/detalle/BTCUSDT")
    print("3. Evolución Pesos: http://localhost:8000/reporting/evolucion")
    print("4. Exportar JSON: http://localhost:8000/reporting/exportar/json")
    print("5. Exportar CSV: http://localhost:8000/reporting/exportar/csv")
    print("\n💡 También puedes usar estos endpoints desde el frontend o cualquier cliente HTTP")

if __name__ == "__main__":
    test_all_reports() 