#!/usr/bin/env python3
"""
Script corregido para analizar datos de tickers usando la estructura correcta de BD
"""
import sqlite3
import pandas as pd
import requests
import json
from datetime import datetime, timedelta

def analizar_base_datos_corregido():
    print("🔍 ANALIZANDO BASE DE DATOS (ESTRUCTURA CORREGIDA)")
    print("=" * 60)
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        
        # Analizar datos por símbolo usando JOIN
        print("\n📊 DATOS POR SÍMBOLO (JOIN signals + tickers):")
        cursor.execute("""
            SELECT 
                t.symbol,
                COUNT(s.id) as total_signals,
                MAX(s.timestamp) as ultima_señal,
                COUNT(CASE WHEN s.timestamp >= datetime('now', '-1 day') THEN 1 END) as señales_24h
            FROM tickers t
            LEFT JOIN signals s ON t.id = s.ticker_id
            GROUP BY t.id, t.symbol
            ORDER BY total_signals DESC
        """)
        
        resultados = cursor.fetchall()
        for symbol, total, ultima, recientes in resultados:
            print(f"   {symbol}:")
            print(f"     Total señales: {total}")
            print(f"     Última señal: {ultima}")
            print(f"     Señales 24h: {recientes}")
        
        # Verificar datos recientes por símbolo
        print("\n📅 DATOS RECIENTES POR SÍMBOLO (últimas 24h):")
        cursor.execute("""
            SELECT 
                t.symbol,
                COUNT(s.id) as total,
                AVG(s.rsi) as rsi_promedio,
                AVG(s.sma_7) as sma7_promedio,
                COUNT(DISTINCT s.recomendacion) as recomendaciones_unicas
            FROM tickers t
            LEFT JOIN signals s ON t.id = s.ticker_id
            WHERE s.timestamp >= datetime('now', '-1 day')
            GROUP BY t.id, t.symbol
            ORDER BY total DESC
        """)
        
        datos_recientes = cursor.fetchall()
        for symbol, total, rsi_avg, sma7_avg, rec_unicas in datos_recientes:
            print(f"   {symbol}:")
            print(f"     Total: {total}")
            print(f"     RSI promedio: {rsi_avg:.2f}" if rsi_avg else "     RSI promedio: N/A")
            print(f"     SMA7 promedio: {sma7_avg:.2f}" if sma7_avg else "     SMA7 promedio: N/A")
            print(f"     Recomendaciones únicas: {rec_unicas}")
        
        # Verificar recomendaciones por símbolo
        print("\n📊 RECOMENDACIONES POR SÍMBOLO:")
        cursor.execute("""
            SELECT 
                t.symbol,
                s.recomendacion,
                COUNT(*) as cantidad
            FROM tickers t
            LEFT JOIN signals s ON t.id = s.ticker_id
            WHERE s.recomendacion IS NOT NULL
            GROUP BY t.symbol, s.recomendacion
            ORDER BY t.symbol, cantidad DESC
        """)
        
        recomendaciones = cursor.fetchall()
        current_symbol = None
        for symbol, rec, cantidad in recomendaciones:
            if symbol != current_symbol:
                print(f"   {symbol}:")
                current_symbol = symbol
            print(f"     {rec}: {cantidad}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analizando base de datos: {e}")

def analizar_endpoint_reportes_corregido():
    print("\n🌐 ANALIZANDO ENDPOINT DE REPORTES")
    print("=" * 50)
    
    try:
        # Probar endpoint de reportes
        url = "http://localhost:8000/reporting/resumen"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint responde correctamente")
            
            # Analizar metadata
            metadata = data.get('metadata', {})
            print(f"📊 Total recomendaciones: {metadata.get('total_recomendaciones', 'N/A')}")
            print(f"📅 Periodo analizado: {metadata.get('periodo_analizado', 'N/A')}")
            
            # Analizar resumen ejecutivo
            resumen = data.get('resumen_ejecutivo', {})
            print(f"🎯 Precisión global: {resumen.get('precision_global', 'N/A')}")
            print(f"✅ Exitosas: {resumen.get('recomendaciones_exitosas', 'N/A')}")
            print(f"❌ Fallidas: {resumen.get('recomendaciones_fallidas', 'N/A')}")
            print(f"⏳ Pendientes: {resumen.get('recomendaciones_pendientes', 'N/A')}")
            
            # Analizar optimizaciones
            optimizaciones = data.get('optimizaciones_recientes', [])
            print(f"⚙️ Optimizaciones recientes: {len(optimizaciones)}")
            
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error consultando endpoint: {e}")

def generar_datos_para_todos_tickers():
    print("\n🔄 GENERANDO DATOS PARA TODOS LOS TICKERS")
    print("=" * 50)
    
    # Obtener lista de tickers de la base de datos
    try:
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT symbol FROM tickers ORDER BY symbol")
        tickers = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"📋 Tickers encontrados: {tickers}")
        
        for ticker in tickers:
            print(f"\n📊 Generando datos para {ticker}:")
            try:
                # Generar recomendación
                url = f"http://localhost:8000/binance/recommendation/{ticker}"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    print(f"   ✅ Recomendación generada")
                    
                    # Verificar si se guardó en la base de datos
                    conn = sqlite3.connect('backend/data/inversiones.db')
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT COUNT(*) FROM signals s
                        JOIN tickers t ON s.ticker_id = t.id
                        WHERE t.symbol = ? AND s.timestamp >= datetime('now', '-5 minutes')
                    """, (ticker,))
                    
                    count = cursor.fetchone()[0]
                    print(f"   💾 Registros en BD (últimos 5 min): {count}")
                    
                    conn.close()
                    
                else:
                    print(f"   ❌ Error {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Error obteniendo tickers: {e}")

def verificar_jobs_y_procesos():
    print("\n⏰ VERIFICANDO JOBS Y PROCESOS")
    print("=" * 50)
    
    try:
        # Verificar si el backend está corriendo
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend funcionando")
        else:
            print("❌ Backend no responde correctamente")
            return
            
        # Verificar jobs programados (si existe el endpoint)
        try:
            jobs_response = requests.get("http://localhost:8000/reporting/jobs", timeout=5)
            if jobs_response.status_code == 200:
                jobs = jobs_response.json()
                print(f"✅ Jobs activos: {len(jobs)}")
                for job in jobs:
                    print(f"   📋 {job.get('id', 'N/A')}: {job.get('func', 'N/A')}")
            else:
                print("⚠️ Endpoint de jobs no disponible")
        except:
            print("⚠️ No se puede verificar jobs")
            
    except Exception as e:
        print(f"❌ Error verificando procesos: {e}")

def main():
    print("🔍 ANÁLISIS COMPLETO DE TICKERS (CORREGIDO)")
    print("=" * 60)
    
    # 1. Analizar base de datos con estructura correcta
    analizar_base_datos_corregido()
    
    # 2. Analizar endpoint de reportes
    analizar_endpoint_reportes_corregido()
    
    # 3. Verificar jobs y procesos
    verificar_jobs_y_procesos()
    
    # 4. Generar datos para todos los tickers
    generar_datos_para_todos_tickers()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNÓSTICO Y SOLUCIONES")
    print("=" * 60)
    print("📊 PROBLEMA IDENTIFICADO:")
    print("   - Solo BTCUSDT y ETHUSDT tienen datos en la base de datos")
    print("   - Los otros tickers no se han consultado recientemente")
    print("   - Los jobs programados pueden no estar funcionando correctamente")
    print()
    print("🔧 SOLUCIONES:")
    print("   1. ✅ Generar recomendaciones manualmente para todos los tickers")
    print("   2. ⏰ Verificar que los jobs programados estén activos")
    print("   3. 📊 Monitorear que se guarden datos regularmente")
    print("   4. 🔄 Configurar jobs para procesar todos los tickers")
    print()
    print("💡 RECOMENDACIONES:")
    print("   - Ejecutar este script regularmente para verificar datos")
    print("   - Configurar alertas si no hay datos de tickers importantes")
    print("   - Revisar logs del backend para errores en jobs")

if __name__ == "__main__":
    main() 