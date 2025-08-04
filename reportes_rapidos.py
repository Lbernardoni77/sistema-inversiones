#!/usr/bin/env python3
"""
Script rápido para acceder a los reportes más importantes del sistema de aprendizaje
"""
import requests
import json
import webbrowser
from datetime import datetime

BASE_URL = "http://localhost:8000"

def mostrar_menu():
    print("\n" + "="*50)
    print("📊 REPORTES DEL SISTEMA DE APRENDIZAJE")
    print("="*50)
    print("1. 📈 Resumen Ejecutivo")
    print("2. 🔍 Detalle BTCUSDT")
    print("3. 📊 Evolución de Pesos")
    print("4. 📤 Exportar Datos (JSON)")
    print("5. 🌐 Abrir en Navegador")
    print("6. 📋 Todos los Reportes")
    print("0. ❌ Salir")
    print("="*50)

def resumen_ejecutivo():
    print("\n📈 RESUMEN EJECUTIVO")
    print("-" * 30)
    try:
        response = requests.get(f"{BASE_URL}/reporting/resumen")
        if response.status_code == 200:
            data = response.json()
            resumen = data.get('resumen_ejecutivo', {})
            
            print(f"🎯 Precisión Global: {resumen.get('precision_global', 'N/A')}")
            print(f"✅ Exitosas: {resumen.get('recomendaciones_exitosas', 'N/A')}")
            print(f"❌ Fallidas: {resumen.get('recomendaciones_fallidas', 'N/A')}")
            print(f"⏳ Pendientes: {resumen.get('recomendaciones_pendientes', 'N/A')}")
            
            optimizaciones = data.get('optimizaciones_recientes', [])
            print(f"\n🔧 Optimizaciones Recientes: {len(optimizaciones)}")
            for opt in optimizaciones[:3]:
                fecha = opt.get('fecha', 'N/A')[:19]  # Solo fecha y hora
                print(f"   📅 {fecha}: {opt.get('tipo', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def detalle_btcusdt():
    print("\n🔍 DETALLE BTCUSDT")
    print("-" * 25)
    try:
        response = requests.get(f"{BASE_URL}/reporting/detalle/BTCUSDT")
        if response.status_code == 200:
            data = response.json()
            metricas = data.get('metricas_generales', {})
            
            print(f"📊 Total Recomendaciones: {metricas.get('total_recomendaciones', 'N/A')}")
            print(f"🎯 Precisión: {metricas.get('precision', 'N/A')}")
            print(f"✅ Exitosas: {metricas.get('exitosas', 'N/A')}")
            print(f"❌ Fallidas: {metricas.get('fallidas', 'N/A')}")
            
            analisis = data.get('analisis_por_tipo', {})
            compras = analisis.get('compras', {})
            ventas = analisis.get('ventas', {})
            print(f"\n📈 Compras: {compras.get('total', 'N/A')} (Precisión: {compras.get('precision', 'N/A')})")
            print(f"📉 Ventas: {ventas.get('total', 'N/A')} (Precisión: {ventas.get('precision', 'N/A')})")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def evolucion_pesos():
    print("\n📊 EVOLUCIÓN DE PESOS")
    print("-" * 25)
    try:
        response = requests.get(f"{BASE_URL}/reporting/evolucion")
        if response.status_code == 200:
            data = response.json()
            evolucion = data.get('evolucion_pesos', [])
            
            print(f"🔄 Cambios Registrados: {len(evolucion)}")
            
            for i, cambio in enumerate(evolucion[-3:], 1):  # Últimos 3 cambios
                fecha = cambio.get('fecha', 'N/A')[:19]
                motivo = cambio.get('motivo_ajuste', 'Sin motivo')
                print(f"\n{i}. 📅 {fecha}")
                print(f"   💡 Motivo: {motivo}")
                
                pesos = cambio.get('pesos_nuevos', {})
                if pesos:
                    print(f"   ⚖️  Pesos: RSI={pesos.get('rsi', 'N/A')}, MACD={pesos.get('macd', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def exportar_datos():
    print("\n📤 EXPORTANDO DATOS...")
    print("-" * 25)
    try:
        response = requests.get(f"{BASE_URL}/reporting/exportar/json")
        if response.status_code == 200:
            data = response.json()
            archivo = data.get('archivo_generado', 'N/A')
            print(f"✅ Archivo generado: {archivo}")
            
            metadata = data.get('metadata', {})
            print(f"📊 Total recomendaciones: {metadata.get('total_recomendaciones', 'N/A')}")
            print(f"🔧 Total optimizaciones: {metadata.get('total_optimizaciones', 'N/A')}")
            print(f"📁 El archivo se guardó en el directorio del backend")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def abrir_navegador():
    print("\n🌐 Abriendo reportes en el navegador...")
    try:
        webbrowser.open(f"{BASE_URL}/reporting/resumen")
        print("✅ Resumen ejecutivo abierto en el navegador")
    except Exception as e:
        print(f"❌ Error al abrir navegador: {e}")

def todos_los_reportes():
    print("\n📋 EJECUTANDO TODOS LOS REPORTES...")
    resumen_ejecutivo()
    detalle_btcusdt()
    evolucion_pesos()
    exportar_datos()

def main():
    while True:
        mostrar_menu()
        opcion = input("\n🎯 Selecciona una opción (0-6): ").strip()
        
        if opcion == "1":
            resumen_ejecutivo()
        elif opcion == "2":
            detalle_btcusdt()
        elif opcion == "3":
            evolucion_pesos()
        elif opcion == "4":
            exportar_datos()
        elif opcion == "5":
            abrir_navegador()
        elif opcion == "6":
            todos_los_reportes()
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida. Intenta de nuevo.")
        
        input("\n⏸️  Presiona Enter para continuar...")

if __name__ == "__main__":
    print("🚀 Iniciando Sistema de Reportes...")
    main() 