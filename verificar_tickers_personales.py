#!/usr/bin/env python3
"""
Script para verificar los tickers que el usuario cargó manualmente en el frontend
"""
import sqlite3
import json
import os

def verificar_tickers_personales():
    print("🔍 VERIFICANDO TICKERS PERSONALES DEL FRONTEND")
    print("=" * 60)
    
    # Verificar si hay archivos de localStorage o configuración
    print("📁 Buscando archivos de configuración del frontend...")
    
    # Buscar en el directorio frontend
    frontend_dir = "frontend"
    if os.path.exists(frontend_dir):
        print(f"✅ Directorio frontend encontrado")
        
        # Buscar archivos de configuración
        config_files = []
        for root, dirs, files in os.walk(frontend_dir):
            for file in files:
                if any(keyword in file.lower() for keyword in ['config', 'ticker', 'watchlist', 'default']):
                    config_files.append(os.path.join(root, file))
        
        if config_files:
            print(f"📋 Archivos de configuración encontrados:")
            for file in config_files:
                print(f"   • {file}")
        else:
            print("⚠️ No se encontraron archivos de configuración específicos")
    
    # Verificar la base de datos del backend
    print(f"\n📊 VERIFICANDO BASE DE DATOS DEL BACKEND")
    print("-" * 40)
    
    try:
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        
        # Obtener todos los tickers
        cursor.execute("SELECT symbol, created_at FROM tickers ORDER BY created_at")
        tickers_bd = cursor.fetchall()
        
        print(f"📋 Total tickers en BD: {len(tickers_bd)}")
        
        # Separar por fecha de creación
        tickers_originales = []
        tickers_agregados_script1 = []
        tickers_agregados_script2 = []
        
        for symbol, created_at in tickers_bd:
            if created_at.startswith('2025-07-22'):
                tickers_originales.append(symbol)
            elif created_at.startswith('2025-07-28') and '16:' in created_at:
                tickers_agregados_script1.append(symbol)
            elif created_at.startswith('2025-07-28') and '17:' in created_at:
                tickers_agregados_script2.append(symbol)
        
        print(f"\n📅 Tickers originales (22 de julio):")
        for ticker in tickers_originales:
            print(f"   • {ticker}")
        
        print(f"\n📅 Tickers agregados por primer script:")
        for ticker in tickers_agregados_script1:
            print(f"   • {ticker}")
        
        print(f"\n📅 Tickers agregados por segundo script:")
        for ticker in tickers_agregados_script2:
            print(f"   • {ticker}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verificando BD: {e}")

def verificar_frontend_localStorage():
    print(f"\n🌐 VERIFICANDO FRONTEND (localStorage)")
    print("=" * 60)
    
    print("💡 Para verificar tus tickers personales del frontend:")
    print("   1. Abre el navegador")
    print("   2. Ve a http://localhost:3000")
    print("   3. Abre las herramientas de desarrollador (F12)")
    print("   4. Ve a la pestaña 'Application' o 'Aplicación'")
    print("   5. En el panel izquierdo, busca 'Local Storage'")
    print("   6. Haz clic en 'http://localhost:3000'")
    print("   7. Busca la clave 'tickers'")
    print("   8. Copia el valor JSON y compártelo aquí")
    
    print(f"\n📋 Alternativamente, puedes:")
    print("   - Abrir la consola del navegador (F12)")
    print("   - Ejecutar: console.log(localStorage.getItem('tickers'))")
    print("   - Copiar el resultado")

def verificar_endpoint_tickers():
    print(f"\n🌐 VERIFICANDO ENDPOINT DE TICKERS")
    print("=" * 50)
    
    try:
        import requests
        response = requests.get("http://localhost:8000/tickers/list", timeout=5)
        
        if response.status_code == 200:
            tickers_api = response.json()
            print("✅ Endpoint responde correctamente")
            print(f"📋 Tickers en API: {tickers_api}")
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error consultando endpoint: {e}")

def comparar_tickers():
    print(f"\n🔄 COMPARANDO TICKERS")
    print("=" * 50)
    
    print("📊 Resumen:")
    print("   • Los tickers que agregaste manualmente en el frontend")
    print("     están guardados en localStorage del navegador")
    print("   • Los tickers en la base de datos del backend")
    print("     son los que procesan los jobs automáticamente")
    print()
    print("💡 Recomendación:")
    print("   Si quieres que tus tickers personales también se procesen")
    print("   automáticamente, deberías agregarlos a la base de datos")
    print("   usando el endpoint: POST /tickers/add")

def main():
    # 1. Verificar archivos de configuración
    verificar_tickers_personales()
    
    # 2. Verificar endpoint
    verificar_endpoint_tickers()
    
    # 3. Instrucciones para verificar localStorage
    verificar_frontend_localStorage()
    
    # 4. Comparación
    comparar_tickers()
    
    print(f"\n" + "=" * 60)
    print("🎯 CONCLUSIÓN")
    print("=" * 60)
    print("📊 Tickers en BD (procesados automáticamente): 51")
    print("📱 Tickers en frontend (localStorage): Necesitas verificar")
    print()
    print("💡 Para sincronizar:")
    print("   1. Verifica qué tickers tienes en el frontend")
    print("   2. Si faltan en la BD, agrégalos con el endpoint")
    print("   3. O compárteme la lista y los agrego automáticamente")

if __name__ == "__main__":
    main() 