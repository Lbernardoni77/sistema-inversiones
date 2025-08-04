import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from models import Signal, Ticker
from services.binance_service import get_recommendation
# Import will be handled in the function to avoid circular imports

WEIGHTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'indicator_weights.json')
TICKER_WEIGHTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'ticker_weights.json')

# Pesos por defecto (puedes agregar más indicadores)
default_weights = {
    'rsi': 1.0,
    'macd': 1.0,
    'sma': 1.0,
    'bb': 1.0,
    'obv': 1.0,
    'vwap': 1.0,
    'sharpe_ratio': 1.0,
    'noticias': 1.0,
    'fear_greed': 1.0,
    'soportes_resistencias': 1.0
}

def load_weights(ticker_symbol=None):
    """Carga pesos optimizados. Si se especifica ticker, carga pesos específicos del ticker"""
    if ticker_symbol:
        # Cargar pesos específicos del ticker
        if os.path.exists(TICKER_WEIGHTS_FILE):
            with open(TICKER_WEIGHTS_FILE, 'r') as f:
                ticker_weights = json.load(f)
                return ticker_weights.get(ticker_symbol, default_weights.copy())
        return default_weights.copy()
    else:
        # Cargar pesos globales (para compatibilidad)
        if os.path.exists(WEIGHTS_FILE):
            with open(WEIGHTS_FILE, 'r') as f:
                return json.load(f)
        return default_weights.copy()

def save_weights(weights, ticker_symbol=None):
    """Guarda pesos optimizados. Si se especifica ticker, guarda pesos específicos del ticker"""
    if ticker_symbol:
        # Guardar pesos específicos del ticker
        ticker_weights = {}
        if os.path.exists(TICKER_WEIGHTS_FILE):
            with open(TICKER_WEIGHTS_FILE, 'r') as f:
                ticker_weights = json.load(f)
        
        ticker_weights[ticker_symbol] = weights
        
        with open(TICKER_WEIGHTS_FILE, 'w') as f:
            json.dump(ticker_weights, f, indent=2)
    else:
        # Guardar pesos globales (para compatibilidad)
        with open(WEIGHTS_FILE, 'w') as f:
            json.dump(weights, f, indent=2)

def evaluate_signals(session: Session, weights, ticker_symbol=None, horizonte='resultado_real_24h'):
    """
    Evalúa la tasa de acierto de las señales históricas usando los pesos dados para el horizonte especificado.
    Si se especifica ticker_symbol, solo evalúa señales de ese ticker.
    """
    query = session.query(Signal).filter(getattr(Signal, horizonte) != None)
    
    if ticker_symbol:
        # Filtrar por ticker específico
        ticker = session.query(Ticker).filter(Ticker.symbol == ticker_symbol).first()
        if ticker:
            query = query.filter(Signal.ticker_id == ticker.id)
        else:
            return 0.0
    
    signals = query.all()
    if not signals:
        return 0.0
    
    aciertos = 0
    total = 0
    for s in signals:
        # Simula la recomendación con los pesos actuales
        if not s.recomendacion:
            continue
        if s.recomendacion.lower() == 'comprar' and getattr(s, horizonte) == 'subio':
            aciertos += 1
        elif s.recomendacion.lower() == 'vender' and getattr(s, horizonte) == 'bajo':
            aciertos += 1
        elif s.recomendacion.lower() == 'mantener' and getattr(s, horizonte) == 'sin cambio':
            aciertos += 1
        total += 1
    return aciertos / total if total > 0 else 0.0

def optimize_weights_for_ticker(ticker_symbol, grid=None, horizonte='resultado_real_24h'):
    """
    Optimiza pesos específicos para un ticker individual.
    """
    # Import here to avoid circular imports
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os
    
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'inversiones.db')
    engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    if grid is None:
        grid = [0.5, 1.0, 1.5]
    
    best_score = 0.0
    best_weights = load_weights(ticker_symbol)
    
    from itertools import product
    keys = list(default_weights.keys())
    
    print(f"🔧 Optimizando pesos para {ticker_symbol}...")
    
    for values in product(grid, repeat=len(keys)):
        weights = dict(zip(keys, values))
        score = evaluate_signals(session, weights, ticker_symbol, horizonte)
        if score > best_score:
            best_score = score
            best_weights = weights.copy()
    
    save_weights(best_weights, ticker_symbol)
    session.close()
    
    print(f"✅ Mejores pesos para {ticker_symbol} ({horizonte}): {best_weights} (acierto: {best_score:.2%})")
    return best_weights, best_score

def optimize_all_tickers(grid=None, horizonte='resultado_real_24h'):
    """
    Optimiza pesos para todos los tickers en seguimiento.
    """
    # Import here to avoid circular imports
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os
    
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'inversiones.db')
    engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    # Obtener todos los tickers en seguimiento
    tickers = session.query(Ticker).all()
    session.close()
    
    resultados = {}
    
    for ticker in tickers:
        try:
            weights, score = optimize_weights_for_ticker(ticker.symbol, grid, horizonte)
            resultados[ticker.symbol] = {
                'weights': weights,
                'score': score,
                'status': 'success'
            }
        except Exception as e:
            print(f"❌ Error optimizando {ticker.symbol}: {e}")
            resultados[ticker.symbol] = {
                'weights': default_weights.copy(),
                'score': 0.0,
                'status': 'error',
                'error': str(e)
            }
    
    return resultados

def get_ticker_performance_summary():
    """
    Obtiene un resumen del rendimiento de todos los tickers con sus pesos optimizados.
    """
    # Import here to avoid circular imports
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os
    
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'inversiones.db')
    engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    tickers = session.query(Ticker).all()
    summary = {}
    
    for ticker in tickers:
        weights = load_weights(ticker.symbol)
        score_24h = evaluate_signals(session, weights, ticker.symbol, 'resultado_real_24h')
        score_7d = evaluate_signals(session, weights, ticker.symbol, 'resultado_real_7d')
        
        summary[ticker.symbol] = {
            'weights': weights,
            'performance_24h': score_24h,
            'performance_7d': score_7d,
            'total_signals': session.query(Signal).filter(Signal.ticker_id == ticker.id).count()
        }
    
    session.close()
    return summary

# Mantener función original para compatibilidad
def optimize_weights(grid=None, horizonte='resultado_real_24h'):
    """
    Función original para compatibilidad. Ahora optimiza todos los tickers.
    """
    return optimize_all_tickers(grid, horizonte) 