import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import update_signals_resultado_real, optimize_all_horizons
from services.learning_service import load_weights, optimize_weights

def ejecutar_aprendizaje():
    """Ejecuta el proceso de aprendizaje completo"""
    
    print("🤖 Iniciando proceso de aprendizaje...")
    
    # 1. Calcular resultados reales de las señales existentes
    print("📊 Calculando resultados reales de señales...")
    try:
        update_signals_resultado_real()
        print("✅ Resultados reales calculados")
    except Exception as e:
        print(f"❌ Error calculando resultados: {e}")
    
    # 2. Verificar pesos actuales
    print("⚖️ Verificando pesos actuales...")
    try:
        weights = load_weights()
        print("Pesos actuales:", weights)
    except Exception as e:
        print(f"❌ Error cargando pesos: {e}")
    
    # 3. Ejecutar optimización
    print("🔧 Ejecutando optimización de pesos...")
    try:
        optimize_all_horizons()
        print("✅ Optimización completada")
    except Exception as e:
        print(f"❌ Error en optimización: {e}")
    
    # 4. Verificar nuevos pesos
    print("⚖️ Verificando nuevos pesos...")
    try:
        new_weights = load_weights()
        print("Nuevos pesos:", new_weights)
    except Exception as e:
        print(f"❌ Error cargando nuevos pesos: {e}")

if __name__ == "__main__":
    ejecutar_aprendizaje() 