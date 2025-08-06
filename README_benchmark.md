# 🚀 Sistema de Benchmark Automatizado de Fuentes de Datos

Sistema completo para medir, monitorear y optimizar automáticamente las fuentes de datos de criptomonedas.

## 📋 Características

- **Benchmark automático** cada 15 días
- **Múltiples fuentes** de datos (CoinGecko, CoinMarketCap, CryptoCompare, etc.)
- **Medición de performance** (velocidad, tasa de éxito, completitud)
- **Actualización automática** de prioridades
- **Dashboard web** para monitoreo
- **Notificaciones por email**
- **Backups automáticos**

## 🏗️ Estructura del Proyecto

```
📁 proyecto/
├── 📄 benchmark_fuentes.py          # Script principal de benchmark
├── 📄 auto_benchmark.py             # Automatización cada 15 días
├── 📄 dashboard_fuentes.py          # Dashboard web
├── 📄 requirements_benchmark.txt    # Dependencias
├── 📄 README_benchmark.md           # Esta documentación
├── 📁 config/
│   └── 📄 fuentes_priority.json     # Configuración de prioridades
├── 📁 backups/                      # Backups automáticos
└── 📁 backend/
    └── 📄 services/
        └── 📄 binance_service.py    # Backend actualizado
```

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements_benchmark.txt
```

### 2. Configurar API Keys

Crear archivo `.env` en la raíz del proyecto:

```env
# API Keys (ya configuradas)
COINGECKO_API_KEY=371f310ae1902bbd029cb7bb765526327d62a72a4b397f48996a3a0e7272f50f
COINMARKETCAP_API_KEY=f76a0f82-e398-4343-8fa3-edbc78ae73fc

# Configuración de email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
NOTIFICATION_EMAIL=tu_email@gmail.com
EMAIL_PASSWORD=tu_password_app
```

## 📊 Uso

### 1. Ejecutar Benchmark Manual

```bash
python benchmark_fuentes.py
```

**Resultado esperado:**
```
🚀 Iniciando benchmark de fuentes de datos...

📊 Probando COINGECKO...
  - BTCUSDT (price)...
  - ETHUSDT (price)...
  ...

📈 Analizando resultados...

============================================================
📊 REPORTE DE BENCHMARK DE FUENTES DE DATOS
============================================================
Fecha: 2025-01-06T14:30:00

🏆 RANKING DE PERFORMANCE:
------------------------------------------------------------
 1. COINGECKO      | Tiempo:   0.85s | Éxito:  95.0% | Completitud: 100.0% | Tests: 9/10
 2. COINCAP        | Tiempo:   1.20s | Éxito:  90.0% | Completitud:  95.0% | Tests: 9/10
 3. CRYPTOCOMPARE  | Tiempo:   0.95s | Éxito:  85.0% | Completitud:  90.0% | Tests: 8/10
 ...

🎯 ORDEN RECOMENDADO DE FUENTES:
------------------------------------------------------------
 1. coingecko
 2. coincap
 3. cryptocompare
 4. coinpaprika
 5. yahoo
 6. kraken

============================================================
💾 Resultados guardados en benchmark_results.json
✅ Benchmark completado exitosamente!
```

### 2. Ejecutar Automatización

```bash
python auto_benchmark.py
```

**Funciones:**
- Verifica si han pasado 15 días desde el último benchmark
- Ejecuta benchmark si es necesario
- Compara con resultados anteriores
- Actualiza prioridades si hay cambios significativos
- Crea backups automáticos
- Envía notificaciones

### 3. Iniciar Dashboard Web

```bash
python dashboard_fuentes.py
```

**Acceso:** http://localhost:8080

**Características del dashboard:**
- Estado actual de las fuentes
- Ranking en tiempo real
- Métricas de performance
- Historial de benchmarks
- Auto-refresh cada 30 segundos

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `COINGECKO_API_KEY` | API Key de CoinGecko | `371f310ae1902bbd...` |
| `COINMARKETCAP_API_KEY` | API Key de CoinMarketCap | `f76a0f82-e398-4343...` |
| `CRYPTOCOMPARE_API_KEY` | API Key de CryptoCompare | `tu_key_aqui` |
| `SMTP_SERVER` | Servidor SMTP para emails | `smtp.gmail.com` |
| `SMTP_PORT` | Puerto SMTP | `587` |
| `NOTIFICATION_EMAIL` | Email para notificaciones | `tu_email@gmail.com` |
| `EMAIL_PASSWORD` | Password del email | `tu_password_app` |

### Configuración de Prioridades

El archivo `config/fuentes_priority.json` se actualiza automáticamente:

```json
{
  "last_updated": "2025-01-06T14:30:00",
  "source_order": [
    "coingecko",
    "coincap",
    "cryptocompare",
    "coinpaprika",
    "yahoo",
    "kraken"
  ],
  "performance_data": [...],
  "metadata": {
    "total_sources": 6,
    "benchmark_timestamp": "2025-01-06T14:30:00"
  }
}
```

## 📈 Métricas Medidas

### 1. Velocidad de Respuesta
- Tiempo promedio de respuesta en segundos
- Timeout configurado en 10-15 segundos

### 2. Tasa de Éxito
- Porcentaje de requests exitosos
- Manejo de errores 429, 451, etc.

### 3. Completitud de Datos
- Cantidad de campos requeridos presentes
- Para klines: número de elementos devueltos

### 4. Score Combinado
- 40% velocidad
- 40% tasa de éxito  
- 20% completitud

## 🔄 Automatización

### Programación Manual (Cron/Task Scheduler)

**Windows (Task Scheduler):**
```cmd
# Crear tarea programada
schtasks /create /tn "Benchmark Fuentes" /tr "python auto_benchmark.py" /sc daily /mo 15 /st 02:00
```

**Linux/Mac (Cron):**
```bash
# Editar crontab
crontab -e

# Agregar línea (cada 15 días a las 2:00 AM)
0 2 */15 * * cd /ruta/al/proyecto && python auto_benchmark.py
```

### Integración con Render

Para automatizar en Render, agregar al `requirements.txt`:

```txt
# Dependencias existentes...
httpx>=0.24.0
yfinance>=0.2.0
python-dotenv>=1.0.0
```

Y configurar variables de entorno en Render Dashboard.

## 📊 Fuentes Soportadas

| Fuente | API Key | Precios | Klines | Rate Limit |
|--------|---------|---------|--------|------------|
| **CoinGecko** | ✅ | ✅ | ✅ | 50,000/mes |
| **CoinMarketCap** | ✅ | ✅ | ❌ | 10,000/mes |
| **CryptoCompare** | ✅ | ✅ | ✅ | 100,000/mes |
| **CoinPaprika** | ❌ | ✅ | ❌ | Sin límite |
| **Yahoo Finance** | ❌ | ✅ | ❌ | Sin límite |
| **Kraken** | ❌ | ✅ | ✅ | Sin límite |

## 🚨 Alertas y Notificaciones

### Condiciones de Alerta

- **Cambio significativo** (>20% en métricas)
- **Nueva fuente** disponible
- **Fuente removida** o fallando
- **Benchmark fallido**

### Notificaciones por Email

```html
📊 Benchmark de Fuentes de Datos Completado

🏆 Top 3 Fuentes:
1. COINGECKO
   Tiempo: 0.85s | Éxito: 95.0% | Completitud: 100.0%

2. COINCAP  
   Tiempo: 1.20s | Éxito: 90.0% | Completitud: 95.0%

3. CRYPTOCOMPARE
   Tiempo: 0.95s | Éxito: 85.0% | Completitud: 90.0%

🎯 Orden Recomendado:
1. coingecko
2. coincap
3. cryptocompare
...
```

## 🔍 Troubleshooting

### Problemas Comunes

**1. Error de API Key**
```
❌ Error: API key no configurada
```
**Solución:** Verificar variables de entorno en `.env`

**2. Timeout en requests**
```
❌ Timeout ejecutando benchmark
```
**Solución:** Aumentar timeout en `benchmark_fuentes.py`

**3. Error de email**
```
❌ Error enviando email: Authentication failed
```
**Solución:** Usar password de aplicación en Gmail

**4. Dashboard no carga**
```
❌ Error cargando datos de estado
```
**Solución:** Verificar que existan los archivos de configuración

### Logs

Los logs se guardan en:
- `auto_benchmark.log` - Logs de automatización
- `benchmark_results.json` - Resultados del benchmark
- `backups/` - Backups automáticos

## 🔮 Próximas Mejoras

- [ ] **Gráficos interactivos** en el dashboard
- [ ] **Alertas en tiempo real** para fallos
- [ ] **Métricas históricas** más detalladas
- [ ] **API REST** para consultar resultados
- [ ] **Integración con Slack/Discord**
- [ ] **Machine Learning** para predicción de fallos

## 📞 Soporte

Para problemas o sugerencias:
1. Revisar logs en `auto_benchmark.log`
2. Verificar configuración en `config/fuentes_priority.json`
3. Ejecutar benchmark manual para diagnóstico

---

**¡Sistema listo para optimizar automáticamente tus fuentes de datos! 🚀** 