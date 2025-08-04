# 📊 Guía del Sistema de Reporting y Auditoría

## 🎯 Descripción General

El sistema de reporting y auditoría permite hacer seguimiento completo del rendimiento del motor de recomendaciones, incluyendo:

- **Historial de optimizaciones**: Registro de todos los ajustes realizados al motor
- **Seguimiento de recomendaciones**: Comparación entre recomendaciones y resultados reales
- **Análisis de rendimiento**: Métricas de precisión y efectividad por símbolo y periodo
- **Exportación de datos**: Generación de reportes en JSON y CSV

## 🗄️ Estructura de la Base de Datos

### Tabla: `optimization_history`
Registra cada optimización realizada al motor de decisión:

```sql
- id: Identificador único
- fecha: Fecha y hora de la optimización
- tipo_optimizacion: Tipo de ajuste ('pesos', 'parametros', 'nuevo_indicador')
- descripcion: Descripción detallada del cambio
- pesos_anteriores: Pesos antes del ajuste (JSON)
- pesos_nuevos: Pesos después del ajuste (JSON)
- parametros_anteriores: Parámetros antes del ajuste (JSON)
- parametros_nuevos: Parámetros después del ajuste (JSON)
- motivo_ajuste: Justificación del cambio
- metricas_resultado: Métricas de rendimiento (JSON)
- usuario: Usuario que realizó el ajuste
```

### Tabla: `recommendation_performance`
Registra cada recomendación y su resultado:

```sql
- id: Identificador único
- fecha_recomendacion: Fecha de la recomendación
- fecha_verificacion: Fecha de verificación del resultado
- simbolo: Símbolo del activo
- recomendacion: Tipo de recomendación ('comprar', 'vender', 'mantener')
- precio_recomendacion: Precio al momento de la recomendación
- precio_verificacion: Precio al momento de la verificación
- resultado: Resultado ('exitoso', 'fallido', 'neutral')
- precision: Precisión de la recomendación (0.0 a 1.0)
- pesos_utilizados: Pesos utilizados en la decisión (JSON)
- indicadores_utilizados: Indicadores técnicos utilizados (JSON)
- contexto_mercado: Contexto del mercado (JSON)
```

## 🔌 Endpoints Disponibles

### 1. Resumen Ejecutivo
**GET** `/reporting/resumen`

Obtiene un resumen general del rendimiento del sistema.

**Parámetros opcionales:**
- `fecha_inicio`: Fecha de inicio (formato ISO)
- `fecha_fin`: Fecha de fin (formato ISO)

**Ejemplo de respuesta:**
```json
{
  "metadata": {
    "fecha_consulta": "2024-01-15T10:30:00",
    "periodo_analizado": "2024-01-01 a 2024-01-15",
    "total_recomendaciones": 150
  },
  "resumen_ejecutivo": {
    "precision_global": 0.78,
    "recomendaciones_exitosas": 117,
    "recomendaciones_fallidas": 33,
    "recomendaciones_pendientes": 0
  },
  "optimizaciones_recientes": [
    {
      "fecha": "2024-01-10T14:30:00",
      "tipo": "pesos",
      "descripcion": "Ajuste de pesos de soportes y resistencias",
      "motivo": "Mejora en precisión"
    }
  ]
}
```

### 2. Detalle por Símbolo
**GET** `/reporting/detalle/{simbolo}`

Análisis detallado del rendimiento por símbolo específico.

**Parámetros:**
- `simbolo`: Símbolo del activo (ej: BTCUSDT)
- `fecha_inicio`: Fecha de inicio (opcional)
- `fecha_fin`: Fecha de fin (opcional)

**Ejemplo de respuesta:**
```json
{
  "simbolo": "BTCUSDT",
  "periodo_analizado": "2024-01-01 a 2024-01-15",
  "metricas_generales": {
    "total_recomendaciones": 45,
    "precision": 0.82,
    "exitosas": 37,
    "fallidas": 8
  },
  "analisis_por_tipo": {
    "compras": {
      "total": 25,
      "exitosas": 22,
      "precision": 0.88
    },
    "ventas": {
      "total": 20,
      "exitosas": 15,
      "precision": 0.75
    }
  },
  "recomendaciones_recientes": [
    {
      "fecha": "2024-01-15T09:00:00",
      "recomendacion": "comprar",
      "precio_recomendacion": 45000.0,
      "resultado": "exitoso",
      "precision": 1.0
    }
  ]
}
```

### 3. Evolución de Pesos
**GET** `/reporting/evolucion`

Historial de cambios en los pesos del motor de decisión.

**Parámetros opcionales:**
- `fecha_inicio`: Fecha de inicio
- `fecha_fin`: Fecha de fin

**Ejemplo de respuesta:**
```json
{
  "evolucion_pesos": [
    {
      "fecha": "2024-01-10T14:30:00",
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
      "motivo_ajuste": "Mejora en precisión de soportes",
      "metricas_resultado": {
        "precision_anterior": 0.75,
        "precision_nueva": 0.82
      }
    }
  ]
}
```

### 4. Registrar Recomendación
**POST** `/reporting/registrar-recomendacion`

Registra una nueva recomendación para seguimiento posterior.

**Body:**
```json
{
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
```

### 5. Verificar Recomendación
**POST** `/reporting/verificar-recomendacion`

Verifica el resultado de una recomendación previa.

**Body:**
```json
{
  "id_recomendacion": 123,
  "precio_verificacion": 46000.0,
  "resultado": "exitoso"
}
```

### 6. Registrar Optimización
**POST** `/reporting/registrar-optimizacion`

Registra una nueva optimización en el historial.

**Body:**
```json
{
  "tipo": "pesos",
  "descripcion": "Ajuste de pesos basado en análisis",
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
  "motivo": "Mejora en precisión",
  "metricas": {
    "precision_anterior": 0.75,
    "precision_nueva": 0.82
  },
  "usuario": "sistema"
}
```

### 7. Exportar Datos
**GET** `/reporting/exportar/{formato}`

Exporta los datos en el formato especificado.

**Parámetros:**
- `formato`: Formato de exportación ('json' o 'csv')
- `fecha_inicio`: Fecha de inicio (opcional)
- `fecha_fin`: Fecha de fin (opcional)

## 📈 Casos de Uso

### 1. Análisis de Rendimiento Semanal
```bash
# Obtener resumen de la última semana
curl "http://localhost:8000/reporting/resumen?fecha_inicio=2024-01-08&fecha_fin=2024-01-15"
```

### 2. Seguimiento de un Símbolo Específico
```bash
# Analizar rendimiento de BTCUSDT
curl "http://localhost:8000/reporting/detalle/BTCUSDT"
```

### 3. Exportar Datos para Análisis
```bash
# Exportar datos del último mes en CSV
curl "http://localhost:8000/reporting/exportar/csv?fecha_inicio=2023-12-15&fecha_fin=2024-01-15"
```

### 4. Registrar una Optimización
```bash
curl -X POST "http://localhost:8000/reporting/registrar-optimizacion" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "pesos",
    "descripcion": "Ajuste automático basado en análisis de precisión",
    "pesos_anteriores": {"rsi": 0.30, "macd": 0.35, "soportes_resistencias": 0.35},
    "pesos_nuevos": {"rsi": 0.25, "macd": 0.30, "soportes_resistencias": 0.45},
    "motivo": "Mejora en precisión de soportes y resistencias",
    "metricas": {"precision_anterior": 0.75, "precision_nueva": 0.82}
  }'
```

## 🔧 Integración con el Motor de Decisiones

Para integrar el sistema de reporting con el motor de decisiones existente:

1. **Registrar cada recomendación** al momento de generarla
2. **Verificar resultados** después de un periodo de tiempo
3. **Registrar optimizaciones** cuando se ajusten los pesos
4. **Analizar rendimiento** regularmente para identificar mejoras

### Ejemplo de Integración:
```python
# En el motor de decisiones
from services.reporting_service import ReportingService

# Al generar una recomendación
reporting_service = ReportingService(db_session)
performance_id = reporting_service.registrar_recomendacion(
    simbolo="BTCUSDT",
    recomendacion="comprar",
    precio_recomendacion=45000.0,
    pesos_utilizados=pesos_actuales,
    indicadores_utilizados=indicadores_calculados,
    contexto_mercado=contexto_actual
)

# Después de un periodo, verificar el resultado
reporting_service.verificar_recomendacion(
    id_recomendacion=performance_id,
    precio_verificacion=46000.0,
    resultado="exitoso"
)
```

## 📊 Métricas y KPIs

### Métricas Principales:
- **Precisión Global**: Porcentaje de recomendaciones exitosas
- **Precisión por Símbolo**: Rendimiento específico por activo
- **Precisión por Tipo**: Comparación entre compras y ventas
- **Evolución Temporal**: Tendencias de rendimiento

### KPIs Recomendados:
- Precisión mínima del 70%
- Mejora continua en el tiempo
- Balance entre compras y ventas
- Reducción de falsos positivos

## 🚀 Próximos Pasos

1. **Integración automática** con el motor de decisiones
2. **Dashboard web** para visualización en tiempo real
3. **Alertas automáticas** cuando la precisión baje
4. **Análisis predictivo** para optimización automática
5. **Reportes programados** por email

---

**Nota**: Para reiniciar el backend después de cambios, usa:
```bash
uvicorn main:app --reload --port 8000
``` 