from fastapi import FastAPI, Query, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.binance_service import BinanceService
from services.multi_source_service import MultiSourceService
from services.external_data_service import (
    get_fear_and_greed_index,
    get_crypto_news,
    get_fundamental_data,
    get_onchain_data,
    sharpe_ratio,
    correlation,
    analizar_sentimiento_noticias
)
from typing import List
# NOTA: Si ves errores de importación, ejecuta 'pip install -r requirements.txt' para instalar sqlalchemy y apscheduler.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Ticker, Signal
import os
from apscheduler.schedulers.background import BackgroundScheduler
import json
from services.learning_service import optimize_weights
from services.reporting_service import ReportingService
from datetime import datetime
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend local
        "https://sistema-inversiones-frontend.onrender.com",  # Frontend en Render
        "https://sistema-inversiones-frontend.onrender.com/",  # Con slash
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de la base de datos SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'inversiones.db')
engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Configurar el scheduler para jobs automáticos
scheduler = BackgroundScheduler()

# Instancias de servicios
multi_source_service = MultiSourceService()
binance_service = BinanceService()

def optimize_weights_job():
    """
    Job programado para optimizar los pesos de los indicadores automáticamente
    """
    try:
        from services.learning_service import optimize_weights
        print("🤖 Iniciando optimización automática de pesos...")
        
        # Optimizar para diferentes horizontes
        horizontes = ['resultado_real_1h', 'resultado_real_4h', 'resultado_real_24h', 'resultado_real_7d']
        for horizonte in horizontes:
            try:
                optimize_weights(horizonte=horizonte)
                print(f"✅ Optimización completada para {horizonte}")
            except Exception as e:
                print(f"❌ Error optimizando {horizonte}: {e}")
        
        print("🎯 Optimización automática completada")
    except Exception as e:
        print(f"❌ Error en job de optimización: {e}")

def save_signals_job():
    session = SessionLocal()
    tickers = session.query(Ticker).all()
    for t in tickers:
        try:
            rec = binance_service.get_recommendation(t.symbol)
            if "error" in rec:
                continue
            
            # Extraer indicadores
            indicadores = rec.get("indicators", {})
            
            signal = Signal(
                ticker_id=t.id,
                price=rec.get("price"),
                rsi=indicadores.get("rsi"),
                sma_7=indicadores.get("sma_20"),  # Usar sma_20 como aproximación
                sma_21=indicadores.get("sma_20"),  # Usar sma_20 como aproximación
                sma_50=indicadores.get("sma_50"),
                sma_200=indicadores.get("sma_50"),  # Usar sma_50 como aproximación
                macd=indicadores.get("macd"),
                macd_signal=indicadores.get("macd_signal"),
                macd_hist=indicadores.get("macd", 0) - indicadores.get("macd_signal", 0),  # Calcular histograma
                bb_upper=indicadores.get("bb_upper"),
                bb_mid=indicadores.get("bb_middle"),
                bb_lower=indicadores.get("bb_lower"),
                obv=0,  # No disponible en la nueva implementación
                vwap=0,  # No disponible en la nueva implementación
                sharpe_ratio=0,  # No disponible en la nueva implementación
                recomendacion=rec.get("recommendation"),
                soportes=json.dumps([]),  # No disponible en la nueva implementación
                resistencias=json.dumps([]),  # No disponible en la nueva implementación
                contexto_sr=json.dumps({}),  # No disponible en la nueva implementación
                timestamp=datetime.now()
            )
            session.add(signal)
            print(f"✅ Señal guardada para {t.symbol}")
        except Exception as e:
            print(f"❌ Error guardando señal para {t.symbol}: {e}")
            continue
    
    session.commit()
    session.close()
    print(f"💾 Job save_signals_job completado - {len(tickers)} tickers procesados")

def update_signals_resultado_real():
    """
    Recorre todas las señales (Signal) y calcula automáticamente los campos resultado_real_1h, resultado_real_4h, resultado_real_12h, resultado_real_24h, resultado_real_7d, resultado_real_1mes
    según el horizonte correspondiente, si ya pasó el tiempo desde la señal.
    Guarda:
      - 'subio' si el precio subió >2%
      - 'bajo' si cayó >2%
      - 'sin cambio' si varió menos de ±2%
    """
    from datetime import datetime, timedelta
    session = SessionLocal()
    now = datetime.utcnow()
    signals = session.query(Signal).all()
    horizontes = [
        ("resultado_real_1h", timedelta(hours=1)),
        ("resultado_real_4h", timedelta(hours=4)),
        ("resultado_real_12h", timedelta(hours=12)),
        ("resultado_real_24h", timedelta(hours=24)),
        ("resultado_real_7d", timedelta(days=7)),
        ("resultado_real_1mes", timedelta(days=30)),
    ]
    for s in signals:
        for campo, delta in horizontes:
            if getattr(s, campo) is not None:
                continue  # Ya calculado
            if (now - s.timestamp) < delta:
                continue  # Aún no pasó el horizonte
            price_data = binance_service.get_multi_source_price(s.ticker.symbol)
            if not price_data or 'price' not in price_data:
                continue
            price_now = float(price_data['price'])
            change = (price_now - s.price) / s.price * 100 if s.price else 0
            if change > 2:
                setattr(s, campo, 'subio')
            elif change < -2:
                setattr(s, campo, 'bajo')
            else:
                setattr(s, campo, 'sin cambio')
    session.commit()
    session.close()

def optimize_all_horizons():
    """
    Ejecuta la optimización de pesos para todos los horizontes de resultado real.
    """
    horizontes = [
        'resultado_real_1h',
        'resultado_real_4h',
        'resultado_real_12h',
        'resultado_real_24h',
        'resultado_real_7d',
        'resultado_real_1mes',
    ]
    for h in horizontes:
        optimize_weights(horizonte=h)

# Programar jobs automáticos
scheduler.add_job(save_signals_job, 'interval', hours=1, id='save_signals')
scheduler.add_job(update_signals_resultado_real, 'interval', hours=1, id='update_results')
scheduler.add_job(optimize_weights_job, 'cron', hour=2, minute=0, id='optimize_weights')  # Cada día a las 2 AM

# Iniciar el scheduler
scheduler.start()
print("⏰ Scheduler iniciado - Jobs programados:")
print("   - Guardar señales: cada hora")
print("   - Actualizar resultados: cada hora") 
print("   - Optimizar pesos: cada día a las 2 AM")

scheduler.add_job(optimize_all_horizons, 'interval', days=1)

@app.get("/")
def read_root():
    return {"mensaje": "¡Backend de inversiones funcionando!"}

@app.get("/healthz")
def health_check():
    """Endpoint para health check de Render"""
    return {"status": "healthy", "message": "Sistema de Inversiones funcionando correctamente"}

@app.get("/binance/price/{symbol}")
async def get_binance_price(symbol: str, period: str = "1d"):
    """Obtener precio actual y porcentaje de cambio calculado"""
    try:
        # Obtener precio actual
        price_data = binance_service.get_binance_price(symbol)
        if not price_data:
            raise HTTPException(status_code=404, detail=f"No se pudo obtener precio para {symbol}")
        
        # Calcular porcentaje de cambio usando nuestro método
        percentage_change = binance_service.calculate_percentage_change(symbol, period)
        
        return {
            "symbol": symbol,
            "price": price_data['price'],
            "change_24h": percentage_change,  # Usar nuestro cálculo
            "timestamp": price_data.get('timestamp', datetime.now().isoformat()),
            "period": period
        }
    except Exception as e:
        logger.error(f"Error obteniendo precio para {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/binance/recommendation/{symbol}")
def binance_recommendation(symbol: str, horizonte: str = Query("24h", enum=["1h", "4h", "12h", "24h", "7d", "1mes"])):
    # Indicadores técnicos y de volumen
    rec = binance_service.get_recommendation(symbol)
    recomendacion_tecnica = rec.get("recommendation", "NEUTRAL")
    # Índice de miedo y codicia
    fear_greed = get_fear_and_greed_index()
    fg_value = None
    try:
        if fear_greed and "value" in fear_greed:
            fg_value = int(fear_greed["value"])
    except Exception:
        fg_value = None
    # Noticias
    news = get_crypto_news()[:5]  # Solo las 5 más recientes
    sentimiento_noticias = analizar_sentimiento_noticias(news)
    # Fundamental y on-chain (simulado/demo)
    fundamental = get_fundamental_data(symbol)
    onchain = get_onchain_data(symbol)
    # Ratio Sharpe (usando retornos de precios)
    klines = binance_service.get_multi_source_klines(symbol)
    if klines and len(klines) > 1:
        closes = [float(k[4]) for k in klines]  # Precio de cierre
        returns = [(closes[i] - closes[i-1])/closes[i-1] for i in range(1, len(closes))]
        sharpe = sharpe_ratio(returns)
    else:
        sharpe = None
    # Ajuste de recomendación según sentimiento de noticias
    score = sentimiento_noticias["score"]
    recomendacion = recomendacion_tecnica
    ajuste_noticias = "Sin ajuste"
    if score > 0:
        if recomendacion == "NEUTRAL":
            recomendacion = "COMPRAR"
            ajuste_noticias = "Noticias positivas reforzaron señal de compra"
        elif recomendacion == "VENDER":
            recomendacion = "NEUTRAL"
            ajuste_noticias = "Noticias positivas moderaron señal de venta"
    elif score < 0:
        if recomendacion == "NEUTRAL":
            recomendacion = "VENDER"
            ajuste_noticias = "Noticias negativas reforzaron señal de venta"
        elif recomendacion == "COMPRAR":
            recomendacion = "NEUTRAL"
            ajuste_noticias = "Noticias negativas moderaron señal de compra"
    # Ajuste por Fear & Greed
    ajuste_fg = "Sin ajuste"
    if fg_value is not None:
        if fg_value > 75 and recomendacion == "COMPRAR":
            recomendacion = "NEUTRAL"
            ajuste_fg = "Fear & Greed alto (>75) moderó señal de compra"
        elif fg_value < 25 and recomendacion == "VENDER":
            recomendacion = "NEUTRAL"
            ajuste_fg = "Fear & Greed bajo (<25) moderó señal de venta"
    # Resumen de ponderación
    resumen_ponderacion = {
        "recomendacion_tecnica": recomendacion_tecnica,
        "peso_indicadores_tecnicos": "70% (RSI, SMA, MACD, Bollinger)",
        "ajuste_noticias": ajuste_noticias,
        "peso_noticias": "20% (análisis de sentimiento en titulares)",
        "ajuste_fear_greed": ajuste_fg,
        "peso_fear_greed": "10% (precaución en extremos de sentimiento)",
        "recomendacion_final": recomendacion,
        "explicacion": f"La recomendación se basa principalmente en indicadores técnicos ({recomendacion_tecnica}), ajustada por sentimiento de noticias y precaución ante extremos de mercado."
    }
    # Respuesta principal y detalle
    indicadores = rec.get("indicators", {})
    detalle = {
        "motivo": [f"Confidence: {rec.get('confidence', 0)}%"],
        "indicadores": {
            "rsi": indicadores.get("rsi"),
            "sma_7": indicadores.get("sma_20"),  # Usar sma_20 como aproximación
            "sma_21": indicadores.get("sma_20"),  # Usar sma_20 como aproximación
            "sma_50": indicadores.get("sma_50"),
            "sma_200": indicadores.get("sma_50"),  # Usar sma_50 como aproximación
            "macd": indicadores.get("macd"),
            "macd_signal": indicadores.get("macd_signal"),
            "macd_hist": indicadores.get("macd", 0) - indicadores.get("macd_signal", 0),  # Calcular histograma
            "bb_upper": indicadores.get("bb_upper"),
            "bb_mid": indicadores.get("bb_middle"),
            "bb_lower": indicadores.get("bb_lower"),
            "obv": 0,  # No disponible en la nueva implementación
            "vwap": 0,  # No disponible en la nueva implementación
            "sharpe_ratio": sharpe
        },
        "soportes": [],  # No disponible en la nueva implementación
        "resistencias": [],  # No disponible en la nueva implementación
        "fundamental": fundamental,
        "onchain": onchain,
        "sentimiento": {"fear_and_greed": fear_greed, "noticias": sentimiento_noticias},
        "noticias": news,
        "resumen_ponderacion": resumen_ponderacion
    }
    return {"recomendacion": recomendacion, "horizonte": horizonte, "detalle": detalle}

@app.post("/binance/snapshot")
def binance_snapshot(tickers: List[str] = Body(..., embed=True)):
    resultados = []
    for symbol in tickers:
        rec = binance_service.get_recommendation(symbol)
        if "error" in rec:
            resultados.append({"symbol": symbol, "error": rec["error"]})
            continue
        # Guardar en CSV
        indicadores = {
            "rsi": rec.get("rsi"),
            "sma_7": rec.get("sma_7"),
            "sma_21": rec.get("sma_21"),
            "sma_50": rec.get("sma_50"),
            "sma_200": rec.get("sma_200"),
            "macd": rec.get("macd"),
            "macd_signal": rec.get("macd_signal"),
            "macd_hist": rec.get("macd_hist"),
            "bb_upper": rec.get("bb_upper"),
            "bb_mid": rec.get("bb_mid"),
            "bb_lower": rec.get("bb_lower"),
            "obv": rec.get("obv"),
            "vwap": rec.get("vwap")
        }
        # log_signal(symbol, rec.get("price"), indicadores, rec.get("recomendacion")) # This line was removed as per the new_code
        resultados.append({"symbol": symbol, "recomendacion": rec.get("recomendacion"), "indicadores": indicadores})
    return {"resultados": resultados}

@app.get("/binance/klines/{symbol}")
def binance_klines(symbol: str, interval: str = Query("1d"), limit: int = Query(30)):
    return binance_service.get_multi_source_klines(symbol, interval, limit)

@app.get("/charts/candlestick/{symbol}")
def generate_candlestick_chart(
    symbol: str, 
    interval: str = Query("1h"), 
    limit: int = Query(100),
    show_indicators: bool = Query(True),
    show_support_resistance: bool = Query(True),
    width: int = Query(1200),
    height: int = Query(600)
):
    """Genera un gráfico de velas con los datos obtenidos"""
    try:
        from services.chart_generator import ChartGenerator
        
        # Obtener klines
        klines = binance_service.get_multi_source_klines(symbol, interval, limit)
        
        if not klines or len(klines) < 2:
            return {
                "error": "No se pudieron obtener datos suficientes para generar el gráfico",
                "symbol": symbol,
                "interval": interval
            }
        
        # Generar gráfico
        chart_generator = ChartGenerator()
        result = chart_generator.generate_candlestick_chart(
            klines=klines,
            symbol=symbol,
            interval=interval,
            show_indicators=show_indicators,
            show_support_resistance=show_support_resistance,
            width=width,
            height=height
        )
        
        return result
        
    except Exception as e:
        return {
            "error": f"Error generando gráfico: {str(e)}",
            "symbol": symbol,
            "interval": interval
        }

@app.get("/charts/price/{symbol}")
def generate_price_chart(
    symbol: str,
    period: str = Query("1d"),
    width: int = Query(800),
    height: int = Query(400)
):
    """Genera un gráfico simple de precios"""
    try:
        from services.chart_generator import ChartGenerator
        from datetime import datetime, timedelta
        
        # Obtener datos de precio
        price_data = binance_service.get_multi_source_price(symbol)
        
        if not price_data or "price" not in price_data:
            return {
                "error": "No se pudo obtener el precio para generar el gráfico",
                "symbol": symbol
            }
        
        # Simular datos históricos (en un sistema real, obtendrías esto de una base de datos)
        current_price = price_data["price"]
        current_time = datetime.now()
        
        # Crear datos simulados para demostración
        prices = []
        for i in range(24):  # Últimas 24 horas
            time = current_time - timedelta(hours=23-i)
            # Simular variación de precio
            variation = (i - 12) * 0.01  # Variación del 1%
            price = current_price * (1 + variation)
            prices.append((time, price))
        
        # Generar gráfico
        chart_generator = ChartGenerator()
        result = chart_generator.generate_price_chart(
            prices=prices,
            symbol=symbol,
            width=width,
            height=height
        )
        
        return result
        
    except Exception as e:
        return {
            "error": f"Error generando gráfico de precios: {str(e)}",
            "symbol": symbol
        }

@app.post("/tickers/add")
def add_ticker(symbol: str):
    session = SessionLocal()
    symbol = symbol.upper()
    exists = session.query(Ticker).filter_by(symbol=symbol).first()
    if exists:
        session.close()
        return {"ok": False, "msg": "Ya está en seguimiento"}
    t = Ticker(symbol=symbol)
    session.add(t)
    session.commit()
    session.close()
    return {"ok": True, "msg": f"Ticker {symbol} agregado"}

@app.post("/tickers/remove")
def remove_ticker(symbol: str):
    session = SessionLocal()
    symbol = symbol.upper()
    t = session.query(Ticker).filter_by(symbol=symbol).first()
    if not t:
        session.close()
        return {"ok": False, "msg": "No estaba en seguimiento"}
    session.delete(t)
    session.commit()
    session.close()
    return {"ok": True, "msg": f"Ticker {symbol} eliminado"}

@app.get("/tickers/list")
def list_tickers():
    session = SessionLocal()
    tickers = [t.symbol for t in session.query(Ticker).all()]
    session.close()
    return {"tickers": tickers}

@app.get("/tickers/recommendations")
def get_tickers_recommendations(horizonte: str = Query("24h", enum=["1h", "4h", "12h", "24h", "7d", "1mes"])):
    """Obtiene recomendaciones para todos los tickers con el horizonte especificado"""
    session = SessionLocal()
    tickers = session.query(Ticker).all()
    session.close()
    
    resultados = []
    for ticker in tickers:
        try:
            rec = binance_service.get_recommendation(ticker.symbol)
            if "error" not in rec:
                indicadores = rec.get("indicators", {})
                resultados.append({
                    "symbol": ticker.symbol,
                    "recomendacion": rec.get("recommendation", "NEUTRAL"),
                    "horizonte": horizonte,
                    "precio": rec.get("price"),
                    "indicadores": {
                        "rsi": indicadores.get("rsi"),
                        "macd": indicadores.get("macd"),
                        "sma_7": indicadores.get("sma_20"),  # Usar sma_20 como aproximación
                        "sma_21": indicadores.get("sma_20"),  # Usar sma_20 como aproximación
                        "sma_50": indicadores.get("sma_50"),
                        "sma_200": indicadores.get("sma_50")  # Usar sma_50 como aproximación
                    },
                    "soportes": [],  # No disponible en la nueva implementación
                    "resistencias": []  # No disponible en la nueva implementación
                })
            else:
                resultados.append({
                    "symbol": ticker.symbol,
                    "error": rec["error"],
                    "horizonte": horizonte
                })
        except Exception as e:
            resultados.append({
                "symbol": ticker.symbol,
                "error": str(e),
                "horizonte": horizonte
            })
    
    return {"horizonte": horizonte, "resultados": resultados}

# ===== ENDPOINTS DE REPORTING Y AUDITORÍA =====

@app.get("/reporting/resumen")
def obtener_resumen_ejecutivo(fecha_inicio: str = None, fecha_fin: str = None):
    """Obtiene un resumen ejecutivo del rendimiento del sistema"""
    from datetime import datetime
    
    session = SessionLocal()
    reporting_service = ReportingService(session)
    
    # Convertir fechas si se proporcionan
    fecha_inicio_dt = None
    fecha_fin_dt = None
    
    if fecha_inicio:
        fecha_inicio_dt = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
    if fecha_fin:
        fecha_fin_dt = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
    
    try:
        resumen = reporting_service.obtener_resumen_ejecutivo(fecha_inicio_dt, fecha_fin_dt)
        session.close()
        return resumen
    except Exception as e:
        session.close()
        return {"error": f"Error al generar resumen: {str(e)}"}

@app.get("/reporting/detalle/{simbolo}")
def obtener_detalle_simbolo(simbolo: str, fecha_inicio: str = None, fecha_fin: str = None):
    """Obtiene un análisis detallado por símbolo"""
    from datetime import datetime
    
    session = SessionLocal()
    reporting_service = ReportingService(session)
    
    # Convertir fechas si se proporcionan
    fecha_inicio_dt = None
    fecha_fin_dt = None
    
    if fecha_inicio:
        fecha_inicio_dt = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
    if fecha_fin:
        fecha_fin_dt = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
    
    try:
        detalle = reporting_service.obtener_detalle_por_simbolo(simbolo, fecha_inicio_dt, fecha_fin_dt)
        session.close()
        return detalle
    except Exception as e:
        session.close()
        return {"error": f"Error al generar detalle: {str(e)}"}

@app.get("/reporting/evolucion")
def obtener_evolucion_pesos(fecha_inicio: str = None, fecha_fin: str = None):
    """Obtiene la evolución de los pesos del motor de decisión"""
    from datetime import datetime
    
    session = SessionLocal()
    reporting_service = ReportingService(session)
    
    # Convertir fechas si se proporcionan
    fecha_inicio_dt = None
    fecha_fin_dt = None
    
    if fecha_inicio:
        fecha_inicio_dt = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
    if fecha_fin:
        fecha_fin_dt = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
    
    try:
        evolucion = reporting_service.obtener_evolucion_pesos(fecha_inicio_dt, fecha_fin_dt)
        session.close()
        return {"evolucion_pesos": evolucion}
    except Exception as e:
        session.close()
        return {"error": f"Error al obtener evolución: {str(e)}"}

@app.post("/reporting/registrar-recomendacion")
def registrar_recomendacion(data: dict):
    """Registra una nueva recomendación para seguimiento posterior"""
    session = SessionLocal()
    reporting_service = ReportingService(session)
    
    try:
        performance = reporting_service.registrar_recomendacion(
            simbolo=data["simbolo"],
            recomendacion=data["recomendacion"],
            precio_recomendacion=data["precio"],
            pesos_utilizados=data["pesos"],
            indicadores_utilizados=data["indicadores"],
            contexto_mercado=data.get("contexto")
        )
        session.close()
        return {
            "id": performance.id,
            "fecha": performance.fecha_recomendacion.isoformat(),
            "mensaje": "Recomendación registrada exitosamente"
        }
    except Exception as e:
        session.close()
        return {"error": f"Error al registrar recomendación: {str(e)}"}

@app.post("/reporting/verificar-recomendacion")
def verificar_recomendacion(data: dict):
    """Verifica el resultado de una recomendación previa"""
    session = SessionLocal()
    reporting_service = ReportingService(session)
    
    try:
        performance = reporting_service.verificar_recomendacion(
            id_recomendacion=data["id_recomendacion"],
            precio_verificacion=data["precio_verificacion"],
            resultado=data["resultado"]
        )
        session.close()
        
        if performance:
            return {
                "id": performance.id,
                "resultado": performance.resultado,
                "precision": performance.precision,
                "mensaje": "Recomendación verificada exitosamente"
            }
        else:
            return {"error": "Recomendación no encontrada"}
    except Exception as e:
        session.close()
        return {"error": f"Error al verificar recomendación: {str(e)}"}

@app.post("/reporting/registrar-optimizacion")
def registrar_optimizacion(data: dict):
    """Registra una nueva optimización en el historial"""
    session = SessionLocal()
    reporting_service = ReportingService(session)
    
    try:
        optimizacion = reporting_service.registrar_optimizacion(
            tipo_optimizacion=data["tipo"],
            descripcion=data["descripcion"],
            pesos_anteriores=data["pesos_anteriores"],
            pesos_nuevos=data["pesos_nuevos"],
            parametros_anteriores=data.get("parametros_anteriores"),
            parametros_nuevos=data.get("parametros_nuevos"),
            motivo_ajuste=data.get("motivo", ""),
            metricas_resultado=data.get("metricas"),
            usuario=data.get("usuario", "sistema")
        )
        session.close()
        return {
            "id": optimizacion.id,
            "fecha": optimizacion.fecha.isoformat(),
            "mensaje": "Optimización registrada exitosamente"
        }
    except Exception as e:
        session.close()
        return {"error": f"Error al registrar optimización: {str(e)}"}

@app.get("/reporting/exportar/{formato}")
def exportar_datos(formato: str, fecha_inicio: str = None, fecha_fin: str = None):
    """Exporta los datos en el formato especificado (json o csv)"""
    from datetime import datetime
    
    session = SessionLocal()
    reporting_service = ReportingService(session)
    
    # Convertir fechas si se proporcionan
    fecha_inicio_dt = None
    fecha_fin_dt = None
    
    if fecha_inicio:
        fecha_inicio_dt = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
    if fecha_fin:
        fecha_fin_dt = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
    
    try:
        filename = reporting_service.exportar_datos(formato, fecha_inicio_dt, fecha_fin_dt)
        session.close()
        return {
            "archivo_generado": filename,
            "formato": formato,
            "mensaje": f"Datos exportados exitosamente en formato {formato.upper()}"
        }
    except Exception as e:
        session.close()
        return {"error": f"Error al exportar datos: {str(e)}"}

@app.get("/cache/stats")
def get_cache_stats():
    """Obtiene estadísticas del cache de recomendaciones"""
    from services.cache_service import get_cache_stats
    return get_cache_stats()

@app.post("/cache/clear")
def clear_cache():
    """Limpia el cache expirado"""
    from services.cache_service import clear_expired_cache
    clear_expired_cache()
    return {"message": "Cache limpiado exitosamente"} 

@app.get("/learning/status")
def get_learning_status():
    """
    Obtiene el estado actual del sistema de aprendizaje automático
    """
    try:
        from services.learning_service import get_ticker_performance_summary
        import os
        
        # Obtener resumen por ticker
        ticker_summary = get_ticker_performance_summary()
        
        # Contar señales con resultados
        session = SessionLocal()
        total_signals = session.query(Signal).count()
        signals_with_results = session.query(Signal).filter(
            (Signal.resultado_real_1h != None) |
            (Signal.resultado_real_4h != None) |
            (Signal.resultado_real_24h != None) |
            (Signal.resultado_real_7d != None)
        ).count()
        
        # Calcular promedio de rendimiento
        rendimientos = [data['performance_24h'] for data in ticker_summary.values()]
        promedio_rendimiento = sum(rendimientos) / len(rendimientos) if rendimientos else 0.0
        
        # Obtener última optimización
        ultima_optimizacion = "N/A"
        if os.path.exists('data/ticker_weights.json'):
            stat = os.stat('data/ticker_weights.json')
            from datetime import datetime
            ultima_optimizacion = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        session.close()
        
        return {
            "status": "activo",
            "total_señales": total_signals,
            "señales_con_resultados": signals_with_results,
            "promedio_rendimiento": f"{promedio_rendimiento:.2%}",
            "ultima_optimizacion": ultima_optimizacion,
            "tickers_optimizados": len(ticker_summary),
            "resumen_por_ticker": ticker_summary
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/learning/optimize-now")
def optimize_weights_now():
    """
    Ejecuta la optimización de pesos individuales por ticker inmediatamente
    """
    try:
        from services.learning_service import optimize_all_tickers
        print("🤖 Iniciando optimización manual de pesos por ticker...")
        
        # Optimizar para horizonte 24h (puedes cambiar esto)
        horizonte = 'resultado_real_24h'
        resultados = optimize_all_tickers(horizonte=horizonte)
        
        # Contar éxitos y errores
        exitos = sum(1 for r in resultados.values() if r['status'] == 'success')
        errores = len(resultados) - exitos
        
        return {
            "status": "completado",
            "mensaje": f"Optimización manual completada para {len(resultados)} tickers",
            "exitos": exitos,
            "errores": errores,
            "resultados": resultados
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        } 