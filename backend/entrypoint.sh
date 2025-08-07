#!/bin/sh
set -e

# Asegurar que estamos en el directorio correcto
cd /app

# Crear tablas si no existen
python create_tables.py

# Iniciar la aplicación
exec python start_production.py
