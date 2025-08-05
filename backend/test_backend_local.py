#!/usr/bin/env python3
"""
Script para probar el backend localmente
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Iniciando servidor de prueba local...")
    print("📍 URL: http://localhost:8001")
    print("🔍 Health check: http://localhost:8001/healthz")
    print("📊 Prueba: http://localhost:8001/binance/price/SANDUSDT?period=1d")
    print("⏹️  Presiona Ctrl+C para detener")
    print("-" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True) 