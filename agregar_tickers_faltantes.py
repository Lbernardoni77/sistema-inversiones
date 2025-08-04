#!/usr/bin/env python3
"""
Script para agregar los tickers faltantes del listado personal del usuario
"""
import sqlite3
from datetime import datetime

def agregar_tickers_faltantes():
    print("➕ AGREGANDO TICKERS FALTANTES DEL LISTADO PERSONAL")
    print("=" * 60)
    
    # Tickers que faltan en la BD según el listado personal del usuario
    tickers_faltantes = [
        "THETAUSDT",  # Theta Network - Gaming/Video streaming
        "SUSDT",      # SushiSwap (aunque ya tenemos SUSHIUSDT, agregamos por si acaso)
    ]
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        
        # Verificar tickers existentes
        cursor.execute("SELECT symbol FROM tickers")
        tickers_existentes = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tickers existentes en BD: {len(tickers_existentes)}")
        
        # Agregar tickers faltantes
        tickers_agregados = 0
        
        for ticker in tickers_faltantes:
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
                print(f"⏭️ Ya existe: {ticker}")
        
        # Confirmar cambios
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Proceso completado:")
        print(f"   Tickers agregados: {tickers_agregados}")
        print(f"   Total tickers en BD: {len(tickers_existentes) + tickers_agregados}")
        
        # Verificar resultado final
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        cursor.execute("SELECT symbol FROM tickers ORDER BY symbol")
        todos_tickers = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"\n📊 RESUMEN DEL LISTADO PERSONAL:")
        print("=" * 40)
        
        # Lista completa del usuario
        tickers_usuario = [
            "BTCUSDT", "ETHUSDT", "DOTUSDT", "ADAUSDT", 
            "SANDUSDT", "THETAUSDT", "MANAUSDT", "SUSDT", "SHIBUSDT"
        ]
        
        for ticker in tickers_usuario:
            if ticker in todos_tickers:
                print(f"   ✅ {ticker} - En BD (se procesa automáticamente)")
            else:
                print(f"   ❌ {ticker} - NO está en BD")
        
        print(f"\n📈 BENEFICIOS:")
        print("   • Todos tus tickers personales se procesarán automáticamente")
        print("   • Los jobs generarán señales para todos ellos")
        print("   • Los reportes incluirán datos de tu listado personal")
        print("   • Sincronización completa entre frontend y backend")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def verificar_sincronizacion():
    print(f"\n🔄 VERIFICANDO SINCRONIZACIÓN")
    print("=" * 50)
    
    try:
        import requests
        response = requests.get("http://localhost:8000/tickers/list", timeout=5)
        
        if response.status_code == 200:
            tickers_api = response.json()['tickers']
            print("✅ Endpoint responde correctamente")
            
            # Verificar si están los tickers del usuario
            tickers_usuario = [
                "BTCUSDT", "ETHUSDT", "DOTUSDT", "ADAUSDT", 
                "SANDUSDT", "THETAUSDT", "MANAUSDT", "SUSDT", "SHIBUSDT"
            ]
            
            print(f"\n📊 Verificación de tickers del usuario:")
            for ticker in tickers_usuario:
                if ticker in tickers_api:
                    print(f"   ✅ {ticker} - Disponible en API")
                else:
                    print(f"   ❌ {ticker} - NO disponible en API")
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando API: {e}")

def main():
    # 1. Agregar tickers faltantes
    agregar_tickers_faltantes()
    
    # 2. Verificar sincronización
    verificar_sincronizacion()
    
    print(f"\n" + "=" * 60)
    print("🎯 PRÓXIMOS PASOS")
    print("=" * 60)
    print("1. 🔄 Reinicia el backend para que los cambios tomen efecto")
    print("2. ⏰ Los jobs procesarán automáticamente todos tus tickers")
    print("3. 📊 Los reportes incluirán datos de tu listado personal")
    print("4. 🔗 Sincronización completa entre frontend y backend")
    print()
    print("💡 Para reiniciar el backend:")
    print("   cd backend")
    print("   uvicorn main:app --reload --port 8000")
    print()
    print("🎉 ¡Ahora todos tus tickers personales se procesarán automáticamente!")

if __name__ == "__main__":
    main() 