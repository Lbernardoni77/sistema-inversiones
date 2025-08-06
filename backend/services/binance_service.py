import httpx
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import csv
import os

# Configuración de API keys de Binance
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

# Configuración de proxy para sortear error 451
PROXY_URL = os.getenv('PROXY_URL')  # ej: "http://proxy-server:port"
PROXY_USERNAME = os.getenv('PROXY_USERNAME')
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD')

# URLs de APIs
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"

# API alternativa sin restricciones
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# Cache simple para precios
price_cache = {}
cache_duration = 300  # 5 minutos (aumentado de 60 segundos)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SIGNALS_FILE = os.path.join(DATA_DIR, 'signals.csv')

def get_httpx_client():
    """Crear cliente HTTP con configuración de proxy si está disponible"""
    # Headers mejorados para sortear restricciones
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site'
    }
    
    # Configurar proxy si está disponible (usando el método correcto para httpx)
    if PROXY_URL:
        if PROXY_USERNAME and PROXY_PASSWORD:
            # Proxy con autenticación
            proxy_auth = f"{PROXY_USERNAME}:{PROXY_PASSWORD}"
            proxy_url = f"http://{proxy_auth}@{PROXY_URL.replace('http://', '')}"
        else:
            # Proxy sin autenticación
            proxy_url = PROXY_URL
        
        return httpx.Client(proxies=proxy_url, timeout=15, headers=headers)
    else:
        return httpx.Client(timeout=15, headers=headers)

def get_binance_price(symbol: str, period: str = "1d") -> dict:
    # Intentar primero con Binance (con API keys y proxy si está configurado)
    url = f"{BINANCE_API_URL}?symbol={symbol.upper()}"
    headers = {}
    if BINANCE_API_KEY:
        headers['X-MBX-APIKEY'] = BINANCE_API_KEY
    
    try:
        # Usar cliente HTTP con proxy si está configurado
        with get_httpx_client() as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            price_actual = float(data["price"])
            
            # Continuar con el resto de la lógica de Binance...
            return process_binance_data(symbol, price_actual, period)
        
    except Exception as e:
        # Si Binance falla, usar CoinGecko como fallback
        print(f"Binance falló para {symbol}, usando CoinGecko: {e}")
        
        # Mapeo de símbolos de Binance a CoinGecko
        symbol_mapping = {
            'BTCUSDT': 'bitcoin',
            'ETHUSDT': 'ethereum',
            'BNBUSDT': 'binancecoin',
            'ADAUSDT': 'cardano',
            'DOTUSDT': 'polkadot',
            'LINKUSDT': 'chainlink',
            'LTCUSDT': 'litecoin',
            'BCHUSDT': 'bitcoin-cash',
            'XRPUSDT': 'ripple',
            'SOLUSDT': 'solana',
            'MATICUSDT': 'matic-network',
            'AVAXUSDT': 'avalanche-2',
            'UNIUSDT': 'uniswap',
            'ATOMUSDT': 'cosmos',
            'FTMUSDT': 'fantom',
            'NEARUSDT': 'near',
            'ALGOUSDT': 'algorand',
            'VETUSDT': 'vechain',
            'ICPUSDT': 'internet-computer',
            'FILUSDT': 'filecoin',
            'SANDUSDT': 'the-sandbox',
            'THETAUSDT': 'theta-token',
            'MANAUSDT': 'decentraland',
            'CHZUSDT': 'chiliz',
            'ENJUSDT': 'enjincoin',
            'AXSUSDT': 'axie-infinity',
            'GALAUSDT': 'gala',
            'ROSEUSDT': 'oasis-network',
            'ONEUSDT': 'harmony',
            'HOTUSDT': 'holochain',
            'BATUSDT': 'basic-attention-token',
            'ZILUSDT': 'zilliqa',
            'IOTAUSDT': 'iota',
            'NEOUSDT': 'neo',
            'QTUMUSDT': 'qtum',
            'XLMUSDT': 'stellar',
            'TRXUSDT': 'tron',
            'EOSUSDT': 'eos',
            'XMRUSDT': 'monero',
            'DASHUSDT': 'dash',
            'ZECUSDT': 'zcash',
            'DOGEUSDT': 'dogecoin',
            'SHIBUSDT': 'shiba-inu',
            'LUNCUSDT': 'terra-luna',
            'APTUSDT': 'aptos',
            'SUIUSDT': 'sui',
            'OPUSDT': 'optimism',
            'ARBUSDT': 'arbitrum',
            'MKRUSDT': 'maker',
            'AAVEUSDT': 'aave',
            'COMPUSDT': 'compound-governance-token',
            'SNXUSDT': 'havven',
            'CRVUSDT': 'curve-dao-token',
            'YFIUSDT': 'yearn-finance',
            'SUSHIUSDT': 'sushi',
            '1INCHUSDT': '1inch',
            'CAKEUSDT': 'pancakeswap-token',
            'DYDXUSDT': 'dydx',
            'RUNEUSDT': 'thorchain',
            'KSMUSDT': 'kusama'
        }
        
        return get_coingecko_price(symbol, symbol_mapping, period)

def get_coingecko_klines(symbol: str, interval: str = "1d", limit: int = 30) -> List[list]:
    """Obtener klines de CoinGecko. Si falla, devolver []."""
    try:
        # Mapeo de símbolos de Binance a CoinGecko
        symbol_mapping = {
            'BTCUSDT': 'bitcoin',
            'ETHUSDT': 'ethereum',
            'BNBUSDT': 'binancecoin',
            'ADAUSDT': 'cardano',
            'DOTUSDT': 'polkadot',
            'LINKUSDT': 'chainlink',
            'LTCUSDT': 'litecoin',
            'BCHUSDT': 'bitcoin-cash',
            'XRPUSDT': 'ripple',
            'SOLUSDT': 'solana',
            'MATICUSDT': 'matic-network',
            'AVAXUSDT': 'avalanche-2',
            'UNIUSDT': 'uniswap',
            'ATOMUSDT': 'cosmos',
            'FTMUSDT': 'fantom',
            'NEARUSDT': 'near',
            'ALGOUSDT': 'algorand',
            'VETUSDT': 'vechain',
            'ICPUSDT': 'internet-computer',
            'FILUSDT': 'filecoin',
            'SANDUSDT': 'the-sandbox',
            'THETAUSDT': 'theta-token',
            'MANAUSDT': 'decentraland',
            'CHZUSDT': 'chiliz',
            'ENJUSDT': 'enjincoin',
            'AXSUSDT': 'axie-infinity',
            'GALAUSDT': 'gala',
            'ROSEUSDT': 'oasis-network',
            'ONEUSDT': 'harmony',
            'HOTUSDT': 'holochain',
            'BATUSDT': 'basic-attention-token',
            'ZILUSDT': 'zilliqa',
            'IOTAUSDT': 'iota',
            'NEOUSDT': 'neo',
            'QTUMUSDT': 'qtum',
            'XLMUSDT': 'stellar',
            'TRXUSDT': 'tron',
            'EOSUSDT': 'eos',
            'XMRUSDT': 'monero',
            'DASHUSDT': 'dash',
            'ZECUSDT': 'zcash',
            'DOGEUSDT': 'dogecoin',
            'SHIBUSDT': 'shiba-inu',
            'LUNCUSDT': 'terra-luna',
            'APTUSDT': 'aptos',
            'SUIUSDT': 'sui',
            'OPUSDT': 'optimism',
            'ARBUSDT': 'arbitrum',
            'MKRUSDT': 'maker',
            'AAVEUSDT': 'aave',
            'COMPUSDT': 'compound-governance-token',
            'SNXUSDT': 'havven',
            'CRVUSDT': 'curve-dao-token',
            'YFIUSDT': 'yearn-finance',
            'SUSHIUSDT': 'sushi',
            '1INCHUSDT': '1inch',
            'CAKEUSDT': 'pancakeswap-token',
            'DYDXUSDT': 'dydx',
            'RUNEUSDT': 'thorchain',
            'KSMUSDT': 'kusama'
        }
        
        coingecko_id = symbol_mapping.get(symbol.upper())
        if not coingecko_id:
            return []
        
        # Obtener precio actual de CoinGecko
        import time
        current_time = time.time()
        cache_key = f"coingecko_klines_{symbol}_{interval}_{limit}"
        
        if cache_key in price_cache:
            cached_data, cached_time = price_cache[cache_key]
            if current_time - cached_time < cache_duration:
                return cached_data
        
        # Obtener precio actual
        price_url = f"{COINGECKO_API_URL}/simple/price?ids={coingecko_id}&vs_currencies=usd"
        with get_httpx_client() as client:
            response = client.get(price_url)
            response.raise_for_status()
            data = response.json()
            current_price = data[coingecko_id]['usd']
        # Aquí podrías implementar obtención de klines reales si CoinGecko lo soporta
        # Por ahora, si no hay endpoint, devolvemos []
        return []
    except Exception as e:
        print(f"Error obteniendo klines de CoinGecko para {symbol}: {e}")
        return []

def get_coingecko_price(symbol: str, symbol_mapping: dict, period: str = "1d") -> dict:
    """Obtener precio usando CoinGecko API como fallback"""
    try:
        # Buscar el ID de CoinGecko para el símbolo
        coingecko_id = symbol_mapping.get(symbol.upper())
        if not coingecko_id:
            return {"error": f"Símbolo {symbol} no soportado en CoinGecko"}
        
        # Verificar cache
        import time
        current_time = time.time()
        cache_key = f"{symbol}_{period}"
        
        if cache_key in price_cache:
            cached_data, cache_time = price_cache[cache_key]
            if current_time - cache_time < cache_duration:
                return cached_data
        
        # Agregar delay para evitar rate limiting
        time.sleep(2)  # Aumentado de 1 a 2 segundos
        
        # Obtener precio actual
        url = f"{COINGECKO_API_URL}/simple/price?ids={coingecko_id}&vs_currencies=usd&include_24hr_change=true"
        response = httpx.get(url, timeout=10)
        
        # Manejar rate limiting
        if response.status_code == 429:
            # Intentar usar cache si está disponible
            if cache_key in price_cache:
                cached_data, cache_time = price_cache[cache_key]
                if current_time - cache_time < cache_duration * 2:  # Usar cache por más tiempo si hay rate limit
                    print(f"Rate limit alcanzado, usando cache para {symbol}")
                    return cached_data
            
            # Fallback a datos estáticos si no hay cache
            print(f"Rate limit alcanzado para {symbol}, usando fallback estático")
            return get_static_price_fallback(symbol, period)
        
        response.raise_for_status()
        data = response.json()
        
        if coingecko_id not in data:
            return {"error": f"No se encontró precio para {symbol}"}
        
        price_data = data[coingecko_id]
        price_actual = price_data.get('usd', 0)
        change_24h = price_data.get('usd_24h_change', 0)
        
        result = {
            "symbol": symbol.upper(),
            "price": price_actual,
            "change_percent": change_24h,
            "period": period,
            "source": "coingecko"
        }
        
        # Guardar en cache
        price_cache[cache_key] = (result, current_time)
        
        return result
        
    except Exception as e:
        return {"error": f"Error obteniendo precio de CoinGecko: {str(e)}"}

def get_static_price_fallback(symbol: str, period: str = "1d") -> dict:
    """Fallback con precios estáticos cuando CoinGecko falla"""
    # Precios aproximados actuales (se pueden actualizar manualmente)
    static_prices = {
        'BTCUSDT': {'price': 65000, 'change': 2.5},
        'ETHUSDT': {'price': 3500, 'change': 1.8},
        'BNBUSDT': {'price': 580, 'change': 0.5},
        'ADAUSDT': {'price': 0.45, 'change': -1.2},
        'DOTUSDT': {'price': 6.8, 'change': 3.1},
        'LINKUSDT': {'price': 15.2, 'change': 2.8},
        'LTCUSDT': {'price': 85, 'change': 1.5},
        'BCHUSDT': {'price': 420, 'change': -0.8},
        'XRPUSDT': {'price': 0.52, 'change': 1.2},
        'SOLUSDT': {'price': 140, 'change': 4.2},
        'MATICUSDT': {'price': 0.75, 'change': 2.1},
        'AVAXUSDT': {'price': 28, 'change': 3.5},
        'UNIUSDT': {'price': 8.5, 'change': 1.9},
        'ATOMUSDT': {'price': 7.2, 'change': 2.3},
        'FTMUSDT': {'price': 0.35, 'change': 5.1},
        'NEARUSDT': {'price': 4.8, 'change': 2.7},
        'ALGOUSDT': {'price': 0.18, 'change': -0.5},
        'VETUSDT': {'price': 0.025, 'change': 1.8},
        'ICPUSDT': {'price': 12.5, 'change': 3.2},
        'FILUSDT': {'price': 5.8, 'change': 1.4},
        'SANDUSDT': {'price': 0.42, 'change': 2.8},
        'THETAUSDT': {'price': 1.85, 'change': 1.2},
        'MANAUSDT': {'price': 0.38, 'change': 3.1},
        'CHZUSDT': {'price': 0.08, 'change': 1.5},
        'ENJUSDT': {'price': 0.28, 'change': 2.4},
        'AXSUSDT': {'price': 6.2, 'change': 4.1},
        'GALAUSDT': {'price': 0.025, 'change': 2.8},
        'ROSEUSDT': {'price': 0.065, 'change': 1.9},
        'ONEUSDT': {'price': 0.015, 'change': 1.1},
        'HOTUSDT': {'price': 0.002, 'change': 0.8},
        'BATUSDT': {'price': 0.22, 'change': 2.1},
        'ZILUSDT': {'price': 0.018, 'change': 1.6},
        'IOTAUSDT': {'price': 0.18, 'change': 2.3},
        'NEOUSDT': {'price': 12.8, 'change': 1.7},
        'QTUMUSDT': {'price': 3.2, 'change': 2.5},
        'XLMUSDT': {'price': 0.12, 'change': 1.4},
        'TRXUSDT': {'price': 0.075, 'change': 1.8},
        'EOSUSDT': {'price': 0.65, 'change': 2.1},
        'XMRUSDT': {'price': 165, 'change': 1.9},
        'DASHUSDT': {'price': 28, 'change': 2.3},
        'ZECUSDT': {'price': 22, 'change': 1.6},
        'DOGEUSDT': {'price': 0.075, 'change': 3.2},
        'SHIBUSDT': {'price': 0.00002, 'change': 4.1},
        'LUNCUSDT': {'price': 0.00008, 'change': 1.2},
        'APTUSDT': {'price': 8.5, 'change': 2.8},
        'SUIUSDT': {'price': 1.2, 'change': 3.5},
        'OPUSDT': {'price': 2.8, 'change': 2.1},
        'ARBUSDT': {'price': 1.1, 'change': 2.9},
        'MKRUSDT': {'price': 2800, 'change': 1.5},
        'AAVEUSDT': {'price': 95, 'change': 2.7},
        'COMPUSDT': {'price': 65, 'change': 1.8},
        'SNXUSDT': {'price': 3.2, 'change': 2.4},
        'CRVUSDT': {'price': 0.45, 'change': 1.9},
        'YFIUSDT': {'price': 8500, 'change': 2.2},
        'SUSHIUSDT': {'price': 1.1, 'change': 2.6},
        '1INCHUSDT': {'price': 0.35, 'change': 3.1},
        'CAKEUSDT': {'price': 2.1, 'change': 2.8},
        'DYDXUSDT': {'price': 1.8, 'change': 3.2},
        'RUNEUSDT': {'price': 4.2, 'change': 2.5},
        'KSMUSDT': {'price': 28, 'change': 1.7}
    }
    
    symbol_upper = symbol.upper()
    if symbol_upper in static_prices:
        data = static_prices[symbol_upper]
        return {
            "symbol": symbol_upper,
            "price": data['price'],
            "change_percent": data['change'],
            "period": period,
            "source": "static_fallback"
        }
    else:
        return {"error": f"Símbolo {symbol} no soportado en fallback estático"}

def process_binance_data(symbol: str, price_actual: float, period: str = "1d") -> dict:
    """Procesar datos de Binance (función auxiliar)"""
    # Determinar cuántos días atrás buscar el cierre de referencia
    if period == "1d":
        limit = 2
    elif period == "1mo":
        limit = 31
    elif period == "1y":
        limit = 366
    elif period == "all":
        limit = 1000
    else:
        limit = 2

    klines_url = f"{BINANCE_KLINES_URL}?symbol={symbol.upper()}&interval=1d&limit={limit}"
    headers = {}
    if BINANCE_API_KEY:
        headers['X-MBX-APIKEY'] = BINANCE_API_KEY
    
    try:
        klines_resp = httpx.get(klines_url, headers=headers, timeout=10)
        klines_resp.raise_for_status()
        klines = klines_resp.json()
        if len(klines) < 2:
            return {"symbol": symbol.upper(), "price": price_actual, "error": "No hay suficientes datos históricos"}

        # Determinar el cierre de referencia según el periodo
        if period == "1d":
            close_ref = float(klines[-2][4])
        elif period == "1mo":
            close_ref = float(klines[-31][4]) if len(klines) >= 31 else float(klines[0][4])
        elif period == "1y":
            close_ref = float(klines[-366][4]) if len(klines) >= 366 else float(klines[0][4])
        elif period == "all":
            close_ref = float(klines[0][4])
        else:
            close_ref = float(klines[-2][4])

        change_percent = ((price_actual - close_ref) / close_ref) * 100 if close_ref != 0 else 0
        return {
            "symbol": symbol.upper(),
            "price": price_actual,
            "close_yesterday": close_ref,
            "change_percent": change_percent,
            "period": period,
            "source": "binance"
        }
    except Exception as e:
        return {"error": str(e)}

        # Determinar cuántos días atrás buscar el cierre de referencia
        if period == "1d":
            limit = 2
        elif period == "1mo":
            limit = 31
        elif period == "1y":
            limit = 366
        elif period == "all":
            limit = 1000  # Binance permite hasta 1000 velas por request
        else:
            limit = 2

        klines_url = f"{BINANCE_KLINES_URL}?symbol={symbol.upper()}&interval=1d&limit={limit}"
        klines_resp = httpx.get(klines_url, timeout=10)
        klines_resp.raise_for_status()
        klines = klines_resp.json()
        if len(klines) < 2:
            return {"symbol": symbol.upper(), "price": price_actual, "error": "No hay suficientes datos históricos"}

        # Determinar el cierre de referencia según el periodo
        if period == "1d":
            close_ref = float(klines[-2][4])
        elif period == "1mo":
            close_ref = float(klines[-31][4]) if len(klines) >= 31 else float(klines[0][4])
        elif period == "1y":
            close_ref = float(klines[-366][4]) if len(klines) >= 366 else float(klines[0][4])
        elif period == "all":
            close_ref = float(klines[0][4])
        else:
            close_ref = float(klines[-2][4])

        change_percent = ((price_actual - close_ref) / close_ref) * 100 if close_ref != 0 else 0
        return {
            "symbol": symbol.upper(),
            "price": price_actual,
            "close_yesterday": close_ref,  # antes 'close_reference'
            "change_percent": change_percent,
            "period": period
        }
    except Exception as e:
        return {"error": str(e)}

def get_binance_klines(symbol: str, interval: str = "1h", limit: int = 200) -> List[list]:
    url = f"{BINANCE_KLINES_URL}?symbol={symbol.upper()}&interval={interval}&limit={limit}"
    
    # Configurar headers con API key si está disponible
    headers = {}
    if BINANCE_API_KEY:
        headers['X-MBX-APIKEY'] = BINANCE_API_KEY
    
    try:
        # Usar cliente HTTP con proxy si está configurado
        with get_httpx_client() as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data and len(data) > 0:
                return data
            else:
                raise Exception("No data received from Binance")
    except Exception as e:
        print(f"Binance klines falló para {symbol}, usando CoinGecko: {e}")
        # Usar CoinGecko como fallback
        klines = get_coingecko_klines(symbol, interval, limit)
        if klines and len(klines) > 0:
            return klines
        else:
            print(f"No se pudieron obtener klines reales para {symbol} ni de Binance ni de CoinGecko.")
            return []

def closes_volumes_from_klines(klines: List[list]):
    closes = [float(k[4]) for k in klines]
    volumes = [float(k[5]) for k in klines]
    return closes, volumes

def sma(data: List[float], period: int) -> Optional[float]:
    if len(data) < period:
        return None
    return sum(data[-period:]) / period

def macd(data: List[float], short_period: int = 12, long_period: int = 26, signal_period: int = 9):
    if len(data) < long_period + signal_period:
        return None, None, None
    ema_short = ema(data, short_period)[-len(data):]
    ema_long = ema(data, long_period)[-len(data):]
    macd_line = [s - l for s, l in zip(ema_short, ema_long)]
    signal_line = ema(macd_line, signal_period)[-len(macd_line):]
    hist = [m - s for m, s in zip(macd_line, signal_line)]
    return macd_line[-1], signal_line[-1], hist[-1]

def ema(data: List[float], period: int) -> List[float]:
    ema_values = []
    k = 2 / (period + 1)
    for i, price in enumerate(data):
        if i == 0:
            ema_values.append(price)
        else:
            ema_values.append(price * k + ema_values[-1] * (1 - k))
    return ema_values

def bollinger_bands(data: List[float], period: int = 20, num_std: float = 2.0):
    if len(data) < period:
        return None, None, None
    sma_val = sma(data, period)
    if sma_val is None:
        return None, None, None
    std = (sum([(x - sma_val) ** 2 for x in data[-period:]]) / period) ** 0.5
    upper = sma_val + num_std * std
    lower = sma_val - num_std * std
    return upper, sma_val, lower

def obv(closes: List[float], volumes: List[float]) -> Optional[float]:
    if len(closes) < 2:
        return None
    obv_val = 0
    for i in range(1, len(closes)):
        if closes[i] > closes[i-1]:
            obv_val += volumes[i]
        elif closes[i] < closes[i-1]:
            obv_val -= volumes[i]
    return obv_val

def vwap(closes: List[float], volumes: List[float]) -> Optional[float]:
    if not closes or not volumes or len(closes) != len(volumes):
        return None
    total = sum([c * v for c, v in zip(closes, volumes)])
    vol = sum(volumes)
    return total / vol if vol != 0 else None

def rsi(data: List[float], period: int = 14) -> Optional[float]:
    if len(data) < period + 1:
        return None
    
    # Filtrar valores None y convertir a float
    clean_data = []
    for value in data:
        if value is not None:
            clean_data.append(float(value))
    
    if len(clean_data) < period + 1:
        return None
    
    gains = []
    losses = []
    for i in range(-period, 0):
        if i < len(clean_data) - 1:  # Asegurar que tenemos al menos 2 valores
            diff = clean_data[i] - clean_data[i-1]
            if diff > 0:
                gains.append(diff)
            else:
                losses.append(abs(diff))
    
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0.0001
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def log_signal(symbol, price, indicadores, recomendacion):
    os.makedirs(DATA_DIR, exist_ok=True)
    file_exists = os.path.isfile(SIGNALS_FILE)
    with open(SIGNALS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                'timestamp','symbol','price','rsi','sma_7','sma_21','sma_50','sma_200','macd','macd_signal','macd_hist','bb_upper','bb_mid','bb_lower','obv','vwap','recomendacion'
            ])
        writer.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            price,
            indicadores.get('rsi'),
            indicadores.get('sma_7'),
            indicadores.get('sma_21'),
            indicadores.get('sma_50'),
            indicadores.get('sma_200'),
            indicadores.get('macd'),
            indicadores.get('macd_signal'),
            indicadores.get('macd_hist'),
            indicadores.get('bb_upper'),
            indicadores.get('bb_mid'),
            indicadores.get('bb_lower'),
            indicadores.get('obv'),
            indicadores.get('vwap'),
            recomendacion
        ])

def get_recommendation(symbol: str, horizonte: str = "24h") -> dict:
    """
    Calcula la recomendación (Comprar, Mantener, Vender) combinando indicadores técnicos, fundamentales, sentimiento y soportes/resistencias.
    - Cada indicador suma o resta puntos según reglas configurables.
    - El puntaje total determina la recomendación:
        > 3: Comprar
        < -3: Vender
        entre -3 y 3: Mantener
    - Los pesos y reglas pueden ajustarse fácilmente para experimentación o aprendizaje automático futuro.
    - El sistema está preparado para guardar el resultado real (si subió, bajó o quedó sin cambio) para retroalimentación y ajuste de pesos.
    """
    # Verificar cache primero
    from services.cache_service import get_cached_recommendation, cache_recommendation
    
    cached_result = get_cached_recommendation(symbol, horizonte)
    if cached_result:
        print(f"📦 Cache hit para {symbol} ({horizonte})")
        return cached_result
    
    # Cargar pesos optimizados específicos del ticker
    try:
        from services.learning_service import load_weights
        optimized_weights = load_weights(symbol)
        print(f"🧠 Usando pesos optimizados para {symbol}: {optimized_weights}")
    except Exception as e:
        print(f"⚠️ No se pudieron cargar pesos optimizados para {symbol}: {e}")
        optimized_weights = None
    
    from services.external_data_service import get_fear_and_greed_index, get_crypto_news, analizar_sentimiento_noticias, sharpe_ratio
    klines = get_binance_klines(symbol)
    if not klines or len(klines) < 50:
        return {"error": "No hay suficientes datos para análisis"}
    
    closes, volumes = closes_volumes_from_klines(klines)
    rsi_value = rsi(closes)
    sma_7 = sma(closes, 7)
    sma_21 = sma(closes, 21)
    sma_50 = sma(closes, 50)
    sma_200 = sma(closes, 200)
    macd_val, macd_signal, macd_hist = macd(closes)
    bb_upper, bb_mid, bb_lower = bollinger_bands(closes)
    obv_val = obv(closes, volumes)
    vwap_val = vwap(closes, volumes)
    
    # --- Soportes y resistencias ---
    def niveles_extremos(data, window):
        if len(data) < window:
            return [], []
        
        soportes = []
        resistencias = []
        
        # Encontrar mínimos y máximos locales
        for i in range(window, len(data) - window):
            ventana_izq = data[i-window:i]
            ventana_der = data[i:i+window]
            actual = data[i]
            
            # Es un soporte si es el mínimo en la ventana
            if actual == min(ventana_izq + [actual] + ventana_der):
                soportes.append(actual)
            
            # Es una resistencia si es el máximo en la ventana
            if actual == max(ventana_izq + [actual] + ventana_der):
                resistencias.append(actual)
        
        # Tomar los 3 niveles más recientes y relevantes
        soportes = sorted(list(set(soportes)), reverse=True)[:3]
        resistencias = sorted(list(set(resistencias)))[:3]
        
        return soportes, resistencias
    
    # Calcular soportes y resistencias con diferentes ventanas
    soportes_5, resistencias_5 = niveles_extremos(closes, 5)
    soportes_10, resistencias_10 = niveles_extremos(closes, 10)
    soportes_20, resistencias_20 = niveles_extremos(closes, 20)
    
    # Combinar todos los niveles
    todos_soportes = list(set(soportes_5 + soportes_10 + soportes_20))
    todas_resistencias = list(set(resistencias_5 + resistencias_10 + resistencias_20))
    
    # Ordenar por relevancia (más cercanos al precio actual)
    precio_actual = closes[-1]
    todos_soportes = sorted(todos_soportes, key=lambda x: abs(x - precio_actual))[:3]
    todas_resistencias = sorted(todas_resistencias, key=lambda x: abs(x - precio_actual))[:3]
    
    # --- Análisis de soportes y resistencias ---
    puntaje_sr = 0
    contexto_sr = {
        "soportes_cercanos": [],
        "resistencias_cercanas": [],
        "distancia_soporte": None,
        "distancia_resistencia": None
    }
    
    # Buscar soportes cercanos (por debajo del precio actual)
    soportes_cercanos = [s for s in todos_soportes if s < precio_actual]
    if soportes_cercanos:
        soporte_mas_cercano = max(soportes_cercanos)
        distancia_soporte = ((precio_actual - soporte_mas_cercano) / precio_actual) * 100
        contexto_sr["distancia_soporte"] = distancia_soporte
        contexto_sr["soportes_cercanos"] = soportes_cercanos
        
        if distancia_soporte < 2:  # Muy cerca del soporte
            puntaje_sr += 2
        elif distancia_soporte < 5:  # Cerca del soporte
            puntaje_sr += 1
    
    # Buscar resistencias cercanas (por encima del precio actual)
    resistencias_cercanas = [r for r in todas_resistencias if r > precio_actual]
    if resistencias_cercanas:
        resistencia_mas_cercana = min(resistencias_cercanas)
        distancia_resistencia = ((resistencia_mas_cercana - precio_actual) / precio_actual) * 100
        contexto_sr["distancia_resistencia"] = distancia_resistencia
        contexto_sr["resistencias_cercanas"] = resistencias_cercanas
        
        if distancia_resistencia < 2:  # Muy cerca de la resistencia
            puntaje_sr -= 2
        elif distancia_resistencia < 5:  # Cerca de la resistencia
            puntaje_sr -= 1
    
    # --- Indicadores técnicos con pesos optimizados ---
    puntaje_total = 0
    motivo = []
    
    # Usar pesos optimizados si están disponibles, sino usar pesos por defecto
    if optimized_weights:
        peso_rsi = optimized_weights.get('rsi', 1.0)
        peso_macd = optimized_weights.get('macd', 1.0)
        peso_sma = optimized_weights.get('sma', 1.0)
        peso_sr = optimized_weights.get('soportes_resistencias', 1.0)
        peso_sharpe = optimized_weights.get('sharpe_ratio', 1.0)
        peso_noticias = optimized_weights.get('noticias', 1.0)
        peso_fear_greed = optimized_weights.get('fear_greed', 1.0)
        motivo.append("🧠 Usando pesos optimizados por aprendizaje automático")
    else:
        # Ajustar pesos según el horizonte
        peso_rsi = 1.0
        peso_macd = 1.0
        peso_sma = 1.0
        peso_sr = 1.0
        peso_sharpe = 1.0
        peso_noticias = 1.0
        peso_fear_greed = 1.0
        
        if horizonte == "1h":
            # Para horizonte muy corto, dar más peso a indicadores de momentum
            peso_rsi = 1.5
            peso_macd = 1.8
            peso_sma = 0.8
            peso_sr = 1.2
            peso_sharpe = 0.5
            motivo.append(f"Horizonte: {horizonte} - Ajuste para trading muy corto plazo")
        elif horizonte == "4h":
            # Para horizonte corto, balance entre momentum y tendencia
            peso_rsi = 1.3
            peso_macd = 1.5
            peso_sma = 1.0
            peso_sr = 1.3
            peso_sharpe = 0.7
            motivo.append(f"Horizonte: {horizonte} - Ajuste para trading corto plazo")
        elif horizonte == "12h":
            # Para horizonte medio-corto
            peso_rsi = 1.2
            peso_macd = 1.3
            peso_sma = 1.1
            peso_sr = 1.2
            peso_sharpe = 0.8
            motivo.append(f"Horizonte: {horizonte} - Ajuste para trading medio-corto plazo")
        elif horizonte == "24h":
            # Para horizonte medio, pesos balanceados
            peso_rsi = 1.0
            peso_macd = 1.0
            peso_sma = 1.0
            peso_sr = 1.0
            peso_sharpe = 1.0
            motivo.append(f"Horizonte: {horizonte} - Ajuste para trading medio plazo")
        elif horizonte == "7d":
            # Para horizonte largo, dar más peso a tendencias y fundamentales
            peso_rsi = 0.8
            peso_macd = 0.7
            peso_sma = 1.5
            peso_sr = 1.3
            peso_sharpe = 1.2
            motivo.append(f"Horizonte: {horizonte} - Ajuste para trading largo plazo")
        elif horizonte == "1mes":
            # Para horizonte muy largo, máximo peso a tendencias
            peso_rsi = 0.5
            peso_macd = 0.5
            peso_sma = 2.0
            peso_sr = 1.5
            peso_sharpe = 1.5
            motivo.append(f"Horizonte: {horizonte} - Ajuste para inversión largo plazo")

    # RSI
    if rsi_value is not None:
        if rsi_value < 30:
            puntaje_total += 2 * peso_rsi
            motivo.append(f"RSI bajo (<30) [peso: {peso_rsi:.1f}]")
        elif rsi_value > 70:
            puntaje_total -= 2 * peso_rsi
            motivo.append(f"RSI alto (>70) [peso: {peso_rsi:.1f}]")
    # MACD
    if macd_val is not None and macd_signal is not None:
        if macd_val > macd_signal:
            puntaje_total += 2 * peso_macd
            motivo.append(f"MACD alcista [peso: {peso_macd:.1f}]")
        elif macd_val < macd_signal:
            puntaje_total -= 2 * peso_macd
            motivo.append(f"MACD bajista [peso: {peso_macd:.1f}]")
    # SMA 7 vs SMA 21
    if sma_7 is not None and sma_21 is not None:
        if sma_7 > sma_21:
            puntaje_total += 1.5 * peso_sma
            motivo.append(f"SMA 7 > SMA 21 [peso: {peso_sma:.1f}]")
        elif sma_7 < sma_21:
            puntaje_total -= 1.5 * peso_sma
            motivo.append(f"SMA 7 < SMA 21 [peso: {peso_sma:.1f}]")
    # Precio cerca de soporte/resistencia
    umbral = 0.005
    cerca_soporte = any(abs(precio_actual - s) / precio_actual < umbral for s in todos_soportes)
    cerca_resistencia = any(abs(precio_actual - r) / precio_actual < umbral for r in todas_resistencias)
    influencia_sr = None
    nivel_sr = None
    if cerca_soporte and rsi_value is not None and macd_val is not None and macd_signal is not None:
        if rsi_value < 35 and macd_val > macd_signal:
            puntaje_total += 2 * peso_sr
            motivo.append(f"Rebote en soporte con confirmación [peso: {peso_sr:.1f}]")
            influencia_sr = "soporte"
            nivel_sr = min(todos_soportes, key=lambda s: abs(precio_actual-s)) if todos_soportes else None
    if cerca_resistencia and rsi_value is not None and macd_val is not None and macd_signal is not None:
        if rsi_value > 65 and macd_val < macd_signal:
            puntaje_total -= 2 * peso_sr
            motivo.append(f"Rechazo en resistencia con agotamiento [peso: {peso_sr:.1f}]")
            influencia_sr = "resistencia"
            nivel_sr = min(todas_resistencias, key=lambda r: abs(precio_actual-r)) if todas_resistencias else None
    # Sharpe ratio
    returns = [(closes[i] - closes[i-1])/closes[i-1] for i in range(1, len(closes))] if len(closes) > 1 else []
    from services.external_data_service import sharpe_ratio as ext_sharpe_ratio
    sharpe = ext_sharpe_ratio(returns)
    if sharpe is not None and sharpe < 0:
        puntaje_total -= 1.5 * peso_sharpe
        motivo.append(f"Sharpe negativo [peso: {peso_sharpe:.1f}]")
    # Fear & Greed
    fg = get_fear_and_greed_index()
    fg_value = None
    try:
        if fg and "value" in fg:
            fg_value = int(fg["value"])
    except Exception:
        fg_value = None
    # Noticias
    news = get_crypto_news()[:5]
    sentimiento_noticias = analizar_sentimiento_noticias(news)
    if sentimiento_noticias["score"] > 0:
        puntaje_total += 1 * peso_noticias
        motivo.append("Noticias positivas")
    elif sentimiento_noticias["score"] < 0:
        puntaje_total -= 1 * peso_noticias
        motivo.append("Noticias negativas")
    # Fear & Greed Index (ajuste sobre recomendación)
    fg_ajuste = 0
    if fg_value is not None:
        if fg_value > 75 and puntaje_total > 3:
            puntaje_total -= 1
            motivo.append("Codicia extrema (FG > 75)")
            fg_ajuste = -1
        elif fg_value < 25 and puntaje_total < -3:
            puntaje_total -= 1
            motivo.append("Miedo extremo (FG < 25)")
            fg_ajuste = -1
    # Recomendación final
    if puntaje_total > 3:
        recomendacion = "Comprar"
    elif puntaje_total < -3:
        recomendacion = "Vender"
    else:
        recomendacion = "Mantener"
    # Indicadores para respuesta
    indicadores = {
        'rsi': round(rsi_value, 2) if rsi_value is not None else None,
        'sma_7': round(sma_7, 4) if sma_7 is not None else None,
        'sma_21': round(sma_21, 4) if sma_21 is not None else None,
        'sma_50': round(sma_50, 4) if sma_50 is not None else None,
        'sma_200': round(sma_200, 4) if sma_200 is not None else None,
        'macd': round(macd_val, 4) if macd_val is not None else None,
        'macd_signal': round(macd_signal, 4) if macd_signal is not None else None,
        'macd_hist': round(macd_hist, 4) if macd_hist is not None else None,
        'bb_upper': round(bb_upper, 4) if bb_upper is not None else None,
        'bb_mid': round(bb_mid, 4) if bb_mid is not None else None,
        'bb_lower': round(bb_lower, 4) if bb_lower is not None else None,
        'obv': round(obv_val, 4) if obv_val is not None else None,
        'vwap': round(vwap_val, 4) if vwap_val is not None else None,
        'sharpe_ratio': round(sharpe, 4) if sharpe is not None else None,
        'fg_index': fg_value,
        'noticias_score': sentimiento_noticias["score"]
    }
    contexto_sr = {
        "influencia": influencia_sr,
        "nivel": nivel_sr,
        "precio": precio_actual,
        "soportes": todos_soportes,
        "resistencias": todas_resistencias
    }
    log_signal(symbol.upper(), precio_actual, indicadores, recomendacion)
    result = {
        "symbol": symbol.upper(),
        "recomendacion": recomendacion,
        "puntaje_total": puntaje_total,
        "motivo": motivo,
        "indicadores": indicadores,
        "soportes": todos_soportes,
        "resistencias": todas_resistencias,
        "contexto_sr": contexto_sr,
        "horizonte": horizonte,
        "pesos_aplicados": {
            "rsi": peso_rsi,
            "macd": peso_macd,
            "sma": peso_sma,
            "soportes_resistencias": peso_sr,
            "sharpe": peso_sharpe
        }
    }
    
    # Guardar en cache
    cache_recommendation(symbol, horizonte, result)
    print(f"💾 Cache miss para {symbol} ({horizonte}) - Guardado en cache")
    
    return result 