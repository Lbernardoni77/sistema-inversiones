#!/usr/bin/env python3
"""
Script para actualizar la configuración con los nuevos resultados del benchmark
"""

import json
import os
from datetime import datetime

def update_config():
    """Actualiza la configuración con los nuevos resultados"""
    
    # Cargar resultados del benchmark
    benchmark_file = 'benchmark_results.json'
    if not os.path.exists(benchmark_file):
        print("❌ No se encontró benchmark_results.json")
        return
    
    with open(benchmark_file, 'r', encoding='utf-8') as f:
        benchmark_data = json.load(f)
    
    # Crear nueva configuración
    config = {
        'last_updated': datetime.now().isoformat(),
        'source_order': benchmark_data['recommended_order'],
        'performance_data': benchmark_data['performance_ranking'],
        'metadata': {
            'total_sources': len(benchmark_data['recommended_order']),
            'benchmark_timestamp': benchmark_data['timestamp'],
            'description': 'Configuración actualizada automáticamente'
        }
    }
    
    # Guardar configuración
    config_file = 'config/fuentes_priority.json'
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ Configuración actualizada exitosamente")
    print(f"   - Fuentes: {len(config['source_order'])}")
    print(f"   - Última actualización: {config['last_updated']}")
    print(f"   - Orden: {', '.join(config['source_order'])}")

if __name__ == "__main__":
    update_config() 