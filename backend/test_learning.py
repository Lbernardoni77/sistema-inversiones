#!/usr/bin/env python3
"""
Script para probar el sistema de aprendizaje automático
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from services.learning_service import load_weights, optimize_weights
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Signal, Ticker

def test_learning_system():
    """
    Prueba el sistema de aprendizaje automático
    """
    print("🧠 Probando Sistema de Aprendizaje Automático")
    print("=" * 50)
    
    # 1. Verificar pesos actuales
    print("\n1. 📊 Pesos actuales:")
    try:
        weights = load_weights()
        for indicator, weight in weights.items():
            print(f"   {indicator}: {weight}")
    except Exception as e:
        print(f"   ❌ Error cargando pesos: {e}")
    
    # 2. Verificar datos de entrenamiento
    print("\n2. 📈 Datos de entrenamiento:")
    try:
        DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'inversiones.db')
        engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        total_signals = session.query(Signal).count()
        signals_with_results = session.query(Signal).filter(
            (Signal.resultado_real_1h != None) |
            (Signal.resultado_real_4h != None) |
            (Signal.resultado_real_24h != None) |
            (Signal.resultado_real_7d != None)
        ).count()
        
        print(f"   Total de señales: {total_signals}")
        print(f"   Señales con resultados: {signals_with_results}")
        
        if signals_with_results > 0:
            print(f"   ✅ Datos suficientes para entrenamiento")
        else:
            print(f"   ⚠️ No hay suficientes datos para entrenamiento")
        
        session.close()
    except Exception as e:
        print(f"   ❌ Error verificando datos: {e}")
    
    # 3. Ejecutar optimización
    print("\n3. 🤖 Ejecutando optimización:")
    try:
        if signals_with_results > 10:  # Solo si hay suficientes datos
            print("   Iniciando optimización de pesos...")
            optimize_weights(horizonte='resultado_real_24h')
            print("   ✅ Optimización completada")
            
            # Verificar nuevos pesos
            print("\n4. 📊 Nuevos pesos optimizados:")
            new_weights = load_weights()
            for indicator, weight in new_weights.items():
                print(f"   {indicator}: {weight}")
        else:
            print("   ⏳ Esperando más datos para optimización...")
    except Exception as e:
        print(f"   ❌ Error en optimización: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Prueba completada")

if __name__ == "__main__":
    test_learning_system() 