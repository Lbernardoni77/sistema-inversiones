#!/usr/bin/env python3
"""
Script para crear las tablas de la base de datos para el sistema de reporting
"""

import os
import sys
from sqlalchemy import create_engine
from models import Base

# Configuración de la base de datos SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'inversiones.db')
engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})

def create_tables():
    """Crea todas las tablas definidas en los modelos"""
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
        print(f"📁 Base de datos: {DB_PATH}")
        
        # Listar las tablas creadas
        inspector = engine.dialect.inspector(engine)
        tables = inspector.get_table_names()
        print(f"📊 Tablas disponibles: {', '.join(tables)}")
        
    except Exception as e:
        print(f"❌ Error al crear las tablas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔧 Creando tablas de la base de datos...")
    create_tables()
    print("✅ Proceso completado") 