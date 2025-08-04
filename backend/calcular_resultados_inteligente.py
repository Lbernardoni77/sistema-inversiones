import sqlite3
import time
from datetime import datetime, timedelta
import requests

def calcular_resultados_inteligente():
    """Calcula resultados reales de manera más eficiente"""
    
    conn = sqlite3.connect('data/inversiones.db')
    cursor = conn.cursor()
    
    # Obtener señales que no tienen resultados calculados y tienen precio válido
    cursor.execute('''
        SELECT s.id, s.ticker_id, s.price, s.timestamp, t.symbol 
        FROM signals s 
        JOIN tickers t ON s.ticker_id = t.id 
        WHERE s.resultado_real_24h IS NULL 
        AND s.price IS NOT NULL 
        AND s.price > 0
        ORDER BY s.timestamp DESC 
        LIMIT 50
    ''')
    
    señales = cursor.fetchall()
    print(f"📊 Procesando {len(señales)} señales más recientes...")
    
    for i, (signal_id, ticker_id, precio_original, timestamp, symbol) in enumerate(señales):
        try:
            print(f"  [{i+1}/{len(señales)}] Procesando {symbol}...")
            
            # Calcular tiempo transcurrido
            tiempo_transcurrido = datetime.now() - datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Solo procesar si han pasado al menos 1 hora
            if tiempo_transcurrido < timedelta(hours=1):
                print(f"    ⏳ Aún no ha pasado suficiente tiempo para {symbol}")
                continue
            
            # Obtener precio actual
            try:
                url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    precio_actual = float(response.json()['price'])
                    
                    # Calcular cambio porcentual
                    cambio_porcentual = ((precio_actual - precio_original) / precio_original) * 100
                    
                    # Determinar resultado
                    if cambio_porcentual > 2:
                        resultado = 'subio'
                    elif cambio_porcentual < -2:
                        resultado = 'bajo'
                    else:
                        resultado = 'sin cambio'
                    
                    # Actualizar base de datos según el tiempo transcurrido
                    if tiempo_transcurrido >= timedelta(hours=1):
                        cursor.execute('UPDATE signals SET resultado_real_1h = ? WHERE id = ?', (resultado, signal_id))
                    
                    if tiempo_transcurrido >= timedelta(hours=4):
                        cursor.execute('UPDATE signals SET resultado_real_4h = ? WHERE id = ?', (resultado, signal_id))
                    
                    if tiempo_transcurrido >= timedelta(hours=24):
                        cursor.execute('UPDATE signals SET resultado_real_24h = ? WHERE id = ?', (resultado, signal_id))
                    
                    if tiempo_transcurrido >= timedelta(days=7):
                        cursor.execute('UPDATE signals SET resultado_real_7d = ? WHERE id = ?', (resultado, signal_id))
                    
                    print(f"    ✅ {symbol}: {resultado} ({cambio_porcentual:.2f}%)")
                    
                else:
                    print(f"    ❌ Error obteniendo precio para {symbol}")
                    
            except Exception as e:
                print(f"    ❌ Error procesando {symbol}: {e}")
            
            # Pausa para no sobrecargar la API
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    ❌ Error general: {e}")
            continue
    
    conn.commit()
    conn.close()
    print("🎉 Proceso completado")

if __name__ == "__main__":
    calcular_resultados_inteligente() 