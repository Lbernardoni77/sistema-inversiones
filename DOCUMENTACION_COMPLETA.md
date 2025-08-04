# 📊 Documentación Completa - Aplicación de Inversiones

## 🎯 **Descripción General**

Esta aplicación es una plataforma completa de análisis de inversiones que combina análisis técnico, fundamental y de sentimiento del mercado para proporcionar recomendaciones inteligentes (comprar, mantener, vender) para diferentes activos financieros.

### **Características Principales:**
- ✅ **Análisis Técnico Avanzado**: RSI, MACD, Medias Móviles, Bandas de Bollinger, OBV, VWAP
- ✅ **Análisis de Sentimiento**: Índice de Miedo y Codicia, Análisis de Noticias
- ✅ **Datos Fundamentales**: Información de CoinGecko para criptomonedas
- ✅ **Métricas On-Chain**: Datos de Blockchair para BTC/ETH
- ✅ **Soportes y Resistencias**: Detección automática de niveles clave
- ✅ **Sistema de Aprendizaje**: Optimización automática de pesos de indicadores
- ✅ **Reportes y Auditoría**: Seguimiento completo del rendimiento
- ✅ **Interfaz Web React**: Dashboard interactivo con gráficos

---

## 🏗️ **Arquitectura del Sistema**

### **Backend (FastAPI + Python)**
```
backend/
├── main.py                 # Punto de entrada y endpoints principales
├── services/
│   ├── binance_service.py  # Conexión con Binance API
│   ├── external_data_service.py  # APIs externas (sentimiento, noticias)
│   ├── reporting_service.py      # Sistema de reportes
│   └── cache_service.py          # Sistema de caché
├── models/
│   └── __init__.py         # Modelos de base de datos
└── data/
    ├── inversiones.db      # Base de datos SQLite
    └── signals.csv         # Historial de señales
```

### **Frontend (React + TypeScript)**
```
frontend/
├── src/
│   ├── App.tsx             # Componente principal
│   ├── components/
│   │   ├── TickerCard.tsx      # Tarjeta de ticker
│   │   ├── TickerDetails.tsx   # Detalles del ticker
│   │   ├── TickerInput.tsx     # Input para agregar tickers
│   │   └── CandleChart.tsx     # Gráfico de velas
│   └── services/
│       └── api.ts          # Servicios de API
```

---

## 🔌 **Endpoints de la API**

### **1. Información Básica**
- **GET** `/` - Estado del servidor
- **GET** `/docs` - Documentación interactiva (Swagger)

### **2. Precios y Datos**
- **GET** `/binance/price/{symbol}` - Precio actual de un ticker
- **GET** `/binance/klines/{symbol}` - Datos históricos para gráficos
- **GET** `/binance/price/{symbol}?period=1d|1mo|1y|all` - Precio con variación por período

### **3. Análisis y Recomendaciones**
- **GET** `/binance/recommendation/{symbol}` - Recomendación completa con análisis
- **GET** `/binance/recommendation/{symbol}?horizonte=1h|4h|12h|24h|7d|1mes` - Recomendación por horizonte temporal

### **4. Gestión de Tickers**
- **GET** `/tickers` - Lista de tickers en seguimiento
- **POST** `/tickers/add` - Agregar ticker al seguimiento
- **DELETE** `/tickers/remove/{symbol}` - Remover ticker del seguimiento
- **GET** `/tickers/recommendations` - Recomendaciones para todos los tickers

### **5. Reportes y Auditoría**
- **GET** `/reporting/resumen` - Resumen ejecutivo del sistema
- **GET** `/reporting/detalle/{symbol}` - Análisis detallado por símbolo
- **GET** `/reporting/evolucion` - Evolución de pesos del sistema
- **POST** `/reporting/exportar` - Exportar datos en JSON/CSV

### **6. Snapshot y Batch**
- **POST** `/binance/snapshot` - Tomar foto de múltiples tickers

---

## 📊 **Indicadores Técnicos Implementados**

### **1. Indicadores de Momentum**
- **RSI (Relative Strength Index)**: Mide sobrecompra/sobreventa
- **MACD**: Divergencia de convergencia de medias móviles
- **OBV (On-Balance Volume)**: Relación volumen-precio

### **2. Medias Móviles**
- **SMA 7**: Media móvil simple de 7 períodos
- **SMA 21**: Media móvil simple de 21 períodos
- **SMA 50**: Media móvil simple de 50 períodos
- **SMA 200**: Media móvil simple de 200 períodos

### **3. Volatilidad y Volumen**
- **Bandas de Bollinger**: Bandas superior, media e inferior
- **VWAP**: Volumen Weighted Average Price

### **4. Soportes y Resistencias**
- **Detección Automática**: 3 niveles principales usando ventanas de 5, 10 y 20 períodos
- **Contexto**: Información sobre la relevancia de cada nivel
- **Leyenda Visual**: Referencia de colores debajo de los gráficos
- **Cálculo de Toques**: Número de veces que el precio ha tocado cada nivel
- **Algoritmo Mejorado**: Detección de mínimos y máximos locales con fallback a niveles globales

### **5. Métricas de Riesgo**
- **Ratio Sharpe**: Rentabilidad ajustada al riesgo
- **Correlación**: Relación con otros activos

---

## 📊 **Leyenda de Soportes y Resistencias**

### **Características de la Leyenda**
- **Ubicación**: Debajo de los gráficos de velas (dashboard y detalle)
- **Diseño**: Fondo oscuro (#1a1a1a) con bordes redondeados
- **Colores**: Verde (🟢) para soportes, Rojo (🔴) para resistencias
- **Formato**: Precios con separadores de miles (ej: $117,040.01)

### **Información Mostrada**
- **📊 Leyenda de Niveles**: Título principal
- **🟢 Soportes (Niveles de Compra)**: Lista de niveles de soporte
- **🔴 Resistencias (Niveles de Venta)**: Lista de niveles de resistencia
- **💰 Precios**: Formateados con comas para mejor legibilidad
- **🔢 Toques**: Número de veces que el precio ha tocado cada nivel
- **💡 Explicación**: Información sobre la opacidad de las líneas

### **Algoritmo de Detección**
1. **Análisis de Ventanas**: Usa ventanas de 5, 10 y 20 períodos
2. **Detección Local**: Encuentra mínimos y máximos locales
3. **Fallback Global**: Si no hay suficientes niveles, usa mínimos/máximos globales
4. **Ordenamiento**: Prioriza niveles más cercanos al precio actual
5. **Eliminación de Duplicados**: Remueve niveles muy similares

### **Cálculo de Toques**
- **Umbral**: 0.2% de diferencia para considerar un "toque"
- **Opacidad**: Los niveles más tocados se muestran más opacos
- **Relevancia**: Ayuda a identificar niveles más importantes

---

## 🧠 **Sistema de Aprendizaje Automático**

### **Optimización de Pesos**
El sistema ajusta automáticamente la importancia de cada indicador basándose en:
- **Precisión histórica**: Qué indicadores han sido más acertados
- **Condiciones de mercado**: Ajustes según volatilidad y tendencia
- **Horizonte temporal**: Pesos diferentes para diferentes timeframes

### **Proceso de Optimización**
1. **Evaluación**: Analiza recomendaciones pasadas vs resultados reales
2. **Ajuste**: Modifica pesos de indicadores para mejorar precisión
3. **Validación**: Prueba los nuevos pesos con datos históricos
4. **Implementación**: Aplica los pesos optimizados

---

## 📈 **Análisis de Sentimiento**

### **Índice de Miedo y Codicia**
- **Fuente**: alternative.me
- **Escala**: 0-100 (Extremo Miedo a Codicia Extrema)
- **Impacto**: Modera recomendaciones en extremos

### **Análisis de Noticias**
- **Fuente**: Cointelegraph (scraping)
- **Proceso**: Análisis de palabras clave en titulares
- **Palabras Positivas**: adopción, inversión, récord, máximo, etc.
- **Palabras Negativas**: hackeo, caída, prohibición, regulación, etc.

---

## 🗄️ **Base de Datos**

### **Tabla: `tickers`**
```sql
- id: INTEGER PRIMARY KEY
- symbol: TEXT UNIQUE
- added_date: DATETIME
- last_updated: DATETIME
```

### **Tabla: `signals`**
```sql
- id: INTEGER PRIMARY KEY
- symbol: TEXT
- timestamp: DATETIME
- price: REAL
- rsi: REAL
- sma_7: REAL
- sma_21: REAL
- sma_50: REAL
- sma_200: REAL
- macd: REAL
- macd_signal: REAL
- macd_hist: REAL
- bb_upper: REAL
- bb_mid: REAL
- bb_lower: REAL
- obv: REAL
- vwap: REAL
- soportes: TEXT (JSON)
- resistencias: TEXT (JSON)
- contexto_sr: TEXT (JSON)
- recomendacion: TEXT
- resultado_real_1h: TEXT
- resultado_real_4h: TEXT
- resultado_real_12h: TEXT
- resultado_real_24h: TEXT
- resultado_real_7d: TEXT
- resultado_real_1mes: TEXT
```

### **Tabla: `optimization_history`**
```sql
- id: INTEGER PRIMARY KEY
- fecha: DATETIME
- tipo_optimizacion: TEXT
- descripcion: TEXT
- pesos_anteriores: TEXT (JSON)
- pesos_nuevos: TEXT (JSON)
- parametros_anteriores: TEXT (JSON)
- parametros_nuevos: TEXT (JSON)
- motivo_ajuste: TEXT
- metricas_resultado: TEXT (JSON)
- usuario: TEXT
```

### **Tabla: `recommendation_performance`**
```sql
- id: INTEGER PRIMARY KEY
- fecha_recomendacion: DATETIME
- fecha_verificacion: DATETIME
- simbolo: TEXT
- recomendacion: TEXT
- precio_recomendacion: REAL
- precio_verificacion: REAL
- resultado: TEXT
- precision: REAL
- pesos_utilizados: TEXT (JSON)
- indicadores_utilizados: TEXT (JSON)
- contexto_mercado: TEXT (JSON)
```

---

## 🎨 **Interfaz de Usuario**

### **Dashboard Principal**
- **Lista de Tickers**: Muestra símbolo, precio, cambio y recomendación
- **Gráfico Principal**: Gráfico de velas del ticker seleccionado
- **Leyenda de Niveles**: Referencia visual de soportes y resistencias
- **Selector de Horizonte**: 1h, 4h, 12h, 24h, 7d, 1mes
- **Controles**: Agregar/remover tickers, cambiar períodos

### **Página de Detalle**
- **Información Completa**: Todos los indicadores y análisis
- **Gráfico Interactivo**: Con soportes, resistencias e indicadores
- **Leyenda de Niveles**: Referencia visual de soportes y resistencias
- **Análisis de Sentimiento**: Fear & Greed, noticias relevantes
- **Datos Fundamentales**: Market cap, volumen, supply
- **Métricas On-Chain**: Solo para BTC/ETH

### **Componentes Principales**
- **TickerCard**: Tarjeta compacta con información esencial
- **TickerDetails**: Modal/página con análisis completo
- **CandleChart**: Gráfico de velas con ApexCharts y leyenda de soportes/resistencias
- **TickerInput**: Input para agregar nuevos tickers

---

## ⚙️ **Configuración y Despliegue**

### **Requisitos del Sistema**
- **Python**: 3.8+
- **Node.js**: 16+
- **npm**: 8+

### **Dependencias Backend**
```bash
pip install -r backend/requirements.txt
```

### **Dependencias Frontend**
```bash
cd frontend
npm install
```

### **Variables de Entorno**
Crear archivo `.env` en la carpeta `backend/`:
```env
NEWSAPI_KEY=tu_api_key_aqui
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_SECRET_KEY=tu_secret_key_aqui
```

### **Iniciar el Sistema**
1. **Backend**:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm start
   ```

---

## 📊 **Ejemplos de Uso**

### **1. Obtener Recomendación Completa**
```bash
curl "http://localhost:8000/binance/recommendation/BTCUSDT?horizonte=24h"
```

**Respuesta:**
```json
{
  "recomendacion": "Comprar",
  "detalle": {
    "motivo": ["RSI bajo (<30)", "MACD alcista"],
    "indicadores": {
      "rsi": 28.5,
      "sma_7": 42000.1,
      "sma_21": 41800.2,
      "macd": 150.5,
      "sharpe_ratio": 1.23
    },
    "soportes": [41500, 41000, 40500],
    "resistencias": [42500, 43000, 43500],
    "fundamental": {
      "nombre": "Bitcoin",
      "market_cap": 850000000000,
      "volumen_24h": 25000000000
    },
    "sentimiento": {
      "fear_and_greed": {
        "value": "45",
        "value_classification": "Fear"
      }
    },
    "noticias": [
      {
        "titulo": "Bitcoin adopción institucional crece",
        "sentimiento": "positivo"
      }
    ]
  }
}
```

**Leyenda Visual Generada:**
```
📊 Leyenda de Niveles

🟢 Soportes (Niveles de Compra)
• $41,500
• $41,000
• $40,500

🔴 Resistencias (Niveles de Venta)
• $42,500
• $43,000
• $43,500

💡 Los niveles más intensos (más opacos) han sido tocados más veces por el precio
```

### **2. Agregar Ticker al Seguimiento**
```bash
curl -X POST "http://localhost:8000/tickers/add" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "ETHUSDT"}'
```

### **3. Obtener Reporte Ejecutivo**
```bash
curl "http://localhost:8000/reporting/resumen"
```

---

## 🔧 **Mantenimiento y Monitoreo**

### **Logs del Sistema**
- **Backend**: Logs en consola durante desarrollo
- **Frontend**: Logs en consola del navegador
- **Base de Datos**: Archivo SQLite en `backend/data/`

### **Backup de Datos**
- **Base de Datos**: Copiar `backend/data/inversiones.db`
- **Señales**: Copiar `backend/data/signals.csv`
- **Configuración**: Copiar archivos `.env` y de configuración

### **Monitoreo de Rendimiento**
- **Tiempo de Respuesta**: Endpoints principales < 5 segundos
- **Precisión del Sistema**: Seguimiento en `/reporting/resumen`
- **Uso de Recursos**: Monitorear uso de CPU y memoria

---

## 🚀 **Roadmap y Mejoras Futuras**

### **Fase 1 - Completado ✅**
- ✅ Análisis técnico básico
- ✅ Interfaz web funcional
- ✅ Sistema de recomendaciones
- ✅ Integración con APIs externas
- ✅ Leyenda de soportes y resistencias
- ✅ Algoritmo mejorado de detección de niveles

### **Fase 2 - En Desarrollo 🔄**
- 🔄 Machine Learning avanzado
- 🔄 Alertas y notificaciones
- 🔄 Portafolio tracking
- 🔄 Backtesting automático

### **Fase 3 - Planificado 📋**
- 📋 Análisis de correlaciones entre activos
- 📋 Integración con más exchanges
- 📋 Análisis de opciones y derivados
- 📋 API pública para terceros

---

## 🆘 **Solución de Problemas**

### **Problemas Comunes**

#### **1. Error de Conexión con Binance**
```bash
# Verificar conectividad
curl "https://api.binance.com/api/v3/ping"
```

#### **2. Ticker No Encontrado**
- Verificar que el símbolo existe en Binance
- Usar formato correcto: `BTCUSDT`, `ETHUSDT`, etc.

#### **3. Error de Base de Datos**
```bash
# Recrear tablas
cd backend
python create_tables.py
```

#### **4. Problemas de CORS en Frontend**
- Verificar que el backend esté en `http://localhost:8000`
- Revisar configuración en `frontend/src/services/api.ts`

#### **5. Leyenda de Soportes y Resistencias No Aparece**
- Verificar que el backend devuelva datos en `detalle.soportes` y `detalle.resistencias`
- Ejecutar `python debug_soportes.py` para verificar datos
- Revisar consola del navegador (F12) para errores JavaScript
- Verificar que el ticker tenga datos históricos suficientes

### **Comandos de Diagnóstico**
```bash
# Verificar estado del backend
curl "http://localhost:8000/"

# Verificar dependencias
pip list | grep -E "(fastapi|uvicorn|pandas)"

# Verificar logs
tail -f backend/logs/app.log
```

### **Scripts de Prueba Especializados**
```bash
# Probar soportes y resistencias
python test_leyenda_soportes.py

# Debug detallado de soportes y resistencias
python debug_soportes.py

# Verificación completa de leyenda
python verificar_leyenda_completa.py

# Probar endpoints de reporting
python test_reporting.py

# Optimizar rendimiento del backend
python optimizar_backend.py

# Diagnosticar problemas con tickers específicos
python diagnostico_ticker.py
```

---

## 📞 **Soporte y Contacto**

### **Recursos Adicionales**
- **Documentación API**: `http://localhost:8000/docs`
- **Repositorio**: [URL del repositorio]
- **Issues**: [URL de issues]

### **Comunidad**
- **Discord**: [Canal de Discord]
- **Telegram**: [Grupo de Telegram]
- **Email**: [Email de soporte]

---

## 📄 **Licencia**

Este proyecto está bajo la licencia [MIT License]. Ver archivo `LICENSE` para más detalles.

---

*Última actualización: Julio 2025*
*Versión: 1.0.0* 