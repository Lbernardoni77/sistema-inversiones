#!/usr/bin/env python3
"""
Script para agregar más tickers a la base de datos
"""
import sqlite3
from datetime import datetime

def agregar_tickers():
    print("➕ AGREGANDO TICKERS A LA BASE DE DATOS")
    print("=" * 50)
    
    # Lista de tickers populares para agregar
    tickers_populares = [
        "ADAUSDT",   # Cardano
        "SOLUSDT",   # Solana
        "BNBUSDT",   # Binance Coin
        "XRPUSDT",   # Ripple
        "DOTUSDT",   # Polkadot
        "AVAXUSDT",  # Avalanche
        "MATICUSDT", # Polygon
        "LINKUSDT",  # Chainlink
        "UNIUSDT",   # Uniswap
        "ATOMUSDT",  # Cosmos
        "LTCUSDT",   # Litecoin
        "BCHUSDT",   # Bitcoin Cash
        "FILUSDT",   # Filecoin
        "NEARUSDT",  # NEAR Protocol
        "ALGOUSDT",  # Algorand
    ]
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        
        # Verificar tickers existentes
        cursor.execute("SELECT symbol FROM tickers")
        tickers_existentes = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tickers existentes: {tickers_existentes}")
        
        # Agregar nuevos tickers
        tickers_agregados = 0
        for ticker in tickers_populares:
            if ticker not in tickers_existentes:
                cursor.execute(
                    "INSERT INTO tickers (symbol, created_at) VALUES (?, ?)",
                    (ticker, datetime.now())
                )
                print(f"✅ Agregado: {ticker}")
                tickers_agregados += 1
            else:
                print(f"⏭️ Ya existe: {ticker}")
        
        # Confirmar cambios
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Proceso completado:")
        print(f"   Tickers agregados: {tickers_agregados}")
        print(f"   Total tickers en BD: {len(tickers_existentes) + tickers_agregados}")
        
        # Verificar resultado
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        cursor.execute("SELECT symbol FROM tickers ORDER BY symbol")
        todos_tickers = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"\n📊 Todos los tickers en la base de datos:")
        for i, ticker in enumerate(todos_tickers, 1):
            print(f"   {i:2d}. {ticker}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def verificar_jobs():
    print(f"\n⏰ VERIFICANDO JOBS PROGRAMADOS")
    print("=" * 50)
    
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend funcionando")
            print("💡 Los jobs deberían estar ejecutándose automáticamente:")
            print("   - save_signals_job: cada 5 minutos")
            print("   - update_signals_resultado_real: cada 10 minutos")
            print("   - optimize_all_horizons: cada día")
        else:
            print("❌ Backend no responde")
    except Exception as e:
        print(f"❌ Error verificando backend: {e}")

def main():
    # 1. Agregar tickers
    agregar_tickers()
    
    # 2. Verificar jobs
    verificar_jobs()
    
    print(f"\n" + "=" * 50)
    print("🎯 PRÓXIMOS PASOS")
    print("=" * 50)
    print("1. 🔄 Reinicia el backend para que los cambios tomen efecto")
    print("2. ⏰ Los jobs comenzarán a procesar automáticamente")
    print("3. 📊 Ejecuta 'python analizar_tickers_corregido.py' para verificar")
    print("4. 📈 Los reportes deberían mostrar datos de múltiples tickers")
    print()
    print("💡 Para reiniciar el backend:")
    print("   cd backend")
    print("   uvicorn main:app --reload --port 8000")

if __name__ == "__main__":
    main() 