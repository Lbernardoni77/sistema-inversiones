import requests
import json
from datetime import datetime

class MonitoreoRemoto:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def verificar_estado(self):
        """Verifica el estado general del sistema"""
        try:
            response = requests.get(f"{self.base_url}/learning/status", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error {response.status_code}"}
        except Exception as e:
            return {"error": f"Error de conexión: {str(e)}"}
    
    def obtener_recomendacion(self, symbol="BTCUSDT"):
        """Obtiene recomendación para un símbolo específico"""
        try:
            response = requests.get(f"{self.base_url}/binance/recommendation/{symbol}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error {response.status_code}"}
        except Exception as e:
            return {"error": f"Error de conexión: {str(e)}"}
    
    def listar_tickers(self):
        """Lista todos los tickers en seguimiento"""
        try:
            response = requests.get(f"{self.base_url}/tickers/list", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error {response.status_code}"}
        except Exception as e:
            return {"error": f"Error de conexión: {str(e)}"}
    
    def optimizar_manual(self):
        """Ejecuta optimización manual"""
        try:
            response = requests.post(f"{self.base_url}/learning/optimize-now", timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error {response.status_code}"}
        except Exception as e:
            return {"error": f"Error de conexión: {str(e)}"}
    
    def monitoreo_completo(self):
        """Ejecuta monitoreo completo del sistema"""
        print("🤖 MONITOREO REMOTO DEL SISTEMA DE INVERSIONES")
        print("=" * 60)
        print(f"🌐 URL: {self.base_url}")
        print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Estado del sistema
        print("📊 1. ESTADO DEL SISTEMA")
        print("-" * 30)
        estado = self.verificar_estado()
        
        if "error" not in estado:
            print(f"   Estado: {estado.get('status', 'N/A')}")
            print(f"   Total señales: {estado.get('total_señales', 0)}")
            print(f"   Señales con resultados: {estado.get('señales_con_resultados', 0)}")
            print(f"   Promedio rendimiento: {estado.get('promedio_rendimiento', 'N/A')}")
            print(f"   Tickers optimizados: {estado.get('tickers_optimizados', 0)}")
            print(f"   Última optimización: {estado.get('ultima_optimizacion', 'N/A')}")
            
            if 'resumen_por_ticker' in estado:
                print("\n   📈 Top 5 tickers por rendimiento:")
                tickers = estado['resumen_por_ticker']
                sorted_tickers = sorted(tickers.items(), key=lambda x: x[1]['performance_24h'], reverse=True)
                for ticker, data in sorted_tickers[:5]:
                    print(f"      {ticker}: {data['performance_24h']:.2%} (24h)")
        else:
            print(f"   ❌ Error: {estado['error']}")
        print()
        
        # 2. Recomendación BTC
        print("📈 2. RECOMENDACIÓN BTC")
        print("-" * 30)
        rec_btc = self.obtener_recomendacion("BTCUSDT")
        
        if "error" not in rec_btc:
            print(f"   Recomendación: {rec_btc.get('recomendacion')}")
            print(f"   Puntaje: {rec_btc.get('puntaje_total')}")
            print(f"   Motivo: {rec_btc.get('motivo', 'N/A')}")
            
            if 'pesos_aplicados' in rec_btc:
                print(f"   Pesos aplicados: {rec_btc['pesos_aplicados']}")
        else:
            print(f"   ❌ Error: {rec_btc['error']}")
        print()
        
        # 3. Recomendación ETH
        print("📈 3. RECOMENDACIÓN ETH")
        print("-" * 30)
        rec_eth = self.obtener_recomendacion("ETHUSDT")
        
        if "error" not in rec_eth:
            print(f"   Recomendación: {rec_eth.get('recomendacion')}")
            print(f"   Puntaje: {rec_eth.get('puntaje_total')}")
            print(f"   Motivo: {rec_eth.get('motivo', 'N/A')}")
        else:
            print(f"   ❌ Error: {rec_eth['error']}")
        print()
        
        print("✅ Monitoreo remoto completado")

def main():
    # Configurar URL de tu aplicación desplegada
    # Cambia esto por tu URL real de Render
    base_url = "https://tu-app.onrender.com"  # Cambiar por tu URL
    
    # Crear instancia de monitoreo
    monitor = MonitoreoRemoto(base_url)
    
    # Ejecutar monitoreo completo
    monitor.monitoreo_completo()

if __name__ == "__main__":
    main() 