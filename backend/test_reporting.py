#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de reporting
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_reporting_system():
    """Prueba todos los endpoints del sistema de reporting"""
    
    print("🧪 Iniciando pruebas del sistema de reporting...")
    
    # 1. Probar resumen ejecutivo
    print("\n1️⃣ Probando resumen ejecutivo...")
    try:
        response = requests.get(f"{BASE_URL}/reporting/resumen")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Resumen ejecutivo: {data.get('resumen_ejecutivo', {})}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 2. Probar detalle por símbolo
    print("\n2️⃣ Probando detalle por símbolo...")
    try:
        response = requests.get(f"{BASE_URL}/reporting/detalle/BTCUSDT")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Detalle BTCUSDT: {data.get('metricas_generales', {})}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 3. Probar evolución de pesos
    print("\n3️⃣ Probando evolución de pesos...")
    try:
        response = requests.get(f"{BASE_URL}/reporting/evolucion")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Evolución de pesos: {len(data.get('evolucion_pesos', []))} registros")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 4. Probar registro de recomendación
    print("\n4️⃣ Probando registro de recomendación...")
    try:
        recomendacion_data = {
            "simbolo": "BTCUSDT",
            "recomendacion": "comprar",
            "precio": 45000.0,
            "pesos": {
                "rsi": 0.25,
                "macd": 0.30,
                "soportes_resistencias": 0.45
            },
            "indicadores": {
                "rsi": 35.5,
                "macd": 0.002,
                "sma_50": 44000
            },
            "contexto": {
                "volatilidad": "alta",
                "tendencia": "alcista"
            }
        }
        response = requests.post(f"{BASE_URL}/reporting/registrar-recomendacion", json=recomendacion_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Recomendación registrada: ID {data.get('id')}")
            recomendacion_id = data.get('id')
        else:
            print(f"   ❌ Error: {response.text}")
            recomendacion_id = None
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        recomendacion_id = None
    
    # 5. Probar registro de optimización
    print("\n5️⃣ Probando registro de optimización...")
    try:
        optimizacion_data = {
            "tipo": "pesos",
            "descripcion": "Ajuste de pesos basado en análisis de soportes y resistencias",
            "pesos_anteriores": {
                "rsi": 0.30,
                "macd": 0.35,
                "soportes_resistencias": 0.35
            },
            "pesos_nuevos": {
                "rsi": 0.25,
                "macd": 0.30,
                "soportes_resistencias": 0.45
            },
            "motivo": "Mejora en precisión de soportes y resistencias",
            "metricas": {
                "precision_anterior": 0.75,
                "precision_nueva": 0.82
            },
            "usuario": "sistema"
        }
        response = requests.post(f"{BASE_URL}/reporting/registrar-optimizacion", json=optimizacion_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Optimización registrada: ID {data.get('id')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 6. Probar verificación de recomendación (si se registró una)
    if recomendacion_id:
        print("\n6️⃣ Probando verificación de recomendación...")
        try:
            verificacion_data = {
                "id_recomendacion": recomendacion_id,
                "precio_verificacion": 46000.0,
                "resultado": "exitoso"
            }
            response = requests.post(f"{BASE_URL}/reporting/verificar-recomendacion", json=verificacion_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Recomendación verificada: {data.get('resultado')} (precisión: {data.get('precision')})")
            else:
                print(f"   ❌ Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
    
    # 7. Probar exportación de datos
    print("\n7️⃣ Probando exportación de datos...")
    try:
        response = requests.get(f"{BASE_URL}/reporting/exportar/json")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Datos exportados: {data.get('archivo_generado')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    test_reporting_system() 