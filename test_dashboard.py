#!/usr/bin/env python3
"""
Script de prueba para verificar que el dashboard puede leer los archivos
"""

import json
import os
from datetime import datetime
from pathlib import Path

def test_file_reading():
    """Prueba la lectura de archivos del dashboard"""
    print("🔍 Probando lectura de archivos del dashboard...")
    
    # Probar archivo de configuración
    config_file = 'config/fuentes_priority.json'
    print(f"\n📁 Verificando: {config_file}")
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✅ Configuración cargada correctamente")
            print(f"   - Fuentes: {len(config.get('source_order', []))}")
            print(f"   - Última actualización: {config.get('last_updated', 'N/A')}")
        except Exception as e:
            print(f"❌ Error leyendo configuración: {e}")
    else:
        print(f"❌ Archivo no encontrado: {config_file}")
    
    # Probar archivo de benchmark
    results_file = 'benchmark_results.json'
    print(f"\n📁 Verificando: {results_file}")
    if os.path.exists(results_file):
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            print(f"✅ Benchmark cargado correctamente")
            print(f"   - Timestamp: {results.get('timestamp', 'N/A')}")
            print(f"   - Fuentes testeadas: {len(results.get('performance_ranking', []))}")
        except Exception as e:
            print(f"❌ Error leyendo benchmark: {e}")
    else:
        print(f"❌ Archivo no encontrado: {results_file}")
    
    # Probar directorio de backups
    backup_dir = Path('backups')
    print(f"\n📁 Verificando: {backup_dir}")
    if backup_dir.exists():
        backup_files = list(backup_dir.glob('benchmark_results_*.json'))
        print(f"✅ Directorio de backups encontrado")
        print(f"   - Archivos de backup: {len(backup_files)}")
    else:
        print(f"⚠️  Directorio de backups no encontrado (se creará automáticamente)")

def test_dashboard_data():
    """Prueba la generación de datos del dashboard"""
    print("\n🔍 Probando generación de datos del dashboard...")
    
    try:
        # Simular la función get_status_data del dashboard
        config_file = 'config/fuentes_priority.json'
        results_file = 'benchmark_results.json'
        
        config = {}
        results = {}
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        if os.path.exists(results_file):
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
        
        status_data = {
            'config': config,
            'last_benchmark': results,
            'current_time': datetime.now().isoformat()
        }
        
        print("✅ Datos del dashboard generados correctamente")
        print(f"   - Configuración: {len(config.get('source_order', []))} fuentes")
        print(f"   - Benchmark: {len(results.get('performance_ranking', []))} fuentes")
        
        return status_data
        
    except Exception as e:
        print(f"❌ Error generando datos del dashboard: {e}")
        return None

if __name__ == "__main__":
    test_file_reading()
    test_dashboard_data()
    print("\n✅ Pruebas completadas") 