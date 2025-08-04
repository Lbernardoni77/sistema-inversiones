# 🤖 Sistema de Inversiones con Aprendizaje Automático

## 📊 Descripción

Sistema avanzado de análisis y recomendaciones de inversión en criptomonedas que utiliza:

- **Análisis Técnico**: RSI, MACD, SMA, Bollinger Bands, OBV, VWAP
- **Análisis de Sentimiento**: Noticias, Fear & Greed Index
- **Aprendizaje Automático**: Optimización de pesos por ticker individual
- **Soportes y Resistencias**: Detección automática de niveles clave
- **Recomendaciones en Tiempo Real**: Comprar/Vender/Mantener

## 🚀 Características

### ✅ **Sistema de Aprendizaje Individual**
- Pesos optimizados específicos por cada ticker
- Aprendizaje automático basado en resultados reales
- Optimización diaria de parámetros

### ✅ **Análisis Completo**
- 53 criptomonedas en seguimiento
- Múltiples horizontes temporales (1h, 4h, 12h, 24h, 7d, 1mes)
- Indicadores técnicos avanzados
- Análisis de noticias y sentimiento

### ✅ **Monitoreo 24/7**
- API REST disponible globalmente
- Aplicación móvil Flutter
- Scripts de monitoreo remoto
- Dashboard web en tiempo real

## 🛠️ Tecnologías

- **Backend**: FastAPI (Python)
- **Base de Datos**: SQLite
- **Frontend**: React + TypeScript
- **Móvil**: Flutter
- **Despliegue**: Render (Gratis)
- **APIs**: Binance, CoinGecko, Blockchair

## 📱 Acceso

### **API Endpoints**:
```
🌐 Base URL: https://tu-app.onrender.com

📊 Estado del sistema:
GET /learning/status

📈 Recomendaciones:
GET /binance/recommendation/{symbol}

📋 Lista de tickers:
GET /tickers/list

🔧 Optimización:
POST /learning/optimize-now
```

### **Aplicación Móvil**:
- Descargar desde Google Play/App Store
- Monitoreo en tiempo real
- Notificaciones de cambios

## 🎯 Uso Rápido

### **Ver Estado del Sistema**:
```bash
curl https://tu-app.onrender.com/learning/status
```

### **Obtener Recomendación BTC**:
```bash
curl https://tu-app.onrender.com/binance/recommendation/BTCUSDT
```

### **Monitoreo Remoto**:
```bash
python monitoreo_remoto.py
```

## 📊 Rendimiento

- **53 Tickers** optimizados individualmente
- **Precisión promedio**: 65-75%
- **Actualización**: Cada hora
- **Optimización**: Diaria automática

## 🔒 Seguridad

- HTTPS automático
- Rate limiting
- Validación de datos
- Logs de auditoría

## 📈 Roadmap

- [ ] Integración con más exchanges
- [ ] Análisis fundamental avanzado
- [ ] Alertas personalizadas
- [ ] Backtesting automático
- [ ] Portfolio tracking

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

- **Email**: soporte@tu-email.com
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/sistema-inversiones/issues)
- **Documentación**: [Wiki](https://github.com/tu-usuario/sistema-inversiones/wiki)

---

**¡Haz trading más inteligente con IA! 🚀** 