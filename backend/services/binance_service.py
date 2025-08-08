#!/usr/bin/env python3
"""
Servicio de Binance para obtener datos de criptomonedas
Incluye integración con múltiples fuentes de datos
"""

import httpx
import json
import os
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import numpy as np
import requests
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

# Configuración de API Keys
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')

class BinanceService:
    """Servicio para interactuar con la API de Binance y múltiples fuentes"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        # Cache para evitar llamadas repetidas
        self.price_cache = {}
        self.klines_cache = {}
        self.cache_duration = 30  # segundos
        
    def get_httpx_client(self, use_proxy: bool = False) -> httpx.Client:
        """Crea un cliente HTTPX configurable"""
        if use_proxy:
            proxy = os.getenv('HTTP_PROXY')
            if proxy:
                return httpx.Client(
                    timeout=30,
                    headers=self.headers,
                    proxies=proxy
                )
        
        return httpx.Client(
            timeout=30,
            headers=self.headers
        )
    
    def get_binance_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio actual de Binance"""
        try:
            url = f"{self.base_url}/api/v3/ticker/price?symbol={symbol}"
            
            with self.get_httpx_client() as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "symbol": symbol,
                    "price": float(data['price']),
                    "source": "binance"
                }
        except Exception as e:
            print(f"❌ Error obteniendo precio de Binance para {symbol}: {e}")
            return None
    
    def get_coingecko_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio de CoinGecko como fallback"""
        try:
            # Mapeo de símbolos para CoinGecko
            symbol_mapping = {
                'BTCUSDT': 'bitcoin',
                'ETHUSDT': 'ethereum',
                'ADAUSDT': 'cardano',
                'SOLUSDT': 'solana',
                'MATICUSDT': 'matic-network',
                'DOTUSDT': 'polkadot',
                'SHIBUSDT': 'shiba-inu',
                'SANDUSDT': 'the-sandbox',
                'THETAUSDT': 'theta-token',
                'MANAUSDT': 'decentraland'
            }
            
            coingecko_id = symbol_mapping.get(symbol)
            if not coingecko_id:
                return None
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd&include_24hr_change=true"
            
            with self.get_httpx_client() as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if coingecko_id not in data:
                    return None
                
                price_data = data[coingecko_id]
                return {
                    "symbol": symbol,
                    "price": price_data.get('usd', 0),
                    "change_percent": price_data.get('usd_24h_change', 0),
                    "source": "coingecko"
                }
        except Exception as e:
            print(f"❌ Error obteniendo precio de CoinGecko para {symbol}: {e}")
            return None
    
    def get_multi_source_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio usando múltiples fuentes con fallback"""
        try:
            from services.multi_source_service import MultiSourceService
            multi_source = MultiSourceService()
            
            # Intentar obtener precio de múltiples fuentes
            price_data = multi_source.get_price(symbol)
            
            if price_data and 'error' not in price_data:
                return price_data
            
            # Si falla, intentar Binance directamente
            binance_price = self.get_binance_price(symbol)
            if binance_price:
                return binance_price
            
            # Último recurso: CoinGecko
            return self.get_coingecko_price(symbol)
            
        except Exception as e:
            print(f"❌ Error con múltiples fuentes para {symbol}: {e}")
            # Fallback a Binance
            return self.get_binance_price(symbol)
    
    def get_binance_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> Optional[List[list]]:
        """Obtiene datos de klines de Binance"""
        try:
            url = f"{self.base_url}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
            
            with self.get_httpx_client() as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Convertir a formato estándar [timestamp, open, high, low, close, volume]
                klines = []
                for kline in data:
                    klines.append([
                        int(kline[0]),      # timestamp
                        float(kline[1]),    # open
                        float(kline[2]),    # high
                        float(kline[3]),    # low
                        float(kline[4]),    # close
                        float(kline[5])     # volume
                    ])
                
                return klines
                
        except Exception as e:
            print(f"❌ Error obteniendo klines de Binance para {symbol}: {e}")
            return None
    
    def get_coingecko_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> Optional[List[list]]:
        """Obtiene datos históricos de CoinGecko"""
        try:
            # Mapeo de símbolos para CoinGecko
            symbol_mapping = {
                'BTCUSDT': 'bitcoin',
                'ETHUSDT': 'ethereum',
                'ADAUSDT': 'cardano',
                'SOLUSDT': 'solana',
                'MATICUSDT': 'matic-network',
                'DOTUSDT': 'polkadot',
                'SHIBUSDT': 'shiba-inu',
                'SANDUSDT': 'the-sandbox',
                'THETAUSDT': 'theta-token',
                'MANAUSDT': 'decentraland'
            }
            
            coingecko_id = symbol_mapping.get(symbol)
            if not coingecko_id:
                return None
            
            # Mapear intervalos
            interval_mapping = {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': 'hourly',
                '4h': 'daily',
                '1d': 'daily'
            }
            
            coingecko_interval = interval_mapping.get(interval, 'hourly')
            
            # Calcular días atrás
            days = min(limit, 365)  # CoinGecko tiene límites
            
            url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days={days}&interval={coingecko_interval}"
            
            with self.get_httpx_client() as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if 'prices' not in data or not data['prices']:
                    return None
                
                # Convertir a formato de klines
                klines = []
                prices = data['prices']
                
                for i in range(len(prices)):
                    timestamp = int(prices[i][0])
                    price = float(prices[i][1])
                    
                    # Para CoinGecko solo tenemos precio, no OHLCV completo
                    # Usamos el mismo precio para open, high, low, close
                    kline = [
                        timestamp,
                        price,  # open
                        price,  # high
                        price,  # low
                        price,  # close
                        0       # volume (no disponible)
                    ]
                    klines.append(kline)
                
                # Tomar solo los últimos 'limit' elementos
                return klines[-limit:] if len(klines) > limit else klines
                
        except Exception as e:
            print(f"❌ Error obteniendo klines de CoinGecko para {symbol}: {e}")
            return None
    
    def get_multi_source_klines(self, symbol: str, interval: str = "1h", limit: int = 200) -> List[list]:
        """
        Obtiene datos de klines usando múltiples fuentes según prioridades dinámicas
        """
        try:
            from services.multi_source_service import MultiSourceService
            multi_source = MultiSourceService()
            
            # Cargar prioridades dinámicas
            source_priorities = multi_source.load_source_priorities()
            print(f"🔄 Intentando klines para {symbol} con prioridades: {source_priorities}")
            
            # Intentar cada fuente en orden de prioridad
            for source in source_priorities:
                try:
                    if source == 'binance':
                        klines = self.get_binance_klines(symbol, interval, limit)
                        if klines and len(klines) > 0:
                            print(f"✅ Klines obtenidos de BINANCE para {symbol}")
                            return klines
                    elif source == 'coingecko':
                        klines = self.get_coingecko_klines(symbol, interval, limit)
                        if klines and len(klines) > 0:
                            print(f"✅ Klines obtenidos de COINGECKO para {symbol}")
                            return klines
                    elif source == 'coinmarketcap':
                        # CoinMarketCap no tiene endpoint de klines, saltar
                        continue
                    elif source == 'coinpaprika':
                        # CoinPaprika no tiene endpoint de klines, saltar
                        continue
                    elif source == 'yahoo':
                        # Yahoo Finance no tiene endpoint de klines, saltar
                        continue
                    elif source == 'cryptocompare':
                        # CryptoCompare no tiene endpoint de klines, saltar
                        continue
                    elif source == 'kraken':
                        # Kraken no tiene endpoint de klines, saltar
                        continue
                    elif source == 'coincap':
                        # CoinCap no tiene endpoint de klines, saltar
                        continue
                    elif source == 'alpha_vantage':
                        klines = multi_source.get_alpha_vantage_klines(symbol, interval, limit)
                        if klines and len(klines) > 0:
                            print(f"✅ Klines obtenidos de ALPHA VANTAGE para {symbol}")
                            return klines
                    elif source == 'polygon':
                        klines = multi_source.get_polygon_klines(symbol, interval, limit)
                        if klines and len(klines) > 0:
                            print(f"✅ Klines obtenidos de POLYGON para {symbol}")
                            return klines
                    elif source == 'finnhub':
                        klines = multi_source.get_finnhub_klines(symbol, interval, limit)
                        if klines and len(klines) > 0:
                            print(f"✅ Klines obtenidos de FINNHUB para {symbol}")
                            return klines
                        
                except Exception as e:
                    print(f"❌ Error con {source} para klines de {symbol}: {e}")
                    continue
            
            # Si todas las fuentes fallan, intentar Binance como último recurso
            print(f"⚠️ Todas las fuentes fallaron para klines de {symbol}, intentando Binance como último recurso")
            return self.get_binance_klines(symbol, interval, limit) or []
            
        except Exception as e:
            print(f"❌ Error general con múltiples fuentes para klines de {symbol}: {e}")
            return self.get_binance_klines(symbol, interval, limit) or []
    
    def calculate_technical_indicators(self, klines: List[list]) -> Dict:
        """Calcula indicadores técnicos basados en los klines"""
        if not klines or len(klines) < 20:
            return {}
        
        try:
            # Convertir a DataFrame
            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['close'] = pd.to_numeric(df['close'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            df['volume'] = pd.to_numeric(df['volume'])
            
            # Calcular indicadores
            indicators = {}
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
            
            # MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            indicators['macd'] = float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else 0
            indicators['macd_signal'] = float(signal.iloc[-1]) if not pd.isna(signal.iloc[-1]) else 0
            
            # Bollinger Bands
            sma = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            upper_band = sma + (std * 2)
            lower_band = sma - (std * 2)
            indicators['bb_upper'] = float(upper_band.iloc[-1]) if not pd.isna(upper_band.iloc[-1]) else 0
            indicators['bb_lower'] = float(lower_band.iloc[-1]) if not pd.isna(lower_band.iloc[-1]) else 0
            indicators['bb_middle'] = float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else 0
            
            # Moving Averages
            indicators['sma_20'] = float(df['close'].rolling(window=20).mean().iloc[-1]) if len(df) >= 20 else 0
            indicators['sma_50'] = float(df['close'].rolling(window=50).mean().iloc[-1]) if len(df) >= 50 else 0
            indicators['ema_12'] = float(df['close'].ewm(span=12).mean().iloc[-1]) if len(df) >= 12 else 0
            indicators['ema_26'] = float(df['close'].ewm(span=26).mean().iloc[-1]) if len(df) >= 26 else 0
            
            return indicators
            
        except Exception as e:
            print(f"❌ Error calculando indicadores técnicos: {e}")
            return {}
    
    def get_recommendation(self, symbol: str, interval: str = "1h") -> Dict:
        """Obtiene recomendación basada en análisis técnico"""
        try:
            # Obtener precio actual
            price_data = self.get_multi_source_price(symbol)
            if not price_data or 'error' in price_data:
                return {
                    "symbol": symbol,
                    "recommendation": "NEUTRAL",
                    "confidence": 0,
                    "price": 0,
                    "indicators": {},
                    "error": "No se pudo obtener precio"
                }
            
            current_price = price_data['price']
            
            # Obtener klines usando múltiples fuentes
            klines = self.get_multi_source_klines(symbol, interval, 200)
            if not klines or len(klines) < 20:
                return {
                    "symbol": symbol,
                    "recommendation": "NEUTRAL",
                    "confidence": 0,
                    "price": current_price,
                    "indicators": {},
                    "error": "No se pudieron obtener datos históricos"
                }
            
            # Calcular indicadores técnicos
            indicators = self.calculate_technical_indicators(klines)
            
            # Cargar pesos individuales del ticker
            ticker_weights = self.load_ticker_weights(symbol)
            
            # Calcular recomendación
            recommendation = self.calculate_recommendation(indicators, ticker_weights)
            
            return {
                "symbol": symbol,
                "recommendation": recommendation['signal'],
                "confidence": recommendation['confidence'],
                "price": current_price,
                "indicators": indicators,
                "source": price_data.get('source', 'unknown'),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo recomendación para {symbol}: {e}")
            return {
                "symbol": symbol,
                "recommendation": "NEUTRAL",
                "confidence": 0,
                "price": 0,
                "indicators": {},
                "error": str(e)
            }
    
    def load_ticker_weights(self, symbol: str) -> Dict:
        """Carga pesos específicos para un ticker"""
        try:
            weights_file = f'config/weights_{symbol.lower()}.json'
            if os.path.exists(weights_file):
                with open(weights_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Pesos por defecto
                return {
                    "rsi_weight": 0.2,
                    "macd_weight": 0.3,
                    "bb_weight": 0.2,
                    "ma_weight": 0.3
                }
        except Exception as e:
            print(f"Error cargando pesos para {symbol}: {e}")
            return {
                "rsi_weight": 0.2,
                "macd_weight": 0.3,
                "bb_weight": 0.2,
                "ma_weight": 0.3
            }
    
    def calculate_recommendation(self, indicators: Dict, weights: Dict) -> Dict:
        """Calcula la recomendación basada en indicadores y pesos"""
        try:
            score = 0
            total_weight = 0
            
            # RSI
            rsi = indicators.get('rsi', 50)
            if rsi < 30:
                score += weights.get('rsi_weight', 0.2) * 1  # Compra
            elif rsi > 70:
                score += weights.get('rsi_weight', 0.2) * -1  # Venta
            total_weight += weights.get('rsi_weight', 0.2)
            
            # MACD
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            if macd > macd_signal:
                score += weights.get('macd_weight', 0.3) * 1  # Compra
            else:
                score += weights.get('macd_weight', 0.3) * -1  # Venta
            total_weight += weights.get('macd_weight', 0.3)
            
            # Bollinger Bands
            current_price = indicators.get('close', 0)
            bb_upper = indicators.get('bb_upper', 0)
            bb_lower = indicators.get('bb_lower', 0)
            if current_price < bb_lower:
                score += weights.get('bb_weight', 0.2) * 1  # Compra
            elif current_price > bb_upper:
                score += weights.get('bb_weight', 0.2) * -1  # Venta
            total_weight += weights.get('bb_weight', 0.2)
            
            # Moving Averages
            sma_20 = indicators.get('sma_20', 0)
            sma_50 = indicators.get('sma_50', 0)
            if sma_20 > sma_50:
                score += weights.get('ma_weight', 0.3) * 1  # Compra
            else:
                score += weights.get('ma_weight', 0.3) * -1  # Venta
            total_weight += weights.get('ma_weight', 0.3)
            
            # Normalizar score
            if total_weight > 0:
                normalized_score = score / total_weight
            else:
                normalized_score = 0
            
            # Determinar señal
            if normalized_score > 0.3:
                signal = "COMPRAR"
                confidence = min(abs(normalized_score) * 100, 100)
            elif normalized_score < -0.3:
                signal = "VENDER"
                confidence = min(abs(normalized_score) * 100, 100)
            else:
                signal = "NEUTRAL"
                confidence = 50
            
            return {
                "signal": signal,
                "confidence": round(confidence, 2),
                "score": round(normalized_score, 4)
            }
            
        except Exception as e:
            print(f"Error calculando recomendación: {e}")
            return {
                "signal": "NEUTRAL",
                "confidence": 0,
                "score": 0
            } 

    def calculate_percentage_change(self, symbol: str, period: str = '1d') -> Optional[float]:
        """
        Calcular el porcentaje de cambio basado en datos históricos
        
        Args:
            symbol: Símbolo del ticker (ej: 'BTCUSDT')
            period: Período para el cálculo ('1d', '1mo', '1y', 'all')
        
        Returns:
            Porcentaje de cambio como float (ej: -2.5 para -2.5%)
        """
        try:
            # Obtener precio actual
            current_price_data = self.get_binance_price(symbol)
            if not current_price_data:
                return None
            
            current_price = current_price_data['price']
            
            # Determinar el intervalo y límite basado en el período
            interval_map = {
                '1d': ('1d', 2),      # 2 días para calcular vs día anterior
                '1mo': ('1d', 32),     # 32 días para calcular vs mes anterior
                '1y': ('1d', 366),     # 366 días para calcular vs año anterior
                'all': ('1d', 1000)    # Máximo histórico disponible
            }
            
            interval, limit = interval_map.get(period, ('1d', 2))
            
            # Obtener datos históricos
            klines = self.get_binance_klines(symbol, interval, limit)
            if not klines or len(klines) < 2:
                logger.error(f"No hay suficientes datos históricos para {symbol}")
                return None
            
            # Encontrar el precio de referencia según el período
            reference_price = None
            
            if period == '1d':
                # Precio de cierre del día anterior (índice 4 es close)
                reference_price = klines[-2][4]
            elif period == '1mo':
                # Precio de cierre hace ~30 días
                if len(klines) >= 30:
                    reference_price = klines[-30][4]
                else:
                    reference_price = klines[0][4]  # Primer dato disponible
            elif period == '1y':
                # Precio de cierre hace ~365 días
                if len(klines) >= 365:
                    reference_price = klines[-365][4]
                else:
                    reference_price = klines[0][4]  # Primer dato disponible
            elif period == 'all':
                # Precio inicial histórico
                reference_price = klines[0][4]
            
            if reference_price is None or reference_price == 0:
                logger.error(f"No se pudo obtener precio de referencia para {symbol}")
                return None
            
            # Calcular porcentaje de cambio
            percentage_change = ((current_price - reference_price) / reference_price) * 100
            
            logger.info(f"Calculado cambio para {symbol}: actual={current_price}, referencia={reference_price}, cambio={percentage_change:.2f}%")
            
            return round(percentage_change, 2)
            
        except Exception as e:
            logger.error(f"Error calculando porcentaje de cambio para {symbol}: {e}")
            return None 