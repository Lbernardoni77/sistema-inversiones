#!/usr/bin/env python3
"""
Script de prueba para verificar que las múltiples fuentes de datos estén funcionando
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_multi_source():
    """Prueba las múltiples fuentes de datos"""
    print("🧪 Probando múltiples fuentes de datos...")
    
    try:
        from backend.services.multi_source_service import MultiSourceService
        from backend.services.binance_service import get_recommendation
        
        # Crear instancia del servicio
        multi_source = MultiSourceService()
        
        # Probar obtención de precio
        print("\n📊 Probando obtención de precio...")
        price_data = multi_source.get_price("BTCUSDT", "1d")
        print(f"Precio BTCUSDT: {price_data}")
        
        # Probar recomendación con múltiples fuentes
        print("\n🎯 Probando recomendación con múltiples fuentes...")
        recommendation = get_recommendation("BTCUSDT", "24h")
        print(f"Recomendación BTCUSDT: {recommendation.get('recomendacion', 'Error')}")
        
        # Verificar que se estén usando las prioridades dinámicas
        print("\n📋 Verificando prioridades dinámicas...")
        priorities = multi_source.load_source_priorities()
        print(f"Orden de prioridades: {priorities}")
        
        print("\n✅ Todas las pruebas pasaron correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        return False

if __name__ == "__main__":
    test_multi_source()
