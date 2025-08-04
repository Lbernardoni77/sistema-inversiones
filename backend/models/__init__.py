# NOTA: Si ves errores de importación, ejecuta 'pip install -r requirements.txt' para instalar sqlalchemy y apscheduler.
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Ticker(Base):
    __tablename__ = 'tickers'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    signals = relationship('Signal', back_populates='ticker')

class Signal(Base):
    __tablename__ = 'signals'
    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'))
    price = Column(Float)
    rsi = Column(Float)
    sma_7 = Column(Float)
    sma_21 = Column(Float)
    sma_50 = Column(Float)
    sma_200 = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_hist = Column(Float)
    bb_upper = Column(Float)
    bb_mid = Column(Float)
    bb_lower = Column(Float)
    obv = Column(Float)
    vwap = Column(Float)
    sharpe_ratio = Column(Float)
    recomendacion = Column(String)
    soportes = Column(Text)  # JSON serializado
    resistencias = Column(Text)  # JSON serializado
    contexto_sr = Column(Text)  # JSON serializado (influencia, nivel, etc)
    resultado_real = Column(String, nullable=True)  # 'subio', 'bajo', 'sin cambio'
    resultado_real_1h = Column(String, nullable=True)
    resultado_real_4h = Column(String, nullable=True)
    resultado_real_12h = Column(String, nullable=True)
    resultado_real_24h = Column(String, nullable=True)
    resultado_real_7d = Column(String, nullable=True)
    resultado_real_1mes = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ticker = relationship('Ticker', back_populates='signals') 

class OptimizationHistory(Base):
    """Modelo para registrar el historial de optimizaciones del motor de decisión"""
    __tablename__ = 'optimization_history'
    
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    tipo_optimizacion = Column(String(100))  # 'pesos', 'parametros', 'nuevo_indicador'
    descripcion = Column(Text)
    pesos_anteriores = Column(JSON)
    pesos_nuevos = Column(JSON)
    parametros_anteriores = Column(JSON)
    parametros_nuevos = Column(JSON)
    motivo_ajuste = Column(Text)
    metricas_resultado = Column(JSON)  # precision, recall, etc.
    usuario = Column(String(100), default='sistema')

class RecommendationPerformance(Base):
    """Modelo para registrar el rendimiento de las recomendaciones vs realidad"""
    __tablename__ = 'recommendation_performance'
    
    id = Column(Integer, primary_key=True)
    fecha_recomendacion = Column(DateTime)
    fecha_verificacion = Column(DateTime)
    simbolo = Column(String(20))
    recomendacion = Column(String(20))  # 'comprar', 'vender', 'mantener'
    precio_recomendacion = Column(Float)
    precio_verificacion = Column(Float)
    resultado = Column(String(20))  # 'exitoso', 'fallido', 'neutral'
    precision = Column(Float)
    pesos_utilizados = Column(JSON)
    indicadores_utilizados = Column(JSON)
    contexto_mercado = Column(JSON)  # volatilidad, tendencia, etc. 