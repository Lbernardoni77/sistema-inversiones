# 🚀 Guía de Despliegue - Sistema de Inversiones

## 🌐 Despliegue en Render (Gratis)

### **Paso 1: Preparar el Repositorio**

1. **Subir a GitHub**:
   ```bash
   git add .
   git commit -m "Preparado para despliegue"
   git push origin main
   ```

2. **Verificar archivos necesarios**:
   - ✅ `requirements.txt`
   - ✅ `render.yaml`
   - ✅ `backend/start_production.py`

### **Paso 2: Desplegar en Render**

1. **Ir a [render.com](https://render.com)**
2. **Crear cuenta gratuita**
3. **Conectar repositorio de GitHub**
4. **Crear nuevo Web Service**
5. **Configurar**:
   - **Name**: `inversiones-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### **Paso 3: Variables de Entorno (Opcional)**

En Render, agregar variables de entorno:
- `DATABASE_URL`: URL de base de datos (si usas PostgreSQL)
- `API_KEYS`: Claves de APIs externas

### **Paso 4: Desplegar**

1. **Click en "Create Web Service"**
2. **Esperar el build** (5-10 minutos)
3. **¡Listo!** Tu API estará disponible en: `https://tu-app.onrender.com`

## 📱 Acceso desde Cualquier Lugar

### **Endpoints Disponibles**:

```
🌐 Base URL: https://tu-app.onrender.com

📊 Estado del sistema:
GET /learning/status

🔧 Optimización manual:
POST /learning/optimize-now

📈 Recomendaciones:
GET /binance/recommendation/{symbol}

📋 Lista de tickers:
GET /tickers/list

📊 Reportes:
GET /reporting/resumen
GET /reporting/detalle/{simbolo}
```

### **Ejemplo de Uso**:

```bash
# Ver estado del sistema
curl https://tu-app.onrender.com/learning/status

# Obtener recomendación para BTC
curl https://tu-app.onrender.com/binance/recommendation/BTCUSDT

# Listar tickers
curl https://tu-app.onrender.com/tickers/list
```

## 🔧 Monitoreo Remoto

### **Script de Monitoreo Remoto**:

```python
import requests

def monitorear_remoto():
    base_url = "https://tu-app.onrender.com"
    
    # Estado del sistema
    response = requests.get(f"{base_url}/learning/status")
    if response.status_code == 200:
        status = response.json()
        print(f"Estado: {status['status']}")
        print(f"Tickers: {status['tickers_optimizados']}")
        print(f"Rendimiento: {status['promedio_rendimiento']}")
    
    # Recomendación BTC
    response = requests.get(f"{base_url}/binance/recommendation/BTCUSDT")
    if response.status_code == 200:
        rec = response.json()
        print(f"BTC: {rec['recomendacion']} - {rec['puntaje_total']}")

# Ejecutar
monitorear_remoto()
```

## 📱 Aplicación Móvil

### **Flutter/Dart**:
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class InversionesAPI {
  static const String baseUrl = 'https://tu-app.onrender.com';
  
  static Future<Map<String, dynamic>> getStatus() async {
    final response = await http.get(Uri.parse('$baseUrl/learning/status'));
    return json.decode(response.body);
  }
  
  static Future<Map<String, dynamic>> getRecommendation(String symbol) async {
    final response = await http.get(
      Uri.parse('$baseUrl/binance/recommendation/$symbol')
    );
    return json.decode(response.body);
  }
}
```

### **React Native**:
```javascript
const API_BASE = 'https://tu-app.onrender.com';

const getStatus = async () => {
  const response = await fetch(`${API_BASE}/learning/status`);
  return response.json();
};

const getRecommendation = async (symbol) => {
  const response = await fetch(`${API_BASE}/binance/recommendation/${symbol}`);
  return response.json();
};
```

## 🔒 Seguridad

### **Recomendaciones**:

1. **Rate Limiting**: Implementar límites de requests
2. **API Keys**: Para endpoints sensibles
3. **HTTPS**: Render lo proporciona automáticamente
4. **CORS**: Configurado para permitir acceso desde cualquier origen

### **Variables de Entorno Sensibles**:
```bash
# En Render Dashboard
BINANCE_API_KEY=tu_api_key
BINANCE_SECRET=tu_secret
DATABASE_URL=tu_database_url
```

## 📊 Monitoreo y Logs

### **Render Dashboard**:
- **Logs**: Ver logs en tiempo real
- **Metrics**: CPU, memoria, requests
- **Deployments**: Historial de despliegues

### **Health Check**:
```bash
# Verificar que el sistema esté funcionando
curl https://tu-app.onrender.com/learning/status
```

## 🚀 Actualizaciones

### **Para actualizar**:
1. **Hacer cambios en código local**
2. **Commit y push a GitHub**
3. **Render detecta automáticamente y redeploya**

### **Rollback**:
- **Render Dashboard** → **Deployments** → **Revert**

## 💡 Tips

1. **Free Tier**: 750 horas/mes gratis
2. **Sleep Mode**: Se duerme después de 15 min sin uso
3. **Wake Up**: Primera request puede tardar 30 segundos
4. **Database**: Considerar PostgreSQL para producción

## 🆘 Troubleshooting

### **Problemas Comunes**:

1. **Build Fails**: Verificar `requirements.txt`
2. **Import Errors**: Verificar estructura de archivos
3. **Database Issues**: Verificar conexiones
4. **Timeout**: Aumentar timeout en Render

### **Logs Útiles**:
```bash
# Ver logs en Render
# Dashboard → Tu App → Logs
```

---

**¡Tu sistema estará disponible 24/7 desde cualquier lugar! 🌍** 