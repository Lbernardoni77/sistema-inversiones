from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from services.binance_service import get_binance_price, get_recommendation, get_binance_klines, log_signal
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
from services.binance_service import get_recommendation

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
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
            rec = get_recommendation(t.symbol)
            if "error" in rec:
                continue
            
            # Extraer indicadores del detalle
            detalle = rec.get("detalle", {})
            indicadores = detalle.get("indicadores", {})
            
            signal = Signal(
                ticker_id=t.id,
                price=rec.get("contexto_sr", {}).get("precio"),
                rsi=indicadores.get("rsi"),
                sma_7=indicadores.get("sma_7"),
                sma_21=indicadores.get("sma_21"),
                sma_50=indicadores.get("sma_50"),
                sma_200=indicadores.get("sma_200"),
                macd=indicadores.get("macd"),
                macd_signal=indicadores.get("macd_signal"),
                macd_hist=indicadores.get("macd_hist"),
                bb_upper=indicadores.get("bb_upper"),
                bb_mid=indicadores.get("bb_mid"),
                bb_lower=indicadores.get("bb_lower"),
                obv=indicadores.get("obv"),
                vwap=indicadores.get("vwap"),
                sharpe_ratio=indicadores.get("sharpe_ratio"),
                recomendacion=rec.get("recomendacion"),
                soportes=json.dumps(rec.get("soportes", [])),
                resistencias=json.dumps(rec.get("resistencias", [])),
                contexto_sr=json.dumps(rec.get("contexto_sr", {}))
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
    from services.binance_service import get_binance_price
    for s in signals:
        for campo, delta in horizontes:
            if getattr(s, campo) is not None:
                continue  # Ya calculado
            if (now - s.timestamp) < delta:
                continue  # Aún no pasó el horizonte
            price_data = get_binance_price(s.ticker.symbol)
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
def binance_price(symbol: str, period: str = Query("1d", enum=["1d", "1mo", "1y", "all"])):
    return get_binance_price(symbol, period)

@app.get("/binance/recommendation/{symbol}")
def binance_recommendation(symbol: str, horizonte: str = Query("24h", enum=["1h", "4h", "12h", "24h", "7d", "1mes"])):
    # Indicadores técnicos y de volumen
    rec = get_recommendation(symbol, horizonte)
    recomendacion_tecnica = rec.get("recomendacion", "Mantener")
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
    from services.binance_service import closes_volumes_from_klines, get_binance_klines
    klines = get_binance_klines(symbol)
    closes, _ = closes_volumes_from_klines(klines)
    returns = [(closes[i] - closes[i-1])/closes[i-1] for i in range(1, len(closes))] if len(closes) > 1 else []
    sharpe = sharpe_ratio(returns)
    # Ajuste de recomendación según sentimiento de noticias
    score = sentimiento_noticias["score"]
    recomendacion = recomendacion_tecnica
    ajuste_noticias = "Sin ajuste"
    if score > 0:
        if recomendacion == "Mantener":
            recomendacion = "Comprar"
            ajuste_noticias = "Noticias positivas reforzaron señal de compra"
        elif recomendacion == "Vender":
            recomendacion = "Mantener"
            ajuste_noticias = "Noticias positivas moderaron señal de venta"
    elif score < 0:
        if recomendacion == "Mantener":
            recomendacion = "Vender"
            ajuste_noticias = "Noticias negativas reforzaron señal de venta"
        elif recomendacion == "Comprar":
            recomendacion = "Mantener"
            ajuste_noticias = "Noticias negativas moderaron señal de compra"
    # Ajuste por Fear & Greed
    ajuste_fg = "Sin ajuste"
    if fg_value is not None:
        if fg_value > 75 and recomendacion == "Comprar":
            recomendacion = "Mantener"
            ajuste_fg = "Fear & Greed alto (>75) moderó señal de compra"
        elif fg_value < 25 and recomendacion == "Vender":
            recomendacion = "Mantener"
            ajuste_fg = "Fear & Greed bajo (<25) moderó señal de venta"
    # Resumen de ponderación
    resumen_ponderacion = {
        "recomendacion_tecnica": recomendacion_tecnica,
        "peso_indicadores_tecnicos": "70% (RSI, SMA, MACD, Bollinger, OBV, VWAP)",
        "ajuste_noticias": ajuste_noticias,
        "peso_noticias": "20% (análisis de sentimiento en titulares)",
        "ajuste_fear_greed": ajuste_fg,
        "peso_fear_greed": "10% (precaución en extremos de sentimiento)",
        "recomendacion_final": recomendacion,
        "explicacion": f"La recomendación se basa principalmente en indicadores técnicos ({recomendacion_tecnica}), ajustada por sentimiento de noticias y precaución ante extremos de mercado."
    }
    # Respuesta principal y detalle
    detalle = {
        "motivo": rec.get("motivo", []),
        "indicadores": {
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
            "vwap": rec.get("vwap"),
            "sharpe_ratio": sharpe
        },
        "soportes": rec.get("soportes", []),
        "resistencias": rec.get("resistencias", []),
        "fundamental": fundamental,
        "onchain": onchain,
        "sentimiento": {"fear_and_greed": fear_greed, "noticias": sentimiento_noticias},
        "noticias": news,
        "resumen_ponderacion": rec.get("resumen_ponderacion", {})
    }
    return {"recomendacion": recomendacion, "horizonte": horizonte, "detalle": detalle}

@app.post("/binance/snapshot")
def binance_snapshot(tickers: List[str] = Body(..., embed=True)):
    resultados = []
    for symbol in tickers:
        rec = get_recommendation(symbol)
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
        log_signal(symbol, rec.get("price"), indicadores, rec.get("recomendacion"))
        resultados.append({"symbol": symbol, "recomendacion": rec.get("recomendacion"), "indicadores": indicadores})
    return {"resultados": resultados}

@app.get("/binance/klines/{symbol}")
def binance_klines(symbol: str, interval: str = Query("1d"), limit: int = Query(30)):
    return get_binance_klines(symbol, interval, limit)

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
            rec = get_recommendation(ticker.symbol, horizonte)
            if "error" not in rec:
                resultados.append({
                    "symbol": ticker.symbol,
                    "recomendacion": rec.get("recomendacion", "Mantener"),
                    "horizonte": horizonte,
                    "precio": rec.get("price"),
                    "indicadores": {
                        "rsi": rec.get("rsi"),
                        "macd": rec.get("macd"),
                        "sma_7": rec.get("sma_7"),
                        "sma_21": rec.get("sma_21"),
                        "sma_50": rec.get("sma_50"),
                        "sma_200": rec.get("sma_200")
                    },
                    "soportes": rec.get("soportes", []),
                    "resistencias": rec.get("resistencias", [])
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