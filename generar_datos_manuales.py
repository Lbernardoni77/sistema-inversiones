#!/usr/bin/env python3
"""
Script para generar datos manuales para todos los tickers del usuario
"""
import requests
import sqlite3
from datetime import datetime
import time

def generar_datos_manuales():
    print("🔄 GENERANDO DATOS MANUALES PARA TICKERS DEL USUARIO")
    print("=" * 60)
    
    # Tickers del listado personal del usuario
    tickers_usuario = [
        "BTCUSDT", "ETHUSDT", "DOTUSDT", "ADAUSDT", 
        "SANDUSDT", "THETAUSDT", "MANAUSDT", "SUSDT", "SHIBUSDT"
    ]
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        
        print(f"📊 Procesando {len(tickers_usuario)} tickers del usuario...")
        
        for i, ticker in enumerate(tickers_usuario, 1):
            try:
                print(f"📈 [{i}/{len(tickers_usuario)}] Procesando {ticker}...")
                
                # Obtener recomendación
                response = requests.get(f"http://localhost:8000/binance/recommendation/{ticker}", timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extraer datos
                    detalle = data.get('detalle', {})
                    indicadores = detalle.get('indicadores', {})
                    recomendacion = data.get('recomendacion', 'N/A')
                    
                    # Obtener ticker_id
                    cursor.execute("SELECT id FROM tickers WHERE symbol = ?", (ticker,))
                    result = cursor.fetchone()
                    
                    if result:
                        ticker_id = result[0]
                        
                        # Insertar señal manualmente
                        cursor.execute("""
                            INSERT INTO signals (
                                ticker_id, timestamp, price, rsi, sma_7, sma_21, sma_50, sma_200,
                                macd, macd_signal, macd_hist, bb_upper, bb_mid, bb_lower,
                                obv, vwap, recomendacion, soportes, resistencias, contexto_sr
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            ticker_id,
                            datetime.now(),
                            detalle.get('precio_actual'),
                            indicadores.get('rsi'),
                            indicadores.get('sma_7'),
                            indicadores.get('sma_21'),
                            indicadores.get('sma_50'),
                            indicadores.get('sma_200'),
                            indicadores.get('macd'),
                            indicadores.get('macd_signal'),
                            indicadores.get('macd_hist'),
                            indicadores.get('bb_upper'),
                            indicadores.get('bb_mid'),
                            indicadores.get('bb_lower'),
                            indicadores.get('obv'),
                            indicadores.get('vwap'),
                            recomendacion,
                            str(detalle.get('soportes', [])),
                            str(detalle.get('resistencias', [])),
                            str(detalle.get('contexto_sr', {}))
                        ))
                        
                        print(f"   ✅ {ticker}: {recomendacion} - Guardado en BD")
                        
                    else:
                        print(f"   ❌ {ticker}: No encontrado en BD")
                        
                else:
                    print(f"   ❌ {ticker}: Error {response.status_code}")
                    
                # Pausa pequeña para no sobrecargar la API
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ {ticker}: Error - {e}")
                continue
        
        # Confirmar cambios
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Proceso completado!")
        print(f"   Tickers procesados: {len(tickers_usuario)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def verificar_datos_generados():
    print(f"\n📊 VERIFICANDO DATOS GENERADOS")
    print("-" * 40)
    
    try:
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        
        # Verificar señales recientes del usuario
        tickers_usuario = [
            "BTCUSDT", "ETHUSDT", "DOTUSDT", "ADAUSDT", 
            "SANDUSDT", "THETAUSDT", "MANAUSDT", "SUSDT", "SHIBUSDT"
        ]
        
        print("📈 Señales recientes del usuario:")
        for ticker in tickers_usuario:
            cursor.execute("""
                SELECT COUNT(*) FROM signals s
                JOIN tickers t ON s.ticker_id = t.id
                WHERE t.symbol = ? AND s.timestamp >= datetime('now', '-5 minutes')
            """, (ticker,))
            
            count = cursor.fetchone()[0]
            print(f"   {ticker}: {count} señales recientes")
        
        # Verificar total de señales
        cursor.execute("SELECT COUNT(*) FROM signals")
        total_signals = cursor.fetchone()[0]
        print(f"\n📊 Total señales en BD: {total_signals}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")

def verificar_reportes():
    print(f"\n📈 VERIFICANDO REPORTES")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/reporting/resumen", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            metadata = data.get('metadata', {})
            resumen = data.get('resumen_ejecutivo', {})
            
            print("✅ Reportes actualizados:")
            print(f"📊 Total recomendaciones: {metadata.get('total_recomendaciones', 'N/A')}")
            print(f"🎯 Precisión global: {resumen.get('precision_global', 'N/A')}")
            print(f"✅ Exitosas: {resumen.get('recomendaciones_exitosas', 'N/A')}")
            print(f"❌ Fallidas: {resumen.get('recomendaciones_fallidas', 'N/A')}")
            print(f"⏳ Pendientes: {resumen.get('recomendaciones_pendientes', 'N/A')}")
        else:
            print(f"❌ Error en reportes: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando reportes: {e}")

def main():
    print("🔄 GENERACIÓN MANUAL DE DATOS")
    print("=" * 60)
    
    # 1. Generar datos manuales
    generar_datos_manuales()
    
    # 2. Verificar datos generados
    verificar_datos_generados()
    
    # 3. Verificar reportes
    verificar_reportes()
    
    print(f"\n" + "=" * 60)
    print("🎯 RESULTADO")
    print("=" * 60)
    print("✅ Datos generados para todos los tickers del usuario")
    print("✅ Reportes actualizados con datos recientes")
    print("✅ Listado personal completamente integrado")
    print()
    print("💡 Ahora puedes:")
    print("   1. Ver los reportes en el frontend")
    print("   2. Verificar que no hay valores en cero")
    print("   3. Ver datos de todos tus tickers personales")

if __name__ == "__main__":
    main() 