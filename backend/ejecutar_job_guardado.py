import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import save_signals_job

def ejecutar_job_guardado():
    """Ejecuta el job de guardado de señales manualmente"""
    
    print("💾 Ejecutando job de guardado de señales...")
    
    try:
        save_signals_job()
        print("✅ Job de guardado completado exitosamente")
        
        # Verificar que se guardaron precios
        import sqlite3
        conn = sqlite3.connect('data/inversiones.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM signals WHERE price IS NOT NULL AND price > 0')
        señales_con_precio = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM signals')
        total_señales = cursor.fetchone()[0]
        conn.close()
        
        print(f"📊 Estado de la base de datos:")
        print(f"   - Total de señales: {total_señales}")
        print(f"   - Señales con precio válido: {señales_con_precio}")
        
        if señales_con_precio > 0:
            print("🎉 ¡El sistema está listo para aprender!")
        else:
            print("⚠️ Aún no hay señales con precios válidos")
            
    except Exception as e:
        print(f"❌ Error ejecutando job de guardado: {e}")

if __name__ == "__main__":
    ejecutar_job_guardado() 