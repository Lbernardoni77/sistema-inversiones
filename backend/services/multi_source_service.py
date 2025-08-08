#!/usr/bin/env python3
"""
Servicio de múltiples fuentes de datos para criptomonedas
Usa las prioridades dinámicas configuradas por el benchmark
"""

import httpx
import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta

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

# Configuración de API Keys
COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY', 'f76a0f82-e398-4343-8fa3-edbc78ae73fc')

class MultiSourceService:
    """Servicio que usa múltiples fuentes de datos según prioridades dinámicas"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        # API Keys para nuevas fuentes
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.polygon_key = os.getenv('POLYGON_API_KEY', 'demo')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', 'demo')
        
        # Mapeo de símbolos para diferentes APIs
        self.symbol_mapping = {
            'BTCUSDT': {
                'coingecko': 'bitcoin',
                'coincap': 'bitcoin',
                'cryptocompare': 'BTC',
                'coinpaprika': 'btc-bitcoin',
                'yahoo': 'BTC-USD'
            },
            'ETHUSDT': {
                'coingecko': 'ethereum',
                'coincap': 'ethereum',
                'cryptocompare': 'ETH',
                'coinpaprika': 'eth-ethereum',
                'yahoo': 'ETH-USD'
            },
            'ADAUSDT': {
                'coingecko': 'cardano',
                'coincap': 'cardano',
                'cryptocompare': 'ADA',
                'coinpaprika': 'ada-cardano',
                'yahoo': 'ADA-USD'
            },
            'SOLUSDT': {
                'coingecko': 'solana',
                'coincap': 'solana',
                'cryptocompare': 'SOL',
                'coinpaprika': 'sol-solana',
                'yahoo': 'SOL-USD'
            },
            'MATICUSDT': {
                'coingecko': 'matic-network',
                'coincap': 'matic-network',
                'cryptocompare': 'MATIC',
                'coinpaprika': 'matic-polygon',
                'yahoo': 'MATIC-USD'
            },
            'DOTUSDT': {
                'coingecko': 'polkadot',
                'coincap': 'polkadot',
                'cryptocompare': 'DOT',
                'coinpaprika': 'dot-polkadot',
                'yahoo': 'DOT-USD'
            },
            'SHIBUSDT': {
                'coingecko': 'shiba-inu',
                'coincap': 'shiba-inu',
                'cryptocompare': 'SHIB',
                'coinpaprika': 'shib-shiba-inu',
                'yahoo': 'SHIB-USD'
            },
            'SANDUSDT': {
                'coingecko': 'the-sandbox',
                'coincap': 'the-sandbox',
                'cryptocompare': 'SAND',
                'coinpaprika': 'sand-the-sandbox',
                'yahoo': 'SAND-USD'
            },
            'THETAUSDT': {
                'coingecko': 'theta-token',
                'coincap': 'theta-token',
                'cryptocompare': 'THETA',
                'coinpaprika': 'theta-theta-token',
                'yahoo': 'THETA-USD'
            },
            'MANAUSDT': {
                'coingecko': 'decentraland',
                'coincap': 'decentraland',
                'cryptocompare': 'MANA',
                'coinpaprika': 'mana-decentraland',
                'yahoo': 'MANA-USD'
            }
        }
        
        # Cargar prioridades dinámicas
        self.source_priorities = self.load_source_priorities()
    
    def load_source_priorities(self) -> List[str]:
        """Carga las prioridades de fuentes desde el archivo de configuración"""
        try:
            config_file = 'config/fuentes_priority.json'
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('source_order', [])
            else:
                # Prioridades por defecto si no existe el archivo
                return ['binance', 'coinmarketcap', 'cryptocompare', 'coinpaprika', 'kraken', 'coingecko', 'alpha_vantage', 'polygon', 'finnhub', 'coincap']
        except Exception as e:
            print(f"Error cargando prioridades: {e}")
            return ['binance', 'coinmarketcap', 'cryptocompare', 'coinpaprika', 'kraken', 'coingecko', 'alpha_vantage', 'polygon', 'finnhub', 'coincap']
    
    def get_price_from_source(self, source: str, symbol: str) -> Optional[Dict]:
        """Obtiene precio de una fuente específica"""
        try:
            if source == 'coinmarketcap':
                return self.get_coinmarketcap_price(symbol)
            elif source == 'coinpaprika':
                return self.get_coinpaprika_price(symbol)
            elif source == 'yahoo':
                return self.get_yahoo_price(symbol)
            elif source == 'cryptocompare':
                return self.get_cryptocompare_price(symbol)
            elif source == 'kraken':
                return self.get_kraken_price(symbol)
            elif source == 'coingecko':
                return self.get_coingecko_price(symbol)
            elif source == 'coincap':
                return self.get_coincap_price(symbol)
            elif source == 'alpha_vantage':
                return self.get_alpha_vantage_price(symbol)
            elif source == 'polygon':
                return self.get_polygon_price(symbol)
            elif source == 'finnhub':
                return self.get_finnhub_price(symbol)
            else:
                return None
        except Exception as e:
            print(f"Error obteniendo precio de {source} para {symbol}: {e}")
            return None
    
    def get_price(self, symbol: str, period: str = "1d") -> Dict:
        """Obtiene precio usando múltiples fuentes según prioridades"""
        # Intentar cada fuente en orden de prioridad
        for source in self.source_priorities:
            result = self.get_price_from_source(source, symbol)
            if result and 'error' not in result:
                print(f"✅ Precio obtenido de {source.upper()} para {symbol}")
                return self.process_price_data(symbol, result, period)
        
        # Si todas las fuentes fallan, devolver error
        return {
            "symbol": symbol,
            "price": 0,
            "change_percent": 0,
            "error": "No hay datos disponibles para este ticker",
            "source": "none"
        }
    
    def get_coinmarketcap_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de CoinMarketCap"""
        try:
            clean_symbol = symbol.replace('USDT', '')
            url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={clean_symbol}"
            headers = {**self.headers, 'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY}
            
            with httpx.Client(timeout=10, headers=headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if 'data' not in data or clean_symbol not in data['data']:
                    return {"error": f"No se encontró precio para {symbol}"}
                
                crypto_data = data['data'][clean_symbol]
                quote = crypto_data.get('quote', {}).get('USD', {})
                
                return {
                    "symbol": symbol,
                    "price": quote.get('price', 0),
                    "change_percent": quote.get('percent_change_24h', 0),
                    "source": "coinmarketcap"
                }
        except Exception as e:
            return {"error": f"Error con CoinMarketCap: {str(e)}"}
    
    def get_coinpaprika_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de CoinPaprika"""
        try:
            paprika_id = self.symbol_mapping[symbol]['coinpaprika']
            url = f"https://api.coinpaprika.com/v1/tickers/{paprika_id}"
            
            with httpx.Client(timeout=10, headers=self.headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "symbol": symbol,
                    "price": float(data.get('quotes', {}).get('USD', {}).get('price', 0)),
                    "change_percent": float(data.get('quotes', {}).get('USD', {}).get('percent_change_24h', 0)),
                    "source": "coinpaprika"
                }
        except Exception as e:
            return {"error": f"Error con CoinPaprika: {str(e)}"}
    
    def get_yahoo_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de Yahoo Finance"""
        if not YFINANCE_AVAILABLE:
            return {"error": "Yahoo Finance no está disponible (yfinance no instalado)"}
        
        try:
            yahoo_symbol = self.symbol_mapping[symbol]['yahoo']
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            
            return {
                "symbol": symbol,
                "price": info.get('regularMarketPrice', 0),
                "change_percent": info.get('regularMarketChangePercent', 0),
                "source": "yahoo"
            }
        except Exception as e:
            return {"error": f"Error con Yahoo Finance: {str(e)}"}
    
    def get_cryptocompare_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de CryptoCompare"""
        try:
            cryptocompare_symbol = self.symbol_mapping[symbol]['cryptocompare']
            url = f"https://min-api.cryptocompare.com/data/price?fsym={cryptocompare_symbol}&tsyms=USD"
            
            with httpx.Client(timeout=10, headers=self.headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if 'USD' not in data:
                    return {"error": f"No se encontró precio para {symbol}"}
                
                # Obtener cambio porcentual de CryptoCompare
                change_url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={cryptocompare_symbol}&tsyms=USD"
                change_response = client.get(change_url)
                change_response.raise_for_status()
                change_data = change_response.json()
                
                change_percent = 0
                if 'RAW' in change_data and cryptocompare_symbol in change_data['RAW']:
                    change_percent = change_data['RAW'][cryptocompare_symbol]['USD'].get('CHANGEPCT24HOUR', 0)
                
                return {
                    "symbol": symbol,
                    "price": data['USD'],
                    "change_percent": change_percent,
                    "source": "cryptocompare"
                }
        except Exception as e:
            return {"error": f"Error con CryptoCompare: {str(e)}"}
    
    def get_kraken_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de Kraken"""
        try:
            kraken_symbols = {
                'BTCUSDT': 'XBTUSD',
                'ETHUSDT': 'ETHUSD',
                'ADAUSDT': 'ADAUSD',
                'SOLUSDT': 'SOLUSD',
                'MATICUSDT': 'MATICUSD',
                'DOTUSDT': 'DOTUSD',
                'SHIBUSDT': 'SHIBUSD',
                'SANDUSDT': 'SANDUSD',
                'THETAUSDT': 'THETAUSD',
                'MANAUSDT': 'MANAUSD'
            }
            
            kraken_symbol = kraken_symbols.get(symbol, symbol)
            url = f"https://api.kraken.com/0/public/Ticker?pair={kraken_symbol}"
            
            with httpx.Client(timeout=10, headers=self.headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if 'result' not in data or kraken_symbol not in data['result']:
                    return {"error": f"No se encontró precio para {symbol}"}
                
                ticker_data = data['result'][kraken_symbol]
                return {
                    "symbol": symbol,
                    "price": float(ticker_data['c'][0]),  # Precio actual
                    "change_percent": 0,  # Kraken requiere cálculo adicional
                    "source": "kraken"
                }
        except Exception as e:
            return {"error": f"Error con Kraken: {str(e)}"}
    
    def get_coingecko_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de CoinGecko"""
        try:
            coingecko_id = self.symbol_mapping[symbol]['coingecko']
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd&include_24hr_change=true"
            
            with httpx.Client(timeout=10, headers=self.headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if coingecko_id not in data:
                    return {"error": f"No se encontró precio para {symbol}"}
                
                price_data = data[coingecko_id]
                return {
                    "symbol": symbol,
                    "price": price_data.get('usd', 0),
                    "change_percent": price_data.get('usd_24h_change', 0),
                    "source": "coingecko"
                }
        except Exception as e:
            return {"error": f"Error con CoinGecko: {str(e)}"}
    
    def get_coincap_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de CoinCap"""
        try:
            coincap_id = self.symbol_mapping[symbol]['coincap']
            url = f"https://api.coincap.io/v2/assets/{coincap_id}"
            
            with httpx.Client(timeout=10, headers=self.headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                asset_data = data.get('data', {})
                return {
                    "symbol": symbol,
                    "price": float(asset_data.get('priceUsd', 0)),
                    "change_percent": float(asset_data.get('changePercent24Hr', 0)),
                    "source": "coincap"
                }
        except Exception as e:
            return {"error": f"Error con CoinCap: {str(e)}"}
    
    def get_alpha_vantage_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de Alpha Vantage"""
        if not ALPHA_VANTAGE_AVAILABLE:
            return {"error": "Alpha Vantage no está disponible"}
        
        try:
            # Mapear símbolos para Alpha Vantage
            symbol_mapping = {
                'BTCUSDT': 'BTC',
                'ETHUSDT': 'ETH',
                'ADAUSDT': 'ADA',
                'SOLUSDT': 'SOL',
                'MATICUSDT': 'MATIC',
                'DOTUSDT': 'DOT',
                'SHIBUSDT': 'SHIB',
                'SANDUSDT': 'SAND',
                'THETAUSDT': 'THETA',
                'MANAUSDT': 'MANA'
            }
            
            av_symbol = symbol_mapping.get(symbol, symbol.replace('USDT', ''))
            ts = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
            
            data, meta_data = ts.get_quote_endpoint(symbol=av_symbol)
            
            if data.empty:
                return {"error": f"No se encontró precio para {symbol}"}
            
            return {
                "symbol": symbol,
                "price": float(data['05. price'].iloc[0]),
                "change_percent": float(data['10. change percent'].iloc[0].replace('%', '')),
                "source": "alpha_vantage"
            }
        except Exception as e:
            return {"error": f"Error con Alpha Vantage: {str(e)}"}
    
    def get_polygon_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de Polygon.io"""
        try:
            # Mapear símbolos para Polygon
            symbol_mapping = {
                'BTCUSDT': 'X:BTCUSD',
                'ETHUSDT': 'X:ETHUSD',
                'ADAUSDT': 'X:ADAUSD',
                'SOLUSDT': 'X:SOLUSD',
                'MATICUSDT': 'X:MATICUSD',
                'DOTUSDT': 'X:DOTUSD',
                'SHIBUSDT': 'X:SHIBUSD',
                'SANDUSDT': 'X:SANDUSD',
                'THETAUSDT': 'X:THETAUSD',
                'MANAUSDT': 'X:MANAUSD'
            }
            
            polygon_symbol = symbol_mapping.get(symbol, f"X:{symbol.replace('USDT', 'USD')}")
            url = f"https://api.polygon.io/v2/snapshot/locale/global/markets/crypto/tickers/{polygon_symbol}?apiKey={self.polygon_key}"
            
            with httpx.Client(timeout=10, headers=self.headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if 'results' not in data or not data['results']:
                    return {"error": f"No se encontró precio para {symbol}"}
                
                ticker_data = data['results']
                return {
                    "symbol": symbol,
                    "price": float(ticker_data.get('last', {}).get('p', 0)),
                    "change_percent": 0,  # Polygon requiere cálculo adicional
                    "source": "polygon"
                }
        except Exception as e:
            return {"error": f"Error con Polygon: {str(e)}"}
    
    def get_finnhub_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de Finnhub"""
        try:
            # Mapear símbolos para Finnhub
            symbol_mapping = {
                'BTCUSDT': 'BINANCE:BTCUSDT',
                'ETHUSDT': 'BINANCE:ETHUSDT',
                'ADAUSDT': 'BINANCE:ADAUSDT',
                'SOLUSDT': 'BINANCE:SOLUSDT',
                'MATICUSDT': 'BINANCE:MATICUSDT',
                'DOTUSDT': 'BINANCE:DOTUSDT',
                'SHIBUSDT': 'BINANCE:SHIBUSDT',
                'SANDUSDT': 'BINANCE:SANDUSDT',
                'THETAUSDT': 'BINANCE:THETAUSDT',
                'MANAUSDT': 'BINANCE:MANAUSDT'
            }
            
            finnhub_symbol = symbol_mapping.get(symbol, f"BINANCE:{symbol}")
            url = f"https://finnhub.io/api/v1/quote?symbol={finnhub_symbol}&token={self.finnhub_key}"
            
            with httpx.Client(timeout=10, headers=self.headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if 'c' not in data or data['c'] == 0:
                    return {"error": f"No se encontró precio para {symbol}"}
                
                return {
                    "symbol": symbol,
                    "price": float(data['c']),
                    "change_percent": float(data.get('dp', 0)),
                    "source": "finnhub"
                }
        except Exception as e:
            return {"error": f"Error con Finnhub: {str(e)}"}
    
    def process_price_data(self, symbol: str, data: Dict, period: str = "1d") -> Dict:
        """Procesa los datos de precio para el formato esperado"""
        if 'error' in data:
            return data
        
        price = data.get('price', 0)
        change_percent = data.get('change_percent', 0)
        source = data.get('source', 'unknown')
        
        # Calcular cambio en diferentes períodos
        change_1h = change_percent * 0.04  # Aproximación
        change_24h = change_percent
        change_7d = change_percent * 1.5   # Aproximación
        change_30d = change_percent * 3     # Aproximación
        
        return {
            "symbol": symbol,
            "price": price,
            "change_1h": change_1h,
            "change_24h": change_24h,
            "change_7d": change_7d,
            "change_30d": change_30d,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_alpha_vantage_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> Optional[List[list]]:
        """Obtiene klines de Alpha Vantage"""
        if not ALPHA_VANTAGE_AVAILABLE:
            return None
        
        try:
            # Mapear símbolos para Alpha Vantage
            symbol_mapping = {
                'BTCUSDT': 'BTC',
                'ETHUSDT': 'ETH',
                'ADAUSDT': 'ADA',
                'SOLUSDT': 'SOL',
                'MATICUSDT': 'MATIC',
                'DOTUSDT': 'DOT',
                'SHIBUSDT': 'SHIB',
                'SANDUSDT': 'SAND',
                'THETAUSDT': 'THETA',
                'MANAUSDT': 'MANA'
            }
            
            av_symbol = symbol_mapping.get(symbol, symbol.replace('USDT', ''))
            
            # Mapear intervalos
            interval_mapping = {
                '1m': '1min',
                '5m': '5min',
                '15m': '15min',
                '30m': '30min',
                '1h': '60min',
                '4h': 'daily',
                '1d': 'daily'
            }
            
            av_interval = interval_mapping.get(interval, '60min')
            
            ts = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
            
            if av_interval == 'daily':
                data, meta_data = ts.get_daily(symbol=av_symbol, outputsize='compact')
            else:
                data, meta_data = ts.get_intraday(symbol=av_symbol, interval=av_interval, outputsize='compact')
            
            if data.empty:
                return None
            
            # Convertir a formato de klines [timestamp, open, high, low, close, volume]
            klines = []
            for index, row in data.tail(limit).iterrows():
                kline = [
                    int(index.timestamp() * 1000),  # timestamp en ms
                    float(row['1. open']),
                    float(row['2. high']),
                    float(row['3. low']),
                    float(row['4. close']),
                    float(row['5. volume'])
                ]
                klines.append(kline)
            
            return klines
            
        except Exception as e:
            print(f"❌ Error con Alpha Vantage para klines de {symbol}: {e}")
            return None
    
    def get_polygon_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> Optional[List[list]]:
        """Obtiene klines de Polygon.io"""
        try:
            # Mapear símbolos para Polygon
            symbol_mapping = {
                'BTCUSDT': 'X:BTCUSD',
                'ETHUSDT': 'X:ETHUSD',
                'ADAUSDT': 'X:ADAUSD',
                'SOLUSDT': 'X:SOLUSD',
                'MATICUSDT': 'X:MATICUSD',
                'DOTUSDT': 'X:DOTUSD',
                'SHIBUSDT': 'X:SHIBUSD',
                'SANDUSDT': 'X:SANDUSD',
                'THETAUSDT': 'X:THETAUSD',
                'MANAUSDT': 'X:MANAUSD'
            }
            
            polygon_symbol = symbol_mapping.get(symbol, f"X:{symbol.replace('USDT', 'USD')}")
            
            # Mapear intervalos
            interval_mapping = {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': '60',
                '4h': '240',
                '1d': 'D'
            }
            
            polygon_interval = interval_mapping.get(interval, '60')
            
            # Calcular fechas
            end_date = datetime.now()
            start_date = end_date - timedelta(days=limit)
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{polygon_symbol}/range/{polygon_interval}/minute/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}?adjusted=true&sort=asc&limit={limit}&apiKey={self.polygon_key}"
            
            with httpx.Client(timeout=30, headers=self.headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if 'results' not in data or not data['results']:
                    return None
                
                # Convertir a formato de klines
                klines = []
                for result in data['results']:
                    kline = [
                        result['t'],  # timestamp en ms
                        result['o'],  # open
                        result['h'],  # high
                        result['l'],  # low
                        result['c'],  # close
                        result['v']   # volume
                    ]
                    klines.append(kline)
                
                return klines
                
        except Exception as e:
            print(f"❌ Error con Polygon para klines de {symbol}: {e}")
            return None
    
    def get_finnhub_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> Optional[List[list]]:
        """Obtiene klines de Finnhub"""
        try:
            # Mapear símbolos para Finnhub
            symbol_mapping = {
                'BTCUSDT': 'BINANCE:BTCUSDT',
                'ETHUSDT': 'BINANCE:ETHUSDT',
                'ADAUSDT': 'BINANCE:ADAUSDT',
                'SOLUSDT': 'BINANCE:SOLUSDT',
                'MATICUSDT': 'BINANCE:MATICUSDT',
                'DOTUSDT': 'BINANCE:DOTUSDT',
                'SHIBUSDT': 'BINANCE:SHIBUSDT',
                'SANDUSDT': 'BINANCE:SANDUSDT',
                'THETAUSDT': 'BINANCE:THETAUSDT',
                'MANAUSDT': 'BINANCE:MANAUSDT'
            }
            
            finnhub_symbol = symbol_mapping.get(symbol, f"BINANCE:{symbol}")
            
            # Mapear intervalos
            interval_mapping = {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': '60',
                '4h': '240',
                '1d': 'D'
            }
            
            finnhub_interval = interval_mapping.get(interval, '60')
            
            # Calcular fechas
            end_timestamp = int(datetime.now().timestamp())
            start_timestamp = end_timestamp - (limit * 3600)  # Aproximación para 1h
            
            url = f"https://finnhub.io/api/v1/stock/candle?symbol={finnhub_symbol}&resolution={finnhub_interval}&from={start_timestamp}&to={end_timestamp}&token={self.finnhub_key}"
            
            with httpx.Client(timeout=30, headers=self.headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if data['s'] != 'ok' or not data['t']:
                    return None
                
                # Convertir a formato de klines
                klines = []
                for i in range(len(data['t'])):
                    kline = [
                        data['t'][i] * 1000,  # timestamp en ms
                        data['o'][i],         # open
                        data['h'][i],         # high
                        data['l'][i],         # low
                        data['c'][i],         # close
                        data['v'][i]          # volume
                    ]
                    klines.append(kline)
                
                return klines
                
        except Exception as e:
            print(f"❌ Error con Finnhub para klines de {symbol}: {e}")
            return None
    
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> Optional[List[list]]:
        """Obtiene klines usando múltiples fuentes con fallback"""
        source_priorities = self.load_source_priorities()
        
        for source in source_priorities:
            try:
                klines_data = None
                
                if source == 'binance':
                    continue  # Manejado en binance_service.py
                elif source == 'coingecko':
                    continue  # Manejado en binance_service.py
                elif source == 'alpha_vantage':
                    klines_data = self.get_alpha_vantage_klines(symbol, interval, limit)
                elif source == 'polygon':
                    klines_data = self.get_polygon_klines(symbol, interval, limit)
                elif source == 'finnhub':
                    klines_data = self.get_finnhub_klines(symbol, interval, limit)
                else:
                    continue  # Otras fuentes no tienen klines
                
                if klines_data and len(klines_data) > 0:
                    return klines_data
                    
            except Exception as e:
                print(f"❌ Error con {source} para klines de {symbol}: {e}")
                continue
        
        return None
    
    def close(self):
        """Cierra conexiones HTTP"""
        pass  # httpx.Client se cierra automáticamente con context manager 