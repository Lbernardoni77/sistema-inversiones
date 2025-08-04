#!/usr/bin/env python3
import requests

def test_horizon_changes():
    print("🧪 Probando cambios de horizonte...")
    
    # Probar diferentes horizontes
    horizontes = ["1h", "4h", "24h", "7d"]
    
    for horizonte in horizontes:
        print(f"\n📊 Horizonte: {horizonte}")
        try:
            response = requests.get(f"http://localhost:8000/binance/recommendation/BTCUSDT?horizonte={horizonte}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Recomendación: {data.get('recomendacion')}")
                print(f"   ✅ Horizonte: {data.get('horizonte')}")
                
                # Mostrar motivos desde detalle
                detalle = data.get('detalle', {})
                motivos = detalle.get('motivo', [])
                print(f"   ✅ Motivos: {len(motivos)} factores")
                
                # Mostrar algunos motivos
                for motivo in motivos[:3]:  # Solo mostrar los primeros 3
                    print(f"      - {motivo}")
                
                # Mostrar pesos aplicados si están disponibles
                if 'pesos_aplicados' in data:
                    pesos = data.get('pesos_aplicados', {})
                    print(f"   ✅ Pesos aplicados: RSI={pesos.get('rsi', 'N/A')}, MACD={pesos.get('macd', 'N/A')}")
            else:
                print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_horizon_changes() 