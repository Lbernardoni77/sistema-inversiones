# Usar una imagen base de Python oficial
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libfreetype6-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar solo requirements.txt primero
COPY backend/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del backend
COPY backend/ .

# Crear directorio para la base de datos
RUN mkdir -p data

# Crear tablas al inicio
RUN python create_tables.py

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Exponer puerto
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Comando de inicio explícito
CMD ["python", "/app/start_production.py"]