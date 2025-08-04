import uvicorn
import os
from main import app

if __name__ == "__main__":
    # Configuración para producción
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"  # Permite conexiones externas
    
    print(f"🚀 Iniciando servidor en {host}:{port}")
    print("📊 Sistema de inversiones - Backend")
    print("🌐 Accesible desde cualquier lugar")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,  # Desactivar reload en producción
        workers=1
    ) 