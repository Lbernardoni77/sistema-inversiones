#!/usr/bin/env python3
"""
Script de Benchmark para Fuentes de Datos de Criptomonedas
Mide velocidad, tasa de éxito y completitud de múltiples APIs
"""

import httpx
import time
import json
import os
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics
from dataclasses import dataclass, asdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración de API Keys
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', '')  # No requiere API key para endpoints básicos
COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY', 'f76a0f82-e398-4343-8fa3-edbc78ae73fc')
CRYPTOCOMPARE_API_KEY = os.getenv('CRYPTOCOMPARE_API_KEY', '')

# Configuración de email para notificaciones
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'email': os.getenv('NOTIFICATION_EMAIL', ''),
    'password': os.getenv('EMAIL_PASSWORD', '')
}

@dataclass
class BenchmarkResult:
    """Resultado de benchmark para una fuente"""
    source: str
    endpoint: str
    symbol: str
    response_time: float
    success: bool
    error_message: str = ""
    data_completeness: float = 0.0
    timestamp: str = ""

@dataclass
class SourcePerformance:
    """Performance agregada de una fuente"""
    source: str
    avg_response_time: float | str  # Puede ser float o "inf" como string
    success_rate: float
    avg_completeness: float
    total_tests: int
    successful_tests: int

class DataSourceBenchmark:
    """Clase principal para benchmark de fuentes de datos"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'MATICUSDT']
        self.test_endpoints = ['price', 'klines']
        
        # Headers comunes
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        # Mapeo de símbolos para diferentes APIs
        self.symbol_mapping = {
            'BTCUSDT': {
                'coingecko': 'bitcoin',
                'coincap': 'bitcoin',
                'cryptocompare': 'BTC',
                'coinpaprika': 'btc-bitcoin',
                'yahoo': 'BTC-USD',
                'binance': 'BTCUSDT'
            },
            'ETHUSDT': {
                'coingecko': 'ethereum',
                'coincap': 'ethereum',
                'cryptocompare': 'ETH',
                'coinpaprika': 'eth-ethereum',
                'yahoo': 'ETH-USD',
                'binance': 'ETHUSDT'
            },
            'ADAUSDT': {
                'coingecko': 'cardano',
                'coincap': 'cardano',
                'cryptocompare': 'ADA',
                'coinpaprika': 'ada-cardano',
                'yahoo': 'ADA-USD',
                'binance': 'ADAUSDT'
            },
            'SOLUSDT': {
                'coingecko': 'solana',
                'coincap': 'solana',
                'cryptocompare': 'SOL',
                'coinpaprika': 'sol-solana',
                'yahoo': 'SOL-USD',
                'binance': 'SOLUSDT'
            },
            'MATICUSDT': {
                'coingecko': 'matic-network',
                'coincap': 'matic-network',
                'cryptocompare': 'MATIC',
                'coinpaprika': 'matic-polygon',
                'yahoo': 'MATIC-USD',
                'binance': 'MATICUSDT'
            }
        }
    
    def measure_request(self, func, *args, **kwargs) -> Tuple[float, bool, str, float]:
        """Mide el tiempo de respuesta y éxito de una función"""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            response_time = time.time() - start_time
            
            if isinstance(result, dict) and 'error' in result:
                return response_time, False, result['error'], 0.0
            
            # Calcular completitud basada en el tipo de resultado
            completeness = self.calculate_completeness(result)
            return response_time, True, "", completeness
            
        except Exception as e:
            response_time = time.time() - start_time
            return response_time, False, str(e), 0.0
    
    def calculate_completeness(self, data) -> float:
        """Calcula la completitud de los datos (0.0 a 1.0)"""
        if not data:
            return 0.0
        
        if isinstance(data, list):
            # Para klines, verificar que tenga al menos 10 elementos
            return min(1.0, len(data) / 10.0)
        
        if isinstance(data, dict):
            # Para precios, verificar campos requeridos
            required_fields = ['price', 'symbol']
            present_fields = sum(1 for field in required_fields if field in data)
            return present_fields / len(required_fields)
        
        return 0.5  # Valor por defecto

    def test_binance_price(self, symbol: str) -> Dict:
        """Test de precio con Binance"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            
            with httpx.Client(timeout=10, headers=self.headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "symbol": symbol,
                    "price": float(data['price']),
                    "source": "binance"
                }
        except Exception as e:
            return {"error": f"Error con Binance: {str(e)}"}

    def test_binance_klines(self, symbol: str) -> List:
        """Test de klines con Binance"""
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
            
            with httpx.Client(timeout=15, headers=self.headers) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return []
    
    def test_coingecko_price(self, symbol: str) -> Dict:
        """Test de precio con CoinGecko (endpoint gratuito)"""
        coingecko_id = self.symbol_mapping[symbol]['coingecko']
        
        # Usar endpoint gratuito de CoinGecko
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
    
    def test_coingecko_klines(self, symbol: str) -> List:
        """Test de klines con CoinGecko (endpoint gratuito)"""
        coingecko_id = self.symbol_mapping[symbol]['coingecko']
        
        # Usar endpoint gratuito de CoinGecko para datos históricos
        url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart?vs_currency=usd&days=30"
        
        with httpx.Client(timeout=15, headers=self.headers) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Convertir a formato de klines
            prices = data.get('prices', [])
            klines = []
            for timestamp_ms, price in prices:
                # Simular formato de klines [timestamp, open, high, low, close, volume]
                klines.append([timestamp_ms/1000, price, price, price, price, 0])
            
            return klines[:200]  # Limitar a 200 elementos
    
    def test_coinmarketcap_price(self, symbol: str) -> Dict:
        """Test de precio con CoinMarketCap"""
        try:
            # CoinMarketCap usa símbolos estándar
            url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol.replace('USDT', '')}"
            
            headers = {**self.headers, 'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY}
            
            with httpx.Client(timeout=10, headers=headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if 'data' not in data or symbol.replace('USDT', '') not in data['data']:
                    return {"error": f"No se encontró precio para {symbol}"}
                
                crypto_data = data['data'][symbol.replace('USDT', '')]
                quote = crypto_data.get('quote', {}).get('USD', {})
                
                return {
                    "symbol": symbol,
                    "price": quote.get('price', 0),
                    "change_percent": quote.get('percent_change_24h', 0),
                    "source": "coinmarketcap"
                }
        except Exception as e:
            return {"error": f"Error con CoinMarketCap: {str(e)}"}
    
    def test_coincap_price(self, symbol: str) -> Dict:
        """Test de precio con CoinCap (gratuito)"""
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
    
    def test_cryptocompare_price(self, symbol: str) -> Dict:
        """Test de precio con CryptoCompare (endpoint gratuito)"""
        try:
            cryptocompare_symbol = self.symbol_mapping[symbol]['cryptocompare']
            url = f"https://min-api.cryptocompare.com/data/price?fsym={cryptocompare_symbol}&tsyms=USD"
            
            # Usar endpoint gratuito que no requiere API key
            with httpx.Client(timeout=10, headers=self.headers) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if 'USD' not in data:
                    return {"error": f"No se encontró precio para {symbol}"}
                
                return {
                    "symbol": symbol,
                    "price": data['USD'],
                    "change_percent": 0,  # CryptoCompare requiere endpoint adicional para cambio
                    "source": "cryptocompare"
                }
        except Exception as e:
            return {"error": f"Error con CryptoCompare: {str(e)}"}
    
    def test_coinpaprika_price(self, symbol: str) -> Dict:
        """Test de precio con CoinPaprika"""
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
    
    def test_yahoo_price(self, symbol: str) -> Dict:
        """Test de precio con Yahoo Finance"""
        yahoo_symbol = self.symbol_mapping[symbol]['yahoo']
        
        try:
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
    
    def test_kraken_price(self, symbol: str) -> Dict:
        """Test de precio con Kraken"""
        # Kraken usa símbolos diferentes
        kraken_symbols = {
            'BTCUSDT': 'XBTUSD',
            'ETHUSDT': 'ETHUSD',
            'ADAUSDT': 'ADAUSD',
            'SOLUSDT': 'SOLUSD',
            'MATICUSDT': 'MATICUSD'
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
    
    def run_benchmark(self) -> Dict:
        """Ejecuta el benchmark completo"""
        print("🚀 Iniciando benchmark de fuentes de datos...")
        
        # Definir fuentes a testear
        sources = {
            'binance': {
                'price': self.test_binance_price,
                'klines': self.test_binance_klines
            },
            'coinmarketcap': {
                'price': self.test_coinmarketcap_price,
                'klines': None  # CoinMarketCap requiere endpoint adicional para klines
            },
            'yahoo': {
                'price': self.test_yahoo_price,
                'klines': None  # Yahoo no tiene klines directos
            },
            'cryptocompare': {
                'price': self.test_cryptocompare_price,
                'klines': None  # Implementar si es necesario
            },
            'coinpaprika': {
                'price': self.test_coinpaprika_price,
                'klines': None  # Implementar si es necesario
            },
            'kraken': {
                'price': self.test_kraken_price,
                'klines': None  # Implementar si es necesario
            },
            'coincap': {
                'price': self.test_coincap_price,
                'klines': None  # CoinCap no tiene klines directos
            }
        }
        
        # Agregar CoinGecko (gratuito, no requiere API key)
        sources['coingecko'] = {
            'price': self.test_coingecko_price,
            'klines': self.test_coingecko_klines
        }
        
        # Ejecutar tests
        for source_name, source_funcs in sources.items():
            print(f"\n📊 Probando {source_name.upper()}...")
            
            for symbol in self.test_symbols:
                for endpoint, func in source_funcs.items():
                    if func is None:
                        continue
                    
                    print(f"  - {symbol} ({endpoint})...")
                    
                    response_time, success, error_msg, completeness = self.measure_request(func, symbol)
                    
                    result = BenchmarkResult(
                        source=source_name,
                        endpoint=endpoint,
                        symbol=symbol,
                        response_time=response_time,
                        success=success,
                        error_message=error_msg,
                        data_completeness=completeness,
                        timestamp=datetime.now().isoformat()
                    )
                    
                    self.results.append(result)
                    
                    # Delay para evitar rate limiting
                    time.sleep(1)
        
        return self.analyze_results()
    
    def analyze_results(self) -> Dict:
        """Analiza los resultados del benchmark"""
        print("\n📈 Analizando resultados...")
        
        # Agrupar por fuente
        source_results = {}
        for result in self.results:
            if result.source not in source_results:
                source_results[result.source] = []
            source_results[result.source].append(result)
        
        # Calcular métricas por fuente
        performance_data = []
        for source, results in source_results.items():
            if not results:
                continue
            
            response_times = [r.response_time for r in results if r.success]
            success_count = sum(1 for r in results if r.success)
            completeness_scores = [r.data_completeness for r in results if r.success]
            
            # Manejar el caso de tiempo infinito para JSON
            avg_time = statistics.mean(response_times) if response_times else float('inf')
            if avg_time == float('inf'):
                avg_time = "inf"  # Convertir a string para JSON válido
            
            performance = SourcePerformance(
                source=source,
                avg_response_time=avg_time,
                success_rate=success_count / len(results) if results else 0.0,
                avg_completeness=statistics.mean(completeness_scores) if completeness_scores else 0.0,
                total_tests=len(results),
                successful_tests=success_count
            )
            
            performance_data.append(performance)
        
        # Ordenar por score combinado (velocidad + éxito + completitud)
        def calculate_score(perf: SourcePerformance) -> float:
            # Normalizar métricas (menor tiempo = mejor, mayor éxito = mejor)
            # Manejar el caso de tiempo infinito
            if perf.avg_response_time == "inf" or perf.avg_response_time == float('inf'):
                time_score = 0.0  # Puntuación mínima para tiempo infinito
            else:
                time_score = 1.0 / (1.0 + perf.avg_response_time)  # Normalizar tiempo
            
            success_score = perf.success_rate
            completeness_score = perf.avg_completeness
            
            # Peso: 40% velocidad, 40% éxito, 20% completitud
            return (0.4 * time_score) + (0.4 * success_score) + (0.2 * completeness_score)
        
        performance_data.sort(key=calculate_score, reverse=True)
        
        # Crear reporte
        report = {
            'timestamp': datetime.now().isoformat(),
            'performance_ranking': [asdict(perf) for perf in performance_data],
            'detailed_results': [asdict(result) for result in self.results],
            'recommended_order': [perf.source for perf in performance_data]
        }
        
        return report
    
    def save_results(self, report: Dict, filename: str = 'benchmark_results.json'):
        """Guarda los resultados en archivo JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"💾 Resultados guardados en {filename}")
    
    def print_report(self, report: Dict):
        """Imprime el reporte en consola"""
        print("\n" + "="*60)
        print("📊 REPORTE DE BENCHMARK DE FUENTES DE DATOS")
        print("="*60)
        print(f"Fecha: {report['timestamp']}")
        print("\n🏆 RANKING DE PERFORMANCE:")
        print("-" * 60)
        
        for i, perf in enumerate(report['performance_ranking'], 1):
            # Manejar el caso de tiempo infinito
            time_str = perf['avg_response_time'] if perf['avg_response_time'] == "inf" else f"{perf['avg_response_time']:6.2f}s"
            print(f"{i:2d}. {perf['source'].upper():12s} | "
                  f"Tiempo: {time_str} | "
                  f"Éxito: {perf['success_rate']:6.1%} | "
                  f"Completitud: {perf['avg_completeness']:6.1%} | "
                  f"Tests: {perf['successful_tests']}/{perf['total_tests']}")
        
        print("\n🎯 ORDEN RECOMENDADO DE FUENTES:")
        print("-" * 60)
        for i, source in enumerate(report['recommended_order'], 1):
            print(f"{i:2d}. {source}")
        
        print("\n" + "="*60)
    
    def send_notification(self, report: Dict, subject: str = "Benchmark de Fuentes Completado"):
        """Envía notificación por email"""
        if not EMAIL_CONFIG['email'] or not EMAIL_CONFIG['password']:
            print("⚠️  Configuración de email no disponible")
            return
        
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG['email']
            msg['To'] = EMAIL_CONFIG['email']
            msg['Subject'] = subject
            
            # Crear contenido del email
            body = f"""
            <html>
            <body>
                <h2>📊 Benchmark de Fuentes de Datos Completado</h2>
                <p><strong>Fecha:</strong> {report['timestamp']}</p>
                
                <h3>🏆 Top 3 Fuentes:</h3>
                <ol>
            """
            
            for i, perf in enumerate(report['performance_ranking'][:3], 1):
                body += f"""
                    <li><strong>{perf['source'].upper()}</strong><br>
                        Tiempo: {perf['avg_response_time']:.2f}s | 
                        Éxito: {perf['success_rate']:.1%} | 
                        Completitud: {perf['avg_completeness']:.1%}
                    </li>
                """
            
            body += """
                </ol>
                
                <h3>🎯 Orden Recomendado:</h3>
                <ol>
            """
            
            for source in report['recommended_order']:
                body += f"<li>{source}</li>"
            
            body += """
                </ol>
                
                <p><em>Este reporte se genera automáticamente cada 15 días.</em></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Enviar email
            with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
                server.starttls()
                server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
                server.send_message(msg)
            
            print("📧 Notificación enviada por email")
            
        except Exception as e:
            print(f"❌ Error enviando email: {e}")

def main():
    """Función principal"""
    benchmark = DataSourceBenchmark()
    
    # Ejecutar benchmark
    report = benchmark.run_benchmark()
    
    # Guardar resultados
    benchmark.save_results(report)
    
    # Mostrar reporte
    benchmark.print_report(report)
    
    # Enviar notificación
    benchmark.send_notification(report)
    
    print("\n✅ Benchmark completado exitosamente!")

if __name__ == "__main__":
    main()