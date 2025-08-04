import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.learning_service import optimize_all_tickers, get_ticker_performance_summary, load_weights
from services.binance_service import get_recommendation

def probar_pesos_individuales():
    """Prueba el nuevo sistema de pesos individuales por ticker"""
    
    print("🎯 PROBANDO SISTEMA DE PESOS INDIVIDUALES POR TICKER")
    print("=" * 60)
    
    # 1. Verificar estado actual
    print("\n📊 1. ESTADO ACTUAL DEL SISTEMA")
    print("-" * 40)
    
    try:
        summary = get_ticker_performance_summary()
        print(f"   Tickers en seguimiento: {len(summary)}")
        
        if summary:
            print("\n   📈 Rendimiento actual por ticker:")
            for ticker, data in list(summary.items())[:5]:  # Mostrar solo los primeros 5
                print(f"      {ticker}: {data['performance_24h']:.2%} (24h)")
        
        # Mostrar pesos actuales de algunos tickers
        print("\n   ⚖️ Pesos actuales (primeros 3 tickers):")
        for ticker in list(summary.keys())[:3]:
            weights = load_weights(ticker)
            print(f"      {ticker}: RSI={weights['rsi']}, MACD={weights['macd']}, SMA={weights['sma']}")
            
    except Exception as e:
        print(f"   ❌ Error obteniendo resumen: {e}")
    
    # 2. Ejecutar optimización
    print("\n🔧 2. EJECUTANDO OPTIMIZACIÓN")
    print("-" * 40)
    
    try:
        print("   Optimizando pesos para todos los tickers...")
        resultados = optimize_all_tickers(horizonte='resultado_real_24h')
        
        exitos = sum(1 for r in resultados.values() if r['status'] == 'success')
        errores = len(resultados) - exitos
        
        print(f"   ✅ Optimización completada:")
        print(f"      - Éxitos: {exitos}")
        print(f"      - Errores: {errores}")
        print(f"      - Total: {len(resultados)}")
        
        # Mostrar algunos resultados
        print("\n   📊 Resultados de optimización:")
        for ticker, resultado in list(resultados.items())[:5]:
            if resultado['status'] == 'success':
                print(f"      {ticker}: {resultado['score']:.2%} acierto")
            else:
                print(f"      {ticker}: ❌ {resultado.get('error', 'Error desconocido')}")
                
    except Exception as e:
        print(f"   ❌ Error en optimización: {e}")
    
    # 3. Verificar nuevos pesos
    print("\n📈 3. VERIFICANDO NUEVOS PESOS")
    print("-" * 40)
    
    try:
        summary_nuevo = get_ticker_performance_summary()
        
        print("   ⚖️ Nuevos pesos optimizados:")
        for ticker in list(summary_nuevo.keys())[:3]:
            weights = load_weights(ticker)
            print(f"      {ticker}:")
            print(f"        RSI: {weights['rsi']}")
            print(f"        MACD: {weights['macd']}")
            print(f"        SMA: {weights['sma']}")
            print(f"        BB: {weights['bb']}")
            print(f"        Noticias: {weights['noticias']}")
            print()
            
    except Exception as e:
        print(f"   ❌ Error verificando nuevos pesos: {e}")
    
    # 4. Probar recomendación con nuevos pesos
    print("\n🎯 4. PROBANDO RECOMENDACIÓN CON NUEVOS PESOS")
    print("-" * 40)
    
    try:
        # Probar con BTCUSDT
        print("   Probando recomendación para BTCUSDT...")
        rec = get_recommendation("BTCUSDT", "24h")
        
        if "error" not in rec:
            print(f"      Recomendación: {rec.get('recomendacion')}")
            print(f"      Puntaje: {rec.get('puntaje_total')}")
            print(f"      Motivo: {rec.get('motivo', 'N/A')}")
            
            # Verificar que se están usando pesos específicos
            if 'pesos_aplicados' in rec:
                print(f"      Pesos aplicados: {rec['pesos_aplicados']}")
        else:
            print(f"      ❌ Error: {rec['error']}")
            
    except Exception as e:
        print(f"   ❌ Error probando recomendación: {e}")
    
    print("\n✅ Prueba completada")
    print("\n💡 Para monitorear el sistema:")
    print("   - python monitorear_aprendizaje.py")
    print("   - curl http://localhost:8000/learning/status")

if __name__ == "__main__":
    probar_pesos_individuales() 