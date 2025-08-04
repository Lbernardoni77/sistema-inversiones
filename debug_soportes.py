#!/usr/bin/env python3
"""
Script para debuggear por qué no se devuelven soportes y resistencias
"""
import requests
import json

def debug_soportes_resistencias():
    print("🔍 DEBUG SOPORTES Y RESISTENCIAS")
    print("=" * 50)
    
    # URL del backend
    base_url = "http://localhost:8000"
    symbol = "BTCUSDT"
    
    try:
        # Obtener recomendación
        url = f"{base_url}/binance/recommendation/{symbol}"
        print(f"🌐 Haciendo request a: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Imprimir toda la respuesta para debug
            print(f"\n📋 Respuesta completa:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Buscar soportes y resistencias en diferentes ubicaciones
            print(f"\n🔍 Buscando soportes y resistencias:")
            
            # En el nivel raíz
            soportes_raiz = data.get('soportes', [])
            resistencias_raiz = data.get('resistencias', [])
            print(f"   Nivel raíz - Soportes: {soportes_raiz}")
            print(f"   Nivel raíz - Resistencias: {resistencias_raiz}")
            
            # En el detalle
            detalle = data.get('detalle', {})
            soportes_detalle = detalle.get('soportes', [])
            resistencias_detalle = detalle.get('resistencias', [])
            print(f"   En detalle - Soportes: {soportes_detalle}")
            print(f"   En detalle - Resistencias: {resistencias_detalle}")
            
            # En contexto_sr
            contexto_sr = detalle.get('contexto_sr', {})
            soportes_contexto = contexto_sr.get('soportes', [])
            resistencias_contexto = contexto_sr.get('resistencias', [])
            print(f"   En contexto_sr - Soportes: {soportes_contexto}")
            print(f"   En contexto_sr - Resistencias: {resistencias_contexto}")
            
            # Verificar si hay datos de klines
            indicadores = detalle.get('indicadores', {})
            print(f"\n📊 Indicadores disponibles:")
            for key, value in indicadores.items():
                print(f"   {key}: {value}")
                
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    debug_soportes_resistencias() 