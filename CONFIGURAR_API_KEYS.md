# 🔑 Configuración de API Keys en Render

## 📋 Variables de Entorno a Configurar

Para que las nuevas fuentes de klines funcionen correctamente, necesitas configurar las siguientes variables de entorno en Render:

### 🔧 Pasos para Configurar:

1. **Ve a tu proyecto en Render**
2. **Navega a la pestaña "Environment"**
3. **Agrega las siguientes variables:**

```
ALPHA_VANTAGE_API_KEY=OQKLL0SS21H10SCW
POLYGON_API_KEY=3LpLDGUpYcWTrwuGFBZ0ntoFN72Lmkmx
FINNHUB_API_KEY=d2agh3hr01qgk9ueof30d2agh3hr01qgk9ueof3g
```

### 📊 Estado Actual de las APIs:

#### ✅ **Funcionando:**
- **CoinMarketCap**: Precios reales para todos los símbolos
- **Alpha Vantage**: Klines para BTCUSDT y ETHUSDT
- **Polygon**: Klines para BTCUSDT y ETHUSDT

#### ⚠️ **Limitaciones:**
- **Alpha Vantage**: No reconoce algunos símbolos como ADAUSDT
- **Finnhub**: Error 403 para algunos símbolos (puede ser limitación de plan gratuito)

### 🎯 **Beneficios de la Configuración:**

1. **Múltiples fuentes de klines**: Ya no dependeremos solo de Binance/CoinGecko
2. **Mayor confiabilidad**: Si una fuente falla, otras pueden funcionar
3. **Datos reales**: Los gráficos de velas mostrarán datos reales
4. **Mejor rendimiento**: Menos errores 451/429

### 🔄 **Después de Configurar:**

1. **Render se desplegará automáticamente** con las nuevas variables
2. **El sistema probará las nuevas fuentes** en el próximo request
3. **Los gráficos de velas deberían funcionar** para la mayoría de símbolos

### 📈 **Monitoreo:**

Puedes verificar que las nuevas fuentes estén funcionando revisando los logs de Render. Deberías ver mensajes como:
- `✅ Klines obtenidos de ALPHA_VANTAGE para BTCUSDT`
- `✅ Klines obtenidos de POLYGON para ETHUSDT`

### 🚨 **Nota Importante:**

Las API keys gratuitas tienen límites de uso:
- **Alpha Vantage**: 500 requests/día
- **Polygon**: 5 requests/minuto
- **Finnhub**: 60 requests/minuto

El sistema está diseñado para manejar estos límites automáticamente.
