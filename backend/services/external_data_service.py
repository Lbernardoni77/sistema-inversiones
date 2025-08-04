import httpx
from typing import Optional, List
import math
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Índice de Miedo y Codicia (fuente: alternative.me)
def get_fear_and_greed_index() -> Optional[dict]:
    try:
        url = "https://api.alternative.me/fng/"
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data and "data" in data and len(data["data"]) > 0:
            return data["data"][0]
        return None
    except Exception as e:
        return {"error": str(e)}

# 2. Noticias cripto (NewsAPI)
def get_crypto_news() -> List[dict]:
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return [{"error": "No se encontró la clave NEWSAPI_KEY en el .env"}]
    try:
        url = (
            "https://newsapi.org/v2/everything?q=cryptocurrency%20OR%20bitcoin%20OR%20ethereum%20OR%20blockchain&language=es&sortBy=publishedAt&pageSize=5"
        )
        headers = {"Authorization": api_key}
        response = httpx.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except Exception as e:
        return [{"error": str(e)}]

# 3. Estructura para análisis fundamental (simulado/demo)
def get_fundamental_data(symbol: str) -> dict:
    # CoinGecko usa ids, no tickers. Mapeo simple para BTC y ETH.
    coingecko_ids = {"BTCUSDT": "bitcoin", "ETHUSDT": "ethereum"}
    coin_id = coingecko_ids.get(symbol.upper(), None)
    if not coin_id:
        return {"error": "Solo disponible para BTCUSDT y ETHUSDT en demo"}
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "nombre": data.get("name"),
            "descripcion": data.get("description", {}).get("es") or data.get("description", {}).get("en"),
            "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
            "volumen_24h": data.get("market_data", {}).get("total_volume", {}).get("usd"),
            "supply_circulante": data.get("market_data", {}).get("circulating_supply"),
            "supply_total": data.get("market_data", {}).get("total_supply"),
            "cambio_24h": data.get("market_data", {}).get("price_change_percentage_24h"),
            "web": data.get("links", {}).get("homepage", [None])[0]
        }
    except Exception as e:
        return {"error": str(e)}

# 4. Estructura para métricas on-chain (simulado/demo)
def get_onchain_data(symbol: str) -> dict:
    # Blockchair solo para BTC y ETH demo
    blockchair_ids = {"BTCUSDT": "bitcoin", "ETHUSDT": "ethereum"}
    chain = blockchair_ids.get(symbol.upper(), None)
    if not chain:
        return {"error": "Solo disponible para BTCUSDT y ETHUSDT en demo"}
    try:
        url = f"https://api.blockchair.com/{chain}/stats"
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        data = json_data.get("data", {}).get("stats", {})
        # Extraer los campos aunque sean cero
        direcciones = data.get("active_addresses_24h", 0)
        transacciones = data.get("transactions_24h", 0)
        hashrate = data.get("hashrate_24h", 0)
        fees = data.get("average_transaction_fee_usd", 0)
        # Verificar si todos los campos clave son cero
        if direcciones == 0 and transacciones == 0 and hashrate == 0 and fees == 0:
            return {
                "direcciones_activas_24h": direcciones,
                "transacciones_24h": transacciones,
                "hashrate": hashrate,
                "fees_usd": fees,
                "mensaje": "Blockchair no reporta datos on-chain para este ticker en este momento"
            }
        return {
            "direcciones_activas_24h": direcciones,
            "transacciones_24h": transacciones,
            "hashrate": hashrate,
            "fees_usd": fees
        }
    except Exception as e:
        return {"error": str(e)}

# 5. Ratio Sharpe (usando precios históricos y un risk-free rate fijo)
def sharpe_ratio(returns: List[float], risk_free_rate: float = 0.01) -> Optional[float]:
    if not returns or len(returns) < 2:
        return None
    avg_return = sum(returns) / len(returns)
    std_return = math.sqrt(sum([(r - avg_return) ** 2 for r in returns]) / (len(returns) - 1))
    if std_return == 0:
        return None
    return (avg_return - risk_free_rate) / std_return

# 6. Correlación con otro activo (por ejemplo, BTC vs Nasdaq)
def correlation(asset1: List[float], asset2: List[float]) -> Optional[float]:
    if not asset1 or not asset2 or len(asset1) != len(asset2):
        return None
    mean1 = sum(asset1) / len(asset1)
    mean2 = sum(asset2) / len(asset2)
    num = sum((a - mean1) * (b - mean2) for a, b in zip(asset1, asset2))
    den1 = math.sqrt(sum((a - mean1) ** 2 for a in asset1))
    den2 = math.sqrt(sum((b - mean2) ** 2 for b in asset2))
    if den1 == 0 or den2 == 0:
        return None
    return num / (den1 * den2)

def analizar_sentimiento_noticias(noticias: List[dict]) -> dict:
    positivas = [
        "adopción", "inversión", "récord", "máximo", "institucional", "alianza", "integración", "crecimiento", "soporte", "ETF", "aprobación", "expansión", "innovación", "actualización", "partnership"
    ]
    negativas = [
        "hackeo", "caída", "prohibición", "regulación", "multa", "demanda", "fraude", "scam", "colapso", "cierre", "restricción", "sanción", "pérdida", "bancarrota", "bug", "vulnerabilidad"
    ]
    score = 0
    positivos = []
    negativos = []
    for noticia in noticias:
        titulo = noticia.get("titulo") or noticia.get("title") or ""
        titulo_lower = titulo.lower()
        if any(p in titulo_lower for p in positivas):
            score += 1
            positivos.append(titulo)
        if any(n in titulo_lower for n in negativas):
            score -= 1
            negativos.append(titulo)
    return {
        "score": score,
        "positivos": positivos,
        "negativos": negativos
    } 