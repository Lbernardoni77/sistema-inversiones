#!/usr/bin/env python3
"""
Script para ejecutar manualmente el job de guardar señales
"""
import requests
import sqlite3
from datetime import datetime

def ejecutar_job_manual():
    print("🔄 EJECUTANDO JOB MANUALMENTE")
    print("=" * 50)
    
    try:
        # Ejecutar el job manualmente
        print("📊 Ejecutando save_signals_job...")
        
        # Primero verificar que el backend esté funcionando
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ Backend no está funcionando")
            return
        
        # Obtener lista de tickers
        response = requests.get("http://localhost:8000/tickers/list", timeout=10)
        if response.status_code == 200:
            tickers = response.json()['tickers']
            print(f"📋 Tickers disponibles: {len(tickers)}")
            
            # Procesar algunos tickers manualmente
            tickers_a_procesar = tickers[:5]  # Solo los primeros 5 para prueba
            print(f"🧪 Procesando tickers de prueba: {tickers_a_procesar}")
            
            for ticker in tickers_a_procesar:
                try:
                    print(f"📊 Procesando {ticker}...")
                    response = requests.get(f"http://localhost:8000/binance/recommendation/{ticker}", timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        recomendacion = data.get('recomendacion', 'N/A')
                        print(f"   ✅ {ticker}: {recomendacion}")
                    else:
                        print(f"   ❌ {ticker}: Error {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {ticker}: Error - {e}")
            
            print(f"\n✅ Procesamiento manual completado")
            
        else:
            print(f"❌ Error obteniendo tickers: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error ejecutando job: {e}")

def verificar_datos_generados():
    print(f"\n📊 VERIFICANDO DATOS GENERADOS")
    print("-" * 40)
    
    try:
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        
        # Verificar señales recientes
        cursor.execute("""
            SELECT 
                t.symbol,
                COUNT(s.id) as total_signals,
                MAX(s.timestamp) as ultima_señal
            FROM tickers t
            LEFT JOIN signals s ON t.id = s.ticker_id
            WHERE s.timestamp >= datetime('now', '-5 minutes')
            GROUP BY t.id, t.symbol
            ORDER BY total_signals DESC
        """)
        
        signals_recientes = cursor.fetchall()
        
        if signals_recientes:
            print("✅ Señales generadas en los últimos 5 minutos:")
            for symbol, total, ultima in signals_recientes:
                print(f"   📈 {symbol}: {total} señales (última: {ultima})")
        else:
            print("⚠️ No hay señales recientes")
        
        # Verificar total de señales
        cursor.execute("SELECT COUNT(*) FROM signals")
        total_signals = cursor.fetchone()[0]
        print(f"\n📊 Total señales en BD: {total_signals}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")

def diagnosticar_jobs():
    print(f"\n🔍 DIAGNÓSTICO DE JOBS")
    print("-" * 40)
    
    print("💡 Posibles problemas con los jobs:")
    print("   1. Los jobs pueden no estar configurados correctamente")
    print("   2. Puede haber errores en el código de los jobs")
    print("   3. Los jobs pueden estar ejecutándose pero fallando silenciosamente")
    print("   4. El scheduler puede no estar iniciado correctamente")
    
    print(f"\n🔧 Soluciones:")
    print("   1. Verificar logs del backend para errores")
    print("   2. Revisar la configuración del scheduler")
    print("   3. Ejecutar jobs manualmente para probar")
    print("   4. Verificar que todas las dependencias estén instaladas")

def main():
    print("🔄 EJECUCIÓN MANUAL DE JOBS")
    print("=" * 60)
    
    # 1. Ejecutar job manualmente
    ejecutar_job_manual()
    
    # 2. Verificar datos generados
    verificar_datos_generados()
    
    # 3. Diagnóstico
    diagnosticar_jobs()
    
    print(f"\n" + "=" * 60)
    print("🎯 RECOMENDACIONES")
    print("=" * 60)
    print("1. 🔍 Revisa los logs del backend para errores")
    print("2. ⚙️ Verifica la configuración del scheduler")
    print("3. 🔄 Ejecuta este script varias veces para generar datos")
    print("4. 📊 Verifica los reportes después de generar datos")

if __name__ == "__main__":
    main() 