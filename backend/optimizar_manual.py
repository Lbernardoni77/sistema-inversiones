import requests
import json
from datetime import datetime

def optimizar_manual():
    """Script para ejecutar optimización manual del sistema de aprendizaje"""
    
    base_url = "http://localhost:8000"
    
    print("🔧 OPTIMIZACIÓN MANUAL DEL SISTEMA DE APRENDIZAJE")
    print("=" * 55)
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Verificar estado antes de optimizar
        print("📊 Estado actual:")
        response = requests.get(f"{base_url}/learning/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   Total señales: {status.get('total_señales', 0)}")
            print(f"   Señales con resultados: {status.get('señales_con_resultados', 0)}")
            print(f"   Tasa de acierto actual: {status.get('tasa_acierto_aproximada', 'N/A')}")
        print()
        
        # Ejecutar optimización
        print("🤖 Ejecutando optimización...")
        response = requests.post(f"{base_url}/learning/optimize-now")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"   Status: {resultado.get('status', 'N/A')}")
            print(f"   Mensaje: {resultado.get('mensaje', 'N/A')}")
            
            if 'resultados' in resultado:
                print("\n   📈 Resultados por horizonte:")
                for horizonte, estado in resultado['resultados'].items():
                    print(f"      {horizonte}: {estado}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Respuesta: {response.text}")
        
        print()
        
        # Verificar estado después de optimizar
        print("📊 Estado después de la optimización:")
        response = requests.get(f"{base_url}/learning/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   Tasa de acierto nueva: {status.get('tasa_acierto_aproximada', 'N/A')}")
            
            if 'pesos_optimizados' in status:
                print("\n   📈 Nuevos pesos optimizados:")
                for indicador, peso in status['pesos_optimizados'].items():
                    print(f"      {indicador}: {peso}")
        
        print("\n✅ Optimización completada")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al backend")
        print("   Asegúrate de que el backend esté corriendo en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    optimizar_manual() 