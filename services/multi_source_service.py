# Import opcional de yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️ yfinance no está disponible, Yahoo Finance será omitido")

# Import opcional de alpha_vantage
try:
    from alpha_vantage.timeseries import TimeSeries
    ALPHA_VANTAGE_AVAILABLE = True
except ImportError:
    ALPHA_VANTAGE_AVAILABLE = False
    print("⚠️ alpha_vantage no está disponible, Alpha Vantage será omitido")

import os
import time
import requests
import httpx
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import json

class MultiSourceService:
    def __init__(self):
        self.session = requests.Session()
        self.httpx_client = httpx.Client(timeout=10.0)
        
        # API Keys (opcionales)
        self.coinmarketcap_key = os.getenv('COINMARKETCAP_API_KEY', 'f76a0f82-e398-4343-8fa3-edbc78ae73fc')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')  # Usar 'demo' para pruebas
        self.polygon_key = os.getenv('POLYGON_API_KEY', 'demo')  # Usar 'demo' para pruebas
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', 'demo')  # Usar 'demo' para pruebas
        
        # Cache simple
        self.price_cache = {}
        self.cache_duration = 60  # 1 minuto
        
    def get_httpx_client(self):
        """Retorna cliente HTTP configurado"""
        return self.httpx_client

    def get_coinmarketcap_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de CoinMarketCap"""
        try:
            # Convertir símbolo a formato CoinMarketCap
            symbol_clean = symbol.replace('USDT', '').replace('USD', '')
            
            url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
            headers = {
                'X-CMC_PRO_API_KEY': self.coinmarketcap_key,
                'Accept': 'application/json'
            }
            params = {
                'symbol': symbol_clean,
                'convert': 'USD'
            }
            
            response = self.httpx_client.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and symbol_clean in data['data']:
                    quote = data['data'][symbol_clean]['quote']['USD']
                    return {
                        'price': quote['price'],
                        'change_24h': quote.get('percent_change_24h', 0),
                        'volume_24h': quote.get('volume_24h', 0),
                        'market_cap': quote.get('market_cap', 0),
                        'source': 'coinmarketcap',
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                print(f"❌ CoinMarketCap error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error CoinMarketCap para {symbol}: {e}")
            
        return None

    def get_coinpaprika_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de CoinPaprika"""
        try:
            # Convertir símbolo a formato CoinPaprika
            symbol_clean = symbol.replace('USDT', '-usdt').replace('USD', '-usd')
            
            url = f"https://api.coinpaprika.com/v1/tickers/{symbol_clean}"
            response = self.httpx_client.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'price': float(data['quotes']['USD']['price']),
                    'change_24h': float(data['quotes']['USD']['percent_change_24h']),
                    'volume_24h': float(data['quotes']['USD']['volume_24h']),
                    'market_cap': float(data['quotes']['USD']['market_cap']),
                    'source': 'coinpaprika',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print(f"❌ CoinPaprika error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error CoinPaprika para {symbol}: {e}")
            
        return None

    def get_yahoo_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de Yahoo Finance"""
        if not YFINANCE_AVAILABLE:
            return {"error": "Yahoo Finance no está disponible (yfinance no instalado)"}
            
        try:
            # Convertir símbolo a formato Yahoo Finance
            symbol_clean = symbol.replace('USDT', '-USD').replace('USD', '-USD')
            
            ticker = yf.Ticker(symbol_clean)
            info = ticker.info
            
            if 'regularMarketPrice' in info and info['regularMarketPrice']:
                return {
                    'price': float(info['regularMarketPrice']),
                    'change_24h': float(info.get('regularMarketChangePercent', 0)),
                    'volume_24h': float(info.get('volume', 0)),
                    'market_cap': float(info.get('marketCap', 0)),
                    'source': 'yahoo',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print(f"❌ Yahoo Finance: No se encontró precio para {symbol}")
                
        except Exception as e:
            print(f"❌ Error Yahoo Finance para {symbol}: {e}")
            
        return None

    def get_cryptocompare_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de CryptoCompare"""
        try:
            # Convertir símbolo a formato CryptoCompare
            symbol_clean = symbol.replace('USDT', '').replace('USD', '')
            
            url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol_clean}&tsyms=USD"
            response = self.httpx_client.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'USD' in data:
                    # Obtener datos adicionales
                    url_extra = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbol_clean}&tsyms=USD"
                    response_extra = self.httpx_client.get(url_extra, timeout=10)
                    
                    change_24h = 0
                    volume_24h = 0
                    market_cap = 0
                    
                    if response_extra.status_code == 200:
                        data_extra = response_extra.json()
                        if 'RAW' in data_extra and symbol_clean in data_extra['RAW']:
                            raw_data = data_extra['RAW'][symbol_clean]['USD']
                            change_24h = raw_data.get('CHANGEPCT24HOUR', 0)
                            volume_24h = raw_data.get('VOLUME24HOUR', 0)
                            market_cap = raw_data.get('MKTCAP', 0)
                    
                    return {
                        'price': float(data['USD']),
                        'change_24h': float(change_24h),
                        'volume_24h': float(volume_24h),
                        'market_cap': float(market_cap),
                        'source': 'cryptocompare',
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                print(f"❌ CryptoCompare error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error CryptoCompare para {symbol}: {e}")
            
        return None

    def get_kraken_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de Kraken"""
        try:
            # Convertir símbolo a formato Kraken
            symbol_clean = symbol.replace('USDT', 'USD').replace('USD', 'USD')
            
            url = f"https://api.kraken.com/0/public/Ticker?pair={symbol_clean}"
            response = self.httpx_client.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and symbol_clean in data['result']:
                    ticker_data = data['result'][symbol_clean]
                    price = float(ticker_data['c'][0])  # Precio actual
                    change_24h = float(ticker_data['p'][1]) - float(ticker_data['p'][0])  # Diferencia 24h
                    volume_24h = float(ticker_data['v'][1])  # Volumen 24h
                    
                    return {
                        'price': price,
                        'change_24h': change_24h,
                        'volume_24h': volume_24h,
                        'market_cap': 0,  # Kraken no proporciona market cap
                        'source': 'kraken',
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                print(f"❌ Kraken error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error Kraken para {symbol}: {e}")
            
        return None

    def get_coingecko_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de CoinGecko (gratuito)"""
        try:
            # Convertir símbolo a formato CoinGecko
            symbol_clean = symbol.replace('USDT', '').replace('USD', '').lower()
            
            # Primero obtener la lista de monedas para encontrar el ID
            url_coins = "https://api.coingecko.com/api/v3/coins/list"
            response_coins = self.httpx_client.get(url_coins, timeout=10)
            
            if response_coins.status_code == 200:
                coins_data = response_coins.json()
                coin_id = None
                
                for coin in coins_data:
                    if coin['symbol'].lower() == symbol_clean:
                        coin_id = coin['id']
                        break
                
                if coin_id:
                    # Obtener datos de la moneda
                    url_price = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                    response_price = self.httpx_client.get(url_price, timeout=10)
                    
                    if response_price.status_code == 200:
                        data = response_price.json()
                        market_data = data['market_data']
                        
                        return {
                            'price': float(market_data['current_price']['usd']),
                            'change_24h': float(market_data['price_change_percentage_24h']),
                            'volume_24h': float(market_data['total_volume']['usd']),
                            'market_cap': float(market_data['market_cap']['usd']),
                            'source': 'coingecko',
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        print(f"❌ CoinGecko error {response_price.status_code}: {response_price.text}")
                else:
                    print(f"❌ CoinGecko: No se encontró ID para {symbol}")
            else:
                print(f"❌ CoinGecko error {response_coins.status_code}: {response_coins.text}")
                
        except Exception as e:
            print(f"❌ Error CoinGecko para {symbol}: {e}")
            
        return None

    def get_coincap_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de CoinCap"""
        try:
            # Convertir símbolo a formato CoinCap
            symbol_clean = symbol.replace('USDT', '').replace('USD', '')
            
            url = f"https://api.coincap.io/v2/assets/{symbol_clean}"
            response = self.httpx_client.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    asset_data = data['data']
                    return {
                        'price': float(asset_data['priceUsd']),
                        'change_24h': float(asset_data['changePercent24Hr']),
                        'volume_24h': float(asset_data['volumeUsd24Hr']),
                        'market_cap': float(asset_data['marketCapUsd']),
                        'source': 'coincap',
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                print(f"❌ CoinCap error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error CoinCap para {symbol}: {e}")
            
        return None

    def get_alpha_vantage_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de Alpha Vantage"""
        if not ALPHA_VANTAGE_AVAILABLE:
            return {"error": "Alpha Vantage no está disponible (alpha_vantage no instalado)"}
            
        try:
            # Convertir símbolo a formato Alpha Vantage
            symbol_clean = symbol.replace('USDT', '').replace('USD', '')
            
            ts = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
            data, meta_data = ts.get_quote_endpoint(symbol_clean)
            
            if not data.empty:
                return {
                    'price': float(data['05. price'].iloc[0]),
                    'change_24h': float(data['09. change'].iloc[0]),
                    'volume_24h': float(data['06. volume'].iloc[0]),
                    'market_cap': 0,  # Alpha Vantage no proporciona market cap
                    'source': 'alpha_vantage',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print(f"❌ Alpha Vantage: No se encontró precio para {symbol}")
                
        except Exception as e:
            print(f"❌ Error Alpha Vantage para {symbol}: {e}")
            
        return None

    def get_polygon_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de Polygon.io"""
        try:
            # Convertir símbolo a formato Polygon
            symbol_clean = symbol.replace('USDT', '').replace('USD', '')
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol_clean}/prev?adjusted=true&apiKey={self.polygon_key}"
            response = self.httpx_client.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    result = data['results'][0]
                    return {
                        'price': float(result['c']),  # Precio de cierre
                        'change_24h': float(result['c']) - float(result['o']),  # Cambio
                        'volume_24h': float(result['v']),  # Volumen
                        'market_cap': 0,  # Polygon no proporciona market cap
                        'source': 'polygon',
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                print(f"❌ Polygon error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error Polygon para {symbol}: {e}")
            
        return None

    def get_finnhub_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de Finnhub"""
        try:
            # Convertir símbolo a formato Finnhub
            symbol_clean = symbol.replace('USDT', '').replace('USD', '')
            
            url = f"https://finnhub.io/api/v1/quote?symbol={symbol_clean}&token={self.finnhub_key}"
            response = self.httpx_client.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'c' in data and data['c'] > 0:
                    return {
                        'price': float(data['c']),  # Precio actual
                        'change_24h': float(data['d']),  # Cambio
                        'volume_24h': 0,  # Finnhub no proporciona volumen en quote
                        'market_cap': 0,  # Finnhub no proporciona market cap
                        'source': 'finnhub',
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                print(f"❌ Finnhub error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error Finnhub para {symbol}: {e}")
            
        return None

    # NUEVAS FUNCIONES PARA KLINES
    def get_alpha_vantage_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> Optional[List[list]]:
        """Obtiene klines de Alpha Vantage"""
        if not ALPHA_VANTAGE_AVAILABLE:
            return None
            
        try:
            # Convertir símbolo a formato Alpha Vantage
            symbol_clean = symbol.replace('USDT', '').replace('USD', '')
            
            # Convertir intervalo
            interval_map = {
                "1m": "1min",
                "5m": "5min", 
                "15m": "15min",
                "30m": "30min",
                "1h": "60min",
                "4h": "daily",
                "1d": "daily"
            }
            
            ts = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
            
            if interval in ["1m", "5m", "15m", "30m", "1h"]:
                data, meta_data = ts.get_intraday(symbol_clean, interval_map[interval], outputsize='compact')
            else:
                data, meta_data = ts.get_daily(symbol_clean, outputsize='compact')
            
            if not data.empty:
                klines = []
                for index, row in data.head(limit).iterrows():
                    klines.append([
                        int(index.timestamp() * 1000),  # Timestamp en ms
                        float(row['1. open']),
                        float(row['2. high']),
                        float(row['3. low']),
                        float(row['4. close']),
                        float(row['5. volume'])
                    ])
                return klines
                
        except Exception as e:
            print(f"❌ Error Alpha Vantage klines para {symbol}: {e}")
            
        return None

    def get_polygon_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> Optional[List[list]]:
        """Obtiene klines de Polygon.io"""
        try:
            # Convertir símbolo a formato Polygon
            symbol_clean = symbol.replace('USDT', '').replace('USD', '')
            
            # Convertir intervalo
            interval_map = {
                "1m": "1",
                "5m": "5", 
                "15m": "15",
                "30m": "30",
                "1h": "60",
                "4h": "240",
                "1d": "D"
            }
            
            multiplier = interval_map.get(interval, "60")
            timespan = "minute" if interval != "1d" else "day"
            
            # Calcular fechas
            end_date = datetime.now()
            start_date = end_date - timedelta(days=limit)
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol_clean}/range/{multiplier}/{timespan}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}?adjusted=true&sort=asc&limit={limit}&apiKey={self.polygon_key}"
            
            response = self.httpx_client.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data:
                    klines = []
                    for result in data['results'][:limit]:
                        klines.append([
                            int(result['t']),  # Timestamp
                            float(result['o']),  # Open
                            float(result['h']),  # High
                            float(result['l']),  # Low
                            float(result['c']),  # Close
                            float(result['v'])   # Volume
                        ])
                    return klines
            else:
                print(f"❌ Polygon klines error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error Polygon klines para {symbol}: {e}")
            
        return None

    def get_finnhub_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> Optional[List[list]]:
        """Obtiene klines de Finnhub"""
        try:
            # Convertir símbolo a formato Finnhub
            symbol_clean = symbol.replace('USDT', '').replace('USD', '')
            
            # Convertir intervalo
            interval_map = {
                "1m": "1",
                "5m": "5", 
                "15m": "15",
                "30m": "30",
                "1h": "60",
                "4h": "240",
                "1d": "D"
            }
            
            resolution = interval_map.get(interval, "60")
            
            # Calcular fechas
            end_date = int(datetime.now().timestamp())
            start_date = int((datetime.now() - timedelta(days=limit)).timestamp())
            
            url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol_clean}&resolution={resolution}&from={start_date}&to={end_date}&token={self.finnhub_key}"
            
            response = self.httpx_client.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data['s'] == 'ok' and len(data['t']) > 0:
                    klines = []
                    for i in range(min(len(data['t']), limit)):
                        klines.append([
                            int(data['t'][i] * 1000),  # Timestamp en ms
                            float(data['o'][i]),  # Open
                            float(data['h'][i]),  # High
                            float(data['l'][i]),  # Low
                            float(data['c'][i]),  # Close
                            float(data['v'][i])   # Volume
                        ])
                    return klines
            else:
                print(f"❌ Finnhub klines error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error Finnhub klines para {symbol}: {e}")
            
        return None

    def get_price(self, symbol: str, period: str = "1d") -> Dict:
        """Obtiene precio usando múltiples fuentes con fallback"""
        # Verificar cache
        cache_key = f"{symbol}_{period}"
        if cache_key in self.price_cache:
            cached_data = self.price_cache[cache_key]
            if (datetime.now() - cached_data['timestamp']).seconds < self.cache_duration:
                return cached_data['data']
        
        # Cargar prioridades dinámicas
        source_priorities = self.load_source_priorities()
        
        # Intentar cada fuente en orden de prioridad
        for source in source_priorities:
            try:
                price_data = None
                
                if source == 'coinmarketcap':
                    price_data = self.get_coinmarketcap_price(symbol)
                elif source == 'coinpaprika':
                    price_data = self.get_coinpaprika_price(symbol)
                elif source == 'yahoo':
                    price_data = self.get_yahoo_price(symbol)
                elif source == 'cryptocompare':
                    price_data = self.get_cryptocompare_price(symbol)
                elif source == 'kraken':
                    price_data = self.get_kraken_price(symbol)
                elif source == 'binance':
                    # Binance se maneja en binance_service.py
                    continue
                elif source == 'coingecko':
                    price_data = self.get_coingecko_price(symbol)
                elif source == 'coincap':
                    price_data = self.get_coincap_price(symbol)
                elif source == 'alpha_vantage':
                    price_data = self.get_alpha_vantage_price(symbol)
                elif source == 'polygon':
                    price_data = self.get_polygon_price(symbol)
                elif source == 'finnhub':
                    price_data = self.get_finnhub_price(symbol)
                
                if price_data and 'price' in price_data and price_data['price'] > 0:
                    # Guardar en cache
                    self.price_cache[cache_key] = {
                        'data': price_data,
                        'timestamp': datetime.now()
                    }
                    return price_data
                    
            except Exception as e:
                print(f"❌ Error con {source} para {symbol}: {e}")
                continue
        
        # Si todas las fuentes fallan
        return {
            'error': f'No se pudo obtener precio para {symbol} de ninguna fuente',
            'price': None,
            'source': 'none',
            'timestamp': datetime.now().isoformat()
        }

    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> Optional[List[list]]:
        """Obtiene klines usando múltiples fuentes con fallback"""
        # Cargar prioridades dinámicas
        source_priorities = self.load_source_priorities()
        
        # Intentar cada fuente en orden de prioridad
        for source in source_priorities:
            try:
                klines_data = None
                
                if source == 'binance':
                    # Binance se maneja en binance_service.py
                    continue
                elif source == 'coingecko':
                    # CoinGecko se maneja en binance_service.py
                    continue
                elif source == 'alpha_vantage':
                    klines_data = self.get_alpha_vantage_klines(symbol, interval, limit)
                elif source == 'polygon':
                    klines_data = self.get_polygon_klines(symbol, interval, limit)
                elif source == 'finnhub':
                    klines_data = self.get_finnhub_klines(symbol, interval, limit)
                else:
                    # Otras fuentes no tienen klines
                    continue
                
                if klines_data and len(klines_data) > 0:
                    return klines_data
                    
            except Exception as e:
                print(f"❌ Error con {source} para klines de {symbol}: {e}")
                continue
        
        # Si todas las fuentes fallan
        return None

    def load_source_priorities(self) -> List[str]:
        """Carga las prioridades de fuentes desde el archivo de configuración"""
        try:
            config_path = "config/fuentes_priority.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('source_order', [])
            else:
                print("⚠️ Archivo de prioridades no encontrado, usando orden por defecto")
                return ['coinmarketcap', 'coinpaprika', 'yahoo', 'cryptocompare', 'kraken', 'binance', 'coingecko', 'coincap']
        except Exception as e:
            print(f"❌ Error cargando prioridades: {e}")
            return ['coinmarketcap', 'coinpaprika', 'yahoo', 'cryptocompare', 'kraken', 'binance', 'coingecko', 'coincap']

    def close(self):
        """Cierra las conexiones"""
        if hasattr(self, 'httpx_client'):
            self.httpx_client.close()
        if hasattr(self, 'session'):
            self.session.close()
