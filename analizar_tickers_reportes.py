#!/usr/bin/env python3
"""
Script para analizar por qué solo BTCUSDT tiene datos en los reportes
"""
import sqlite3
import pandas as pd
import requests
import json
from datetime import datetime, timedelta

def analizar_base_datos():
    print("🔍 ANALIZANDO BASE DE DATOS")
    print("=" * 50)
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        
        # Verificar tablas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        print(f"📋 Tablas encontradas: {[tabla[0] for tabla in tablas]}")
        
        # Analizar tabla de señales
        if ('signals',) in tablas:
            print("\n📊 ANALIZANDO TABLA SIGNALS:")
            cursor.execute("SELECT symbol, COUNT(*) as total FROM signals GROUP BY symbol ORDER BY total DESC")
            signals_por_symbol = cursor.fetchall()
            
            for symbol, count in signals_por_symbol:
                print(f"   {symbol}: {count} registros")
            
            # Verificar datos recientes
            print("\n📅 DATOS RECIENTES (últimas 24h):")
            cursor.execute("""
                SELECT symbol, COUNT(*) as total 
                FROM signals 
                WHERE timestamp >= datetime('now', '-1 day')
                GROUP BY symbol 
                ORDER BY total DESC
            """)
            signals_recientes = cursor.fetchall()
            
            for symbol, count in signals_recientes:
                print(f"   {symbol}: {count} registros")
        
        # Analizar tabla de performance
        if ('recommendation_performance',) in tablas:
            print("\n📈 ANALIZANDO TABLA RECOMMENDATION_PERFORMANCE:")
            cursor.execute("SELECT symbol, COUNT(*) as total FROM recommendation_performance GROUP BY symbol ORDER BY total DESC")
            perf_por_symbol = cursor.fetchall()
            
            for symbol, count in perf_por_symbol:
                print(f"   {symbol}: {count} registros")
        
        # Analizar tabla de optimización
        if ('optimization_history',) in tablas:
            print("\n⚙️ ANALIZANDO TABLA OPTIMIZATION_HISTORY:")
            cursor.execute("SELECT symbol, COUNT(*) as total FROM optimization_history GROUP BY symbol ORDER BY total DESC")
            opt_por_symbol = cursor.fetchall()
            
            for symbol, count in opt_por_symbol:
                print(f"   {symbol}: {count} registros")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analizando base de datos: {e}")

def analizar_endpoint_reportes():
    print("\n🌐 ANALIZANDO ENDPOINT DE REPORTES")
    print("=" * 50)
    
    try:
        # Probar endpoint de reportes
        url = "http://localhost:8000/reporting/resumen"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint responde correctamente")
            
            # Analizar datos por símbolo
            if 'datos_por_symbol' in data:
                print("\n📊 DATOS POR SÍMBOLO:")
                for symbol, info in data['datos_por_symbol'].items():
                    print(f"\n   {symbol}:")
                    for key, value in info.items():
                        print(f"     {key}: {value}")
            else:
                print("⚠️ No se encontró 'datos_por_symbol' en la respuesta")
                print(f"📋 Respuesta completa: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error consultando endpoint: {e}")

def probar_tickers_individuales():
    print("\n🧪 PROBANDO TICKERS INDIVIDUALES")
    print("=" * 50)
    
    tickers = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
    
    for ticker in tickers:
        print(f"\n📊 Probando {ticker}:")
        try:
            # Probar endpoint de recomendación
            url = f"http://localhost:8000/binance/recommendation/{ticker}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar si tiene datos válidos
                detalle = data.get('detalle', {})
                indicadores = detalle.get('indicadores', {})
                
                # Contar indicadores no nulos
                indicadores_validos = sum(1 for v in indicadores.values() if v is not None and v != 0)
                total_indicadores = len(indicadores)
                
                print(f"   ✅ Respuesta exitosa")
                print(f"   📊 Indicadores válidos: {indicadores_validos}/{total_indicadores}")
                
                # Verificar soportes y resistencias
                soportes = detalle.get('soportes', [])
                resistencias = detalle.get('resistencias', [])
                print(f"   🟢 Soportes: {len(soportes)} niveles")
                print(f"   🔴 Resistencias: {len(resistencias)} niveles")
                
                # Verificar precio
                precio = detalle.get('precio_actual')
                print(f"   💰 Precio: {precio}")
                
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def verificar_jobs_programados():
    print("\n⏰ VERIFICANDO JOBS PROGRAMADOS")
    print("=" * 50)
    
    try:
        # Verificar si hay jobs activos
        url = "http://localhost:8000/reporting/jobs"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            jobs = response.json()
            print("✅ Jobs encontrados:")
            for job in jobs:
                print(f"   📋 {job.get('id', 'N/A')}: {job.get('func', 'N/A')}")
                print(f"      Estado: {job.get('next_run_time', 'N/A')}")
        else:
            print(f"❌ Error consultando jobs: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def generar_recomendaciones():
    print("\n🔄 GENERANDO RECOMENDACIONES MANUALMENTE")
    print("=" * 50)
    
    tickers = ["ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
    
    for ticker in tickers:
        print(f"\n📊 Generando recomendación para {ticker}:")
        try:
            # Generar recomendación
            url = f"http://localhost:8000/binance/recommendation/{ticker}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                print(f"   ✅ Recomendación generada exitosamente")
                
                # Verificar si se guardó en la base de datos
                conn = sqlite3.connect('backend/data/inversiones.db')
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM signals 
                    WHERE symbol = ? AND timestamp >= datetime('now', '-5 minutes')
                """, (ticker,))
                
                count = cursor.fetchone()[0]
                print(f"   💾 Registros en BD (últimos 5 min): {count}")
                
                conn.close()
                
            else:
                print(f"   ❌ Error generando recomendación: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    print("🔍 ANÁLISIS COMPLETO DE TICKERS EN REPORTES")
    print("=" * 60)
    
    # 1. Analizar base de datos
    analizar_base_datos()
    
    # 2. Analizar endpoint de reportes
    analizar_endpoint_reportes()
    
    # 3. Probar tickers individuales
    probar_tickers_individuales()
    
    # 4. Verificar jobs programados
    verificar_jobs_programados()
    
    # 5. Generar recomendaciones manualmente
    generar_recomendaciones()
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN Y RECOMENDACIONES")
    print("=" * 60)
    print("1. 🔍 Verifica que el backend esté corriendo")
    print("2. 📊 Revisa los logs del backend para errores")
    print("3. ⏰ Verifica que los jobs programados estén activos")
    print("4. 💾 Confirma que la base de datos tenga permisos de escritura")
    print("5. 🔄 Genera recomendaciones manualmente para poblar datos")
    print("\n💡 Si solo BTCUSDT tiene datos, puede ser que:")
    print("   - Los otros tickers no se han consultado recientemente")
    print("   - Hay errores en las APIs externas para otros tickers")
    print("   - Los jobs programados no están procesando todos los tickers")

if __name__ == "__main__":
    main() 