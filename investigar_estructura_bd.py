#!/usr/bin/env python3
"""
Script para investigar la estructura real de la base de datos
"""
import sqlite3
import pandas as pd

def investigar_estructura_bd():
    print("🔍 INVESTIGANDO ESTRUCTURA DE BASE DE DATOS")
    print("=" * 60)
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('backend/data/inversiones.db')
        cursor = conn.cursor()
        
        # Verificar tablas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        print(f"📋 Tablas encontradas: {[tabla[0] for tabla in tablas]}")
        
        # Investigar estructura de cada tabla
        for tabla in tablas:
            nombre_tabla = tabla[0]
            print(f"\n📊 ESTRUCTURA DE TABLA: {nombre_tabla}")
            print("-" * 40)
            
            # Obtener estructura de la tabla
            cursor.execute(f"PRAGMA table_info({nombre_tabla});")
            columnas = cursor.fetchall()
            
            print("Columnas:")
            for col in columnas:
                print(f"   {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PK' if col[5] else ''}")
            
            # Mostrar algunos registros de ejemplo
            cursor.execute(f"SELECT * FROM {nombre_tabla} LIMIT 3;")
            registros = cursor.fetchall()
            
            if registros:
                print(f"\nRegistros de ejemplo ({len(registros)}):")
                for i, registro in enumerate(registros, 1):
                    print(f"   {i}. {registro}")
            else:
                print("\n   (Sin registros)")
        
        # Verificar si hay datos en signals
        print(f"\n📈 ANÁLISIS DETALLADO DE SIGNALS")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM signals;")
        total_signals = cursor.fetchone()[0]
        print(f"Total de registros en signals: {total_signals}")
        
        if total_signals > 0:
            # Ver las primeras columnas disponibles
            cursor.execute("SELECT * FROM signals LIMIT 1;")
            primer_registro = cursor.fetchall()
            if primer_registro:
                print(f"Primer registro: {primer_registro[0]}")
                
                # Intentar encontrar columnas que puedan contener el símbolo
                cursor.execute("PRAGMA table_info(signals);")
                columnas_signals = cursor.fetchall()
                
                print("\nBuscando columnas que puedan contener símbolos:")
                for col in columnas_signals:
                    nombre_col = col[1]
                    tipo_col = col[2]
                    print(f"   {nombre_col} ({tipo_col})")
                    
                    # Verificar si esta columna contiene símbolos
                    try:
                        cursor.execute(f"SELECT DISTINCT {nombre_col} FROM signals WHERE {nombre_col} IS NOT NULL LIMIT 5;")
                        valores = cursor.fetchall()
                        if valores:
                            print(f"     Valores: {[v[0] for v in valores]}")
                    except:
                        print(f"     (Error al consultar)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def verificar_creacion_tablas():
    print(f"\n🔧 VERIFICANDO SCRIPT DE CREACIÓN DE TABLAS")
    print("=" * 60)
    
    try:
        # Leer el script de creación de tablas
        with open('backend/create_tables.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            print("📋 Contenido del script create_tables.py:")
            print("-" * 40)
            print(contenido)
            
    except FileNotFoundError:
        print("❌ No se encontró el archivo create_tables.py")
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

def recrear_tablas():
    print(f"\n🔄 RECREANDO TABLAS")
    print("=" * 60)
    
    try:
        # Ejecutar el script de creación de tablas
        import subprocess
        result = subprocess.run(['python', 'backend/create_tables.py'], 
                              capture_output=True, text=True)
        
        print("📋 Salida del script:")
        print(result.stdout)
        
        if result.stderr:
            print("❌ Errores:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error ejecutando script: {e}")

def main():
    # 1. Investigar estructura actual
    investigar_estructura_bd()
    
    # 2. Verificar script de creación
    verificar_creacion_tablas()
    
    # 3. Recrear tablas si es necesario
    print(f"\n" + "=" * 60)
    print("🎯 RECOMENDACIONES")
    print("=" * 60)
    print("1. 🔍 Revisa la estructura actual de las tablas")
    print("2. 🔧 Verifica que create_tables.py tenga la estructura correcta")
    print("3. 🔄 Recrea las tablas si es necesario")
    print("4. 📊 Verifica que los jobs programados funcionen")
    print("5. 💾 Confirma que se guarden datos de múltiples tickers")

if __name__ == "__main__":
    main() 