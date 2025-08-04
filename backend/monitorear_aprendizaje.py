import requests
import json
from datetime import datetime

def monitorear_aprendizaje():
    """Script para monitorear el estado del sistema de aprendizaje"""
    
    base_url = "http://localhost:8000"
    
    print("🤖 MONITOREO DEL SISTEMA DE APRENDIZAJE")
    print("=" * 50)
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 1. Estado del sistema de aprendizaje
        print("📊 1. ESTADO DEL SISTEMA DE APRENDIZAJE")
        print("-" * 30)
        response = requests.get(f"{base_url}/learning/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   Estado: {status.get('status', 'N/A')}")
            print(f"   Total señales: {status.get('total_señales', 0)}")
            print(f"   Señales con resultados: {status.get('señales_con_resultados', 0)}")
            print(f"   Promedio rendimiento: {status.get('promedio_rendimiento', 'N/A')}")
            print(f"   Tickers optimizados: {status.get('tickers_optimizados', 0)}")
            print(f"   Última optimización: {status.get('ultima_optimizacion', 'N/A')}")
            
            if 'resumen_por_ticker' in status:
                print("\n   📈 Top 5 tickers por rendimiento:")
                tickers = status['resumen_por_ticker']
                sorted_tickers = sorted(tickers.items(), key=lambda x: x[1]['performance_24h'], reverse=True)
                for ticker, data in sorted_tickers[:5]:
                    print(f"      {ticker}: {data['performance_24h']:.2%} (24h)")
        else:
            print(f"   ❌ Error: {response.status_code}")
        print()
        
        # 2. Resumen ejecutivo
        print("📈 2. RESUMEN EJECUTIVO")
        print("-" * 30)
        response = requests.get(f"{base_url}/reporting/resumen")
        if response.status_code == 200:
            resumen = response.json()
            print(f"   Total recomendaciones: {resumen.get('total_recomendaciones', 0)}")
            print(f"   Aciertos: {resumen.get('aciertos', 0)}")
            print(f"   Errores: {resumen.get('errores', 0)}")
            print(f"   Precisión: {resumen.get('precision', 'N/A')}")
            
            if 'por_recomendacion' in resumen:
                print("\n   📊 Por tipo de recomendación:")
                for tipo, datos in resumen['por_recomendacion'].items():
                    print(f"      {tipo}: {datos.get('precision', 'N/A')} precisión")
        else:
            print(f"   ❌ Error: {response.status_code}")
        print()
        
        # 3. Evolución de pesos
        print("⚖️ 3. EVOLUCIÓN DE PESOS")
        print("-" * 30)
        response = requests.get(f"{base_url}/reporting/evolucion")
        if response.status_code == 200:
            evolucion = response.json()
            if 'optimizaciones' in evolucion and evolucion['optimizaciones']:
                print(f"   Total optimizaciones: {len(evolucion['optimizaciones'])}")
                ultima = evolucion['optimizaciones'][-1]
                print(f"   Última optimización: {ultima.get('fecha', 'N/A')}")
                print(f"   Tipo: {ultima.get('tipo_optimizacion', 'N/A')}")
                print(f"   Mejora: {ultima.get('mejora_precision', 'N/A')}")
            else:
                print("   ⏳ Aún no hay optimizaciones registradas")
        else:
            print(f"   ❌ Error: {response.status_code}")
        print()
        
        # 4. Estadísticas del cache
        print("💾 4. ESTADÍSTICAS DEL CACHE")
        print("-" * 30)
        response = requests.get(f"{base_url}/cache/stats")
        if response.status_code == 200:
            cache_stats = response.json()
            print(f"   Hits: {cache_stats.get('hits', 0)}")
            print(f"   Misses: {cache_stats.get('misses', 0)}")
            print(f"   Hit rate: {cache_stats.get('hit_rate', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
        print()
        
        print("✅ Monitoreo completado")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al backend")
        print("   Asegúrate de que el backend esté corriendo en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    monitorear_aprendizaje() 