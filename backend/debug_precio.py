import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.binance_service import get_recommendation
from services.cache_service import clear_expired_cache

def debug_precio():
    """Debug para ver qué devuelve get_recommendation"""
    
    print("🔍 Debuggeando get_recommendation...")
    
    # Limpiar cache completamente
    clear_expired_cache()
    print("🗑️ Cache limpiado")
    
    try:
        # Obtener recomendación para BTCUSDT
        rec = get_recommendation("BTCUSDT", "24h")
        
        print("📊 Respuesta completa:")
        print(f"  Recomendación: {rec.get('recomendacion')}")
        print(f"  Puntaje: {rec.get('puntaje_total')}")
        
        # Verificar estructura de detalle
        detalle = rec.get("detalle", {})
        print(f"  ¿Tiene detalle?: {bool(detalle)}")
        
        # Verificar contexto_sr
        contexto_sr = detalle.get("contexto_sr", {})
        print(f"  ¿Tiene contexto_sr?: {bool(contexto_sr)}")
        print(f"  Precio en contexto_sr: {contexto_sr.get('precio')}")
        
        # Verificar estructura completa
        print("\n🔍 Estructura completa de contexto_sr:")
        for key, value in contexto_sr.items():
            print(f"  {key}: {value}")
        
        # Verificar soportes y resistencias
        print(f"\n📈 Soportes: {rec.get('soportes')}")
        print(f"📉 Resistencias: {rec.get('resistencias')}")
        
        # Verificar indicadores
        indicadores = detalle.get("indicadores", {})
        print(f"\n📊 Indicadores disponibles: {list(indicadores.keys())}")
        
        # Verificar estructura completa de la respuesta
        print(f"\n🔍 Claves en la respuesta: {list(rec.keys())}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_precio() 