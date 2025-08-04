#!/usr/bin/env python3
"""
Script para agregar tickers del listado de seguimiento común
"""
import sqlite3
from datetime import datetime

def agregar_tickers_seguimiento():
    print("📊 AGREGANDO TICKERS DEL LISTADO DE SEGUIMIENTO")
    print("=" * 60)
    
    # Tickers más comunes en listados de seguimiento de usuarios
    tickers_seguimiento = [
        # Top 10 por capitalización (excluyendo BTCUSDT y ETHUSDT que ya están)
        "BNBUSDT",   # Binance Coin - #3 por capitalización
        "SOLUSDT",   # Solana - #4 por capitalización
        "XRPUSDT",   # Ripple - #5 por capitalización
        "USDCUSDT",  # USD Coin - #6 por capitalización
        "USDTUSDT",  # Tether - #7 por capitalización
        "ADAUSDT",   # Cardano - #8 por capitalización
        "AVAXUSDT",  # Avalanche - #9 por capitalización
        "DOGEUSDT",  # Dogecoin - #10 por capitalización
        
        # DeFi y Finanzas Descentralizadas
        "UNIUSDT",   # Uniswap - DEX líder
        "LINKUSDT",  # Chainlink - Oracle líder
        "MATICUSDT", # Polygon - Solución de escalabilidad
        "AAVEUSDT",  # Aave - Lending protocol
        "COMPUSDT",  # Compound - Lending protocol
        "SUSHIUSDT", # SushiSwap - DEX
        
        # Layer 1 y Plataformas
        "DOTUSDT",   # Polkadot - Interoperabilidad
        "ATOMUSDT",  # Cosmos - Interoperabilidad
        "NEARUSDT",  # NEAR Protocol - Blockchain de nueva gen
        "ALGOUSDT",  # Algorand - Blockchain de alto rendimiento
        "FTMUSDT",   # Fantom - Blockchain rápida
        "ICPUSDT",   # Internet Computer - Computación descentralizada
        
        # Memecoins y Tokens Populares
        "SHIBUSDT",  # Shiba Inu - Memecoin popular
        "PEPEUSDT",  # Pepe - Memecoin
        "WIFUSDT",   # dogwifhat - Memecoin
        
        # Gaming y Metaverso
        "AXSUSDT",   # Axie Infinity - Gaming
        "SANDUSDT",  # The Sandbox - Metaverso
        "MANAUSDT",  # Decentraland - Metaverso
        "GALAUSDT",  # Gala Games - Gaming
        
        # Infraestructura y Utilidades
        "FILUSDT",   # Filecoin - Almacenamiento
        "LTCUSDT",   # Litecoin - Bitcoin fork
        "BCHUSDT",   # Bitcoin Cash - Bitcoin fork
        "ETCUSDT",   # Ethereum Classic
        "XLMUSDT",   # Stellar - Pagos
        "TRXUSDT",   # Tron - Plataforma
        "EOSUSDT",   # EOS - Plataforma
        "XMRUSDT",   # Monero - Privacidad
        "DASHUSDT",  # Dash - Privacidad
        
        # Stablecoins (para análisis de correlación)
        "DAIUSDT",   # Dai - Stablecoin descentralizado
        "BUSDUSDT",  # Binance USD - Stablecoin
        "TUSDUSDT",  # TrueUSD - Stablecoin
        "FRAXUSDT",  # Frax - Stablecoin algorítmico
        
        # Tokens de Exchange
        "OKBUSDT",   # OKB - Token de OKX
        "HTUSDT",    # Huobi Token - Token de Huobi
        "KCSUSDT",   # KuCoin Token - Token de KuCoin
        
        # DeFi Emergente
        "CRVUSDT",   # Curve - DEX para stablecoins
        "BALUSDT",   # Balancer - DEX
        "YFIUSDT",   # Yearn Finance - Yield farming
        "SNXUSDT",   # Synthetix - Derivados sintéticos
        "1INCHUSDT", # 1inch - DEX aggregator
        "ZRXUSDT",   # 0x Protocol - DEX protocol
    ]
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        
        # Verificar tickers existentes
        cursor.execute("SELECT symbol FROM tickers")
        tickers_existentes = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tickers existentes: {len(tickers_existentes)}")
        
        # Agregar nuevos tickers
        tickers_agregados = 0
        tickers_ya_existentes = 0
        
        for ticker in tickers_seguimiento:
            if ticker not in tickers_existentes:
                try:
                    cursor.execute(
                        "INSERT INTO tickers (symbol, created_at) VALUES (?, ?)",
                        (ticker, datetime.now())
                    )
                    print(f"✅ Agregado: {ticker}")
                    tickers_agregados += 1
                except Exception as e:
                    print(f"❌ Error agregando {ticker}: {e}")
            else:
                tickers_ya_existentes += 1
        
        # Confirmar cambios
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Proceso completado:")
        print(f"   Tickers agregados: {tickers_agregados}")
        print(f"   Tickers ya existentes: {tickers_ya_existentes}")
        print(f"   Total tickers en BD: {len(tickers_existentes) + tickers_agregados}")
        
        # Verificar resultado final
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        cursor.execute("SELECT symbol FROM tickers ORDER BY symbol")
        todos_tickers = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"\n📊 Resumen de tickers por categoría:")
        
        # Categorizar tickers
        categorias = {
            "Top 10": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "USDCUSDT", "USDTUSDT", "ADAUSDT", "AVAXUSDT", "DOGEUSDT"],
            "DeFi": ["UNIUSDT", "LINKUSDT", "MATICUSDT", "AAVEUSDT", "COMPUSDT", "SUSHIUSDT", "CRVUSDT", "BALUSDT", "YFIUSDT", "SNXUSDT", "1INCHUSDT", "ZRXUSDT"],
            "Layer 1": ["DOTUSDT", "ATOMUSDT", "NEARUSDT", "ALGOUSDT", "FTMUSDT", "ICPUSDT"],
            "Memecoins": ["SHIBUSDT", "PEPEUSDT", "WIFUSDT"],
            "Gaming/Metaverso": ["AXSUSDT", "SANDUSDT", "MANAUSDT", "GALAUSDT"],
            "Infraestructura": ["FILUSDT", "LTCUSDT", "BCHUSDT", "ETCUSDT", "XLMUSDT", "TRXUSDT", "EOSUSDT", "XMRUSDT", "DASHUSDT"],
            "Stablecoins": ["DAIUSDT", "BUSDUSDT", "TUSDUSDT", "FRAXUSDT"],
            "Exchange Tokens": ["OKBUSDT", "HTUSDT", "KCSUSDT"]
        }
        
        for categoria, tickers_cat in categorias.items():
            tickers_en_bd = [t for t in tickers_cat if t in todos_tickers]
            if tickers_en_bd:
                print(f"   {categoria}: {len(tickers_en_bd)}/{len(tickers_cat)} tickers")
                for ticker in tickers_en_bd:
                    print(f"     • {ticker}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def verificar_backend():
    print(f"\n⏰ VERIFICANDO BACKEND")
    print("=" * 50)
    
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend funcionando")
            print("💡 Los jobs procesarán automáticamente todos los tickers:")
            print("   - save_signals_job: cada 5 minutos")
            print("   - update_signals_resultado_real: cada 10 minutos")
        else:
            print("❌ Backend no responde")
    except Exception as e:
        print(f"❌ Error verificando backend: {e}")

def main():
    # 1. Agregar tickers del seguimiento
    agregar_tickers_seguimiento()
    
    # 2. Verificar backend
    verificar_backend()
    
    print(f"\n" + "=" * 60)
    print("🎯 PRÓXIMOS PASOS")
    print("=" * 60)
    print("1. 🔄 Reinicia el backend para que los cambios tomen efecto")
    print("2. ⏰ Los jobs procesarán automáticamente todos los tickers")
    print("3. 📊 Ejecuta 'python analizar_tickers_corregido.py' para verificar")
    print("4. 📈 Los reportes mostrarán datos de múltiples categorías")
    print()
    print("💡 Para reiniciar el backend:")
    print("   cd backend")
    print("   uvicorn main:app --reload --port 8000")

if __name__ == "__main__":
    main() 