import sqlite3

conn = sqlite3.connect('data/inversiones.db')
cursor = conn.cursor()

# Verificar estructura de la tabla signals
cursor.execute('PRAGMA table_info(signals)')
columns = cursor.fetchall()
print("Estructura de la tabla signals:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

print("\n" + "="*50)

# Verificar estructura de la tabla tickers
cursor.execute('PRAGMA table_info(tickers)')
columns = cursor.fetchall()
print("Estructura de la tabla tickers:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close() 