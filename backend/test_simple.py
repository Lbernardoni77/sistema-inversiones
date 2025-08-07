import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.learning_service import get_ticker_performance_summary, load_weights
from services.binance_service import BinanceService

def test_simple():
    """Test simple del sistema de pesos individuales"""
    
    print("🎯 TEST SIMPLE - SISTEMA DE PESOS INDIVIDUALES")
    print("=" * 50)
    
    # 1. Verificar resumen por ticker
    print("\n📊 1. RESUMEN POR TICKER")
    print("-" * 30)
    
    try:
        summary = get_ticker_performance_summary()
        print(f"   Tickers en seguimiento: {len(summary)}")
        
        if summary:
            print("\n   📈 Primeros 5 tickers:")
            for ticker, data in list(summary.items())[:5]:
                print(f"      {ticker}: {data['performance_24h']:.2%} (24h)")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Verificar pesos de algunos tickers
    print("\n⚖️ 2. PESOS POR TICKER")
    print("-" * 30)
    
    try:
        tickers_test = ['BTCUSDT', 'ETHUSDT', 'DOGEUSDT']
        
        for ticker in tickers_test:
            weights = load_weights(ticker)
            print(f"   {ticker}:")
            print(f"     RSI: {weights['rsi']}")
            print(f"     MACD: {weights['macd']}")
            print(f"     SMA: {weights['sma']}")
            print(f"     Noticias: {weights['noticias']}")
            print()
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Probar recomendación
    print("\n🎯 3. PRUEBA DE RECOMENDACIÓN")
    print("-" * 30)
    
    try:
        binance_service = BinanceService()
        rec = binance_service.get_recommendation("BTCUSDT")
        
        if "error" not in rec:
            print(f"   Recomendación: {rec.get('recommendation')}")
            print(f"   Confidence: {rec.get('confidence')}%")
            print(f"   Precio: {rec.get('price')}")
            
            # Verificar indicadores
            indicators = rec.get('indicators', {})
            if indicators:
                print(f"   RSI: {indicators.get('rsi')}")
                print(f"   MACD: {indicators.get('macd')}")
        else:
            print(f"   ❌ Error: {rec['error']}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Test completado")

if __name__ == "__main__":
    test_simple() 