#!/usr/bin/env python3
import requests
import json

def debug_response():
    print("🔍 Debugging API response...")
    
    try:
        response = requests.get("http://localhost:8000/binance/recommendation/BTCUSDT?horizonte=1h")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📋 Response structure:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar campos específicos
            print(f"\n🔍 Campos disponibles:")
            for key in data.keys():
                print(f"  - {key}: {type(data[key])}")
                
            # Verificar detalle
            if 'detalle' in data:
                print(f"\n📊 Detalle:")
                for key in data['detalle'].keys():
                    print(f"  - {key}: {type(data['detalle'][key])}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_response() 