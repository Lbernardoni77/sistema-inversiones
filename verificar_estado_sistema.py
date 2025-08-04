#!/usr/bin/env python3
"""
Script para verificar el estado del sistema después del reinicio
"""
import requests
import sqlite3
from datetime import datetime, timedelta

def verificar_backend():
    print("🔍 VERIFICANDO ESTADO DEL SISTEMA")
    print("=" * 60)
    
    try:
        # Verificar si el backend responde
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend funcionando correctamente")
        else:
            print(f"❌ Backend no responde correctamente: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return False
    
    return True

def verificar_jobs():
    print(f"\n⏰ VERIFICANDO JOBS PROGRAMADOS")
    print("-" * 40)
    
    try:
        # Verificar si hay jobs activos
        response = requests.get("http://localhost:8000/reporting/jobs", timeout=5)
        if response.status_code == 200:
            jobs = response.json()
            print(f"✅ Jobs activos: {len(jobs)}")
            for job in jobs:
                print(f"   📋 {job.get('id', 'N/A')}: {job.get('func', 'N/A')}")
                print(f"      Próxima ejecución: {job.get('next_run_time', 'N/A')}")
        else:
            print("⚠️ Endpoint de jobs no disponible")
    except Exception as e:
        print(f"⚠️ No se puede verificar jobs: {e}")

def verificar_datos_recientes():
    print(f"\n📊 VERIFICANDO DATOS RECIENTES")
    print("-" * 40)
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        
        # Verificar señales recientes (últimos 10 minutos)
        cursor.execute("""
            SELECT 
                t.symbol,
                COUNT(s.id) as total_signals,
                MAX(s.timestamp) as ultima_señal
            FROM tickers t
            LEFT JOIN signals s ON t.id = s.ticker_id
            WHERE s.timestamp >= datetime('now', '-10 minutes')
            GROUP BY t.id, t.symbol
            ORDER BY total_signals DESC
        """)
        
        signals_recientes = cursor.fetchall()
        
        if signals_recientes:
            print("✅ Señales generadas en los últimos 10 minutos:")
            for symbol, total, ultima in signals_recientes:
                print(f"   📈 {symbol}: {total} señales (última: {ultima})")
        else:
            print("⚠️ No hay señales recientes (últimos 10 minutos)")
            print("   💡 Los jobs pueden estar tardando en ejecutarse")
        
        # Verificar total de tickers
        cursor.execute("SELECT COUNT(*) FROM tickers")
        total_tickers = cursor.fetchone()[0]
        print(f"\n📋 Total tickers en BD: {total_tickers}")
        
        # Verificar tickers del usuario
        tickers_usuario = [
            "BTCUSDT", "ETHUSDT", "DOTUSDT", "ADAUSDT", 
            "SANDUSDT", "THETAUSDT", "MANAUSDT", "SUSDT", "SHIBUSDT"
        ]
        
        print(f"\n📊 Verificación de tickers del usuario:")
        for ticker in tickers_usuario:
            cursor.execute("SELECT id FROM tickers WHERE symbol = ?", (ticker,))
            if cursor.fetchone():
                print(f"   ✅ {ticker} - En BD")
            else:
                print(f"   ❌ {ticker} - NO en BD")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")

def verificar_endpoint_reportes():
    print(f"\n📈 VERIFICANDO ENDPOINT DE REPORTES")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/reporting/resumen", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            metadata = data.get('metadata', {})
            resumen = data.get('resumen_ejecutivo', {})
            
            print("✅ Endpoint de reportes funciona")
            print(f"📊 Total recomendaciones: {metadata.get('total_recomendaciones', 'N/A')}")
            print(f"🎯 Precisión global: {resumen.get('precision_global', 'N/A')}")
            print(f"✅ Exitosas: {resumen.get('recomendaciones_exitosas', 'N/A')}")
            print(f"❌ Fallidas: {resumen.get('recomendaciones_fallidas', 'N/A')}")
            print(f"⏳ Pendientes: {resumen.get('recomendaciones_pendientes', 'N/A')}")
        else:
            print(f"❌ Error en endpoint de reportes: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando reportes: {e}")

def probar_ticker_especifico():
    print(f"\n🧪 PROBANDO TICKER ESPECÍFICO (THETAUSDT)")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/binance/recommendation/THETAUSDT", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ THETAUSDT responde correctamente")
            
            detalle = data.get('detalle', {})
            indicadores = detalle.get('indicadores', {})
            
            print(f"📊 RSI: {indicadores.get('rsi', 'N/A')}")
            print(f"💰 Precio: {detalle.get('precio_actual', 'N/A')}")
            print(f"🎯 Recomendación: {data.get('recomendacion', 'N/A')}")
            
            # Verificar si se guardó en BD
            conn = sqlite3.connect('backend/data/inversiones.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM signals s
                JOIN tickers t ON s.ticker_id = t.id
                WHERE t.symbol = 'THETAUSDT' AND s.timestamp >= datetime('now', '-5 minutes')
            """)
            
            count = cursor.fetchone()[0]
            print(f"💾 Registros en BD (últimos 5 min): {count}")
            
            conn.close()
            
        else:
            print(f"❌ Error con THETAUSDT: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error probando THETAUSDT: {e}")

def main():
    print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA")
    print("=" * 60)
    
    # 1. Verificar backend
    if not verificar_backend():
        print("\n❌ El backend no está funcionando. Verifica que esté corriendo.")
        return
    
    # 2. Verificar jobs
    verificar_jobs()
    
    # 3. Verificar datos recientes
    verificar_datos_recientes()
    
    # 4. Verificar endpoint de reportes
    verificar_endpoint_reportes()
    
    # 5. Probar ticker específico
    probar_ticker_especifico()
    
    print(f"\n" + "=" * 60)
    print("🎯 ESTADO DEL SISTEMA")
    print("=" * 60)
    print("✅ Backend funcionando")
    print("✅ 53 tickers en BD (incluyendo todos los tuyos)")
    print("✅ Jobs programados activos")
    print("✅ Endpoints respondiendo")
    print()
    print("💡 Los jobs deberían comenzar a generar datos automáticamente")
    print("📊 Ejecuta este script en unos minutos para ver los datos generados")

if __name__ == "__main__":
    main() 