import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.binance_service import BinanceService
from services.cache_service import clear_expired_cache

def debug_precio():
    """Debug para ver qué devuelve get_recommendation"""
    
    print("🔍 Debuggeando get_recommendation...")
    
    # Limpiar cache completamente
    clear_expired_cache()
    print("🗑️ Cache limpiado")
    
    try:
        # Obtener recomendación para BTCUSDT
        binance_service = BinanceService()
        rec = binance_service.get_recommendation("BTCUSDT")
        
        print("📊 Respuesta completa:")
        print(f"  Recomendación: {rec.get('recommendation')}")
        print(f"  Confidence: {rec.get('confidence')}%")
        print(f"  Precio: {rec.get('price')}")
        
        # Verificar indicadores
        indicators = rec.get("indicators", {})
        print(f"  ¿Tiene indicadores?: {bool(indicators)}")
        
        # Verificar estructura completa
        print("\n🔍 Estructura completa de indicators:")
        for key, value in indicators.items():
            print(f"  {key}: {value}")
        
        # Verificar source
        print(f"\n📊 Source: {rec.get('source')}")
        
        # Verificar timestamp
        print(f"🕒 Timestamp: {rec.get('timestamp')}")
        
        # Verificar estructura completa de la respuesta
        print(f"\n🔍 Claves en la respuesta: {list(rec.keys())}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_precio() 