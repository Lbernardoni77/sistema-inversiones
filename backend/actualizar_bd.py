import sqlite3
import os

def actualizar_base_datos():
    """Actualiza la base de datos agregando las columnas faltantes para el sistema de aprendizaje"""
    
    db_path = 'data/inversiones.db'
    if not os.path.exists(db_path):
        print("❌ No se encontró la base de datos")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Columnas que necesitamos agregar
    columnas_faltantes = [
        'sharpe_ratio',
        'resultado_real',
        'resultado_real_1h', 
        'resultado_real_4h',
        'resultado_real_12h',
        'resultado_real_24h',
        'resultado_real_7d',
        'resultado_real_1mes'
    ]
    
    # Verificar qué columnas ya existen
    cursor.execute('PRAGMA table_info(signals)')
    columnas_existentes = [col[1] for col in cursor.fetchall()]
    
    print("Columnas existentes:", columnas_existentes)
    print("Columnas a agregar:", columnas_faltantes)
    
    # Agregar columnas faltantes
    for columna in columnas_faltantes:
        if columna not in columnas_existentes:
            try:
                if columna == 'sharpe_ratio':
                    cursor.execute(f'ALTER TABLE signals ADD COLUMN {columna} FLOAT')
                else:
                    cursor.execute(f'ALTER TABLE signals ADD COLUMN {columna} VARCHAR')
                print(f"✅ Agregada columna: {columna}")
            except Exception as e:
                print(f"❌ Error agregando {columna}: {e}")
    
    # Crear tablas de optimización si no existen
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_history (
                id INTEGER PRIMARY KEY,
                fecha DATETIME,
                tipo_optimizacion VARCHAR(100),
                descripcion TEXT,
                pesos_anteriores TEXT,
                pesos_nuevos TEXT,
                parametros_anteriores TEXT,
                parametros_nuevos TEXT,
                motivo_ajuste TEXT,
                metricas_resultado TEXT,
                usuario VARCHAR(100)
            )
        ''')
        print("✅ Tabla optimization_history creada/verificada")
    except Exception as e:
        print(f"❌ Error con optimization_history: {e}")
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendation_performance (
                id INTEGER PRIMARY KEY,
                fecha_recomendacion DATETIME,
                fecha_verificacion DATETIME,
                simbolo VARCHAR(20),
                recomendacion VARCHAR(20),
                precio_recomendacion FLOAT,
                precio_verificacion FLOAT,
                resultado VARCHAR(20),
                precision FLOAT,
                pesos_utilizados TEXT,
                indicadores_utilizados TEXT,
                contexto_mercado TEXT
            )
        ''')
        print("✅ Tabla recommendation_performance creada/verificada")
    except Exception as e:
        print(f"❌ Error con recommendation_performance: {e}")
    
    conn.commit()
    conn.close()
    print("🎉 Base de datos actualizada exitosamente")

if __name__ == "__main__":
    actualizar_base_datos() 