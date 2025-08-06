#!/usr/bin/env python3
"""
Script de Automatización para Benchmark de Fuentes
Se ejecuta cada 15 días y actualiza automáticamente las prioridades
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import logging
from typing import Dict, List, Optional
import shutil

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_benchmark.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class AutoBenchmark:
    """Clase para automatización del benchmark"""
    
    def __init__(self):
        self.results_file = 'benchmark_results.json'
        self.config_file = 'config/fuentes_priority.json'
        self.backup_dir = 'backups'
        self.threshold_change = 0.2  # 20% de cambio para considerar significativo
        
        # Crear directorios necesarios
        Path('config').mkdir(exist_ok=True)
        Path(self.backup_dir).mkdir(exist_ok=True)
        
        # Configuración inicial de fuentes (orden por defecto)
        self.default_sources = [
            'coingecko',
            'coincap', 
            'cryptocompare',
            'coinpaprika',
            'yahoo',
            'kraken'
        ]
    
    def should_run_benchmark(self) -> bool:
        """Determina si debe ejecutarse el benchmark basado en la fecha del último"""
        if not os.path.exists(self.results_file):
            logging.info("No existe archivo de resultados previo. Ejecutando benchmark inicial.")
            return True
        
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                last_results = json.load(f)
            
            last_timestamp = datetime.fromisoformat(last_results['timestamp'])
            days_since_last = (datetime.now() - last_timestamp).days
            
            logging.info(f"Días desde último benchmark: {days_since_last}")
            return days_since_last >= 15
            
        except Exception as e:
            logging.error(f"Error leyendo archivo de resultados: {e}")
            return True
    
    def run_benchmark(self) -> bool:
        """Ejecuta el benchmark y retorna True si fue exitoso"""
        try:
            logging.info("🚀 Ejecutando benchmark de fuentes...")
            
            # Ejecutar el script de benchmark
            result = subprocess.run(
                [sys.executable, 'benchmark_fuentes.py'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos máximo
            )
            
            if result.returncode == 0:
                logging.info("✅ Benchmark ejecutado exitosamente")
                return True
            else:
                logging.error(f"❌ Error ejecutando benchmark: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logging.error("❌ Timeout ejecutando benchmark")
            return False
        except Exception as e:
            logging.error(f"❌ Error inesperado: {e}")
            return False
    
    def load_current_results(self) -> Optional[Dict]:
        """Carga los resultados actuales del benchmark"""
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error cargando resultados actuales: {e}")
            return None
    
    def load_previous_results(self) -> Optional[Dict]:
        """Carga los resultados del benchmark anterior"""
        backup_files = list(Path(self.backup_dir).glob('benchmark_results_*.json'))
        if not backup_files:
            return None
        
        # Obtener el archivo más reciente
        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_backup, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error cargando resultados previos: {e}")
            return None
    
    def compare_performance(self, current: Dict, previous: Dict) -> Dict:
        """Compara la performance actual con la anterior"""
        logging.info("📊 Comparando performance con benchmark anterior...")
        
        current_ranking = {p['source']: p for p in current['performance_ranking']}
        previous_ranking = {p['source']: p for p in previous['performance_ranking']}
        
        changes = {
            'significant_changes': [],
            'new_sources': [],
            'removed_sources': [],
            'performance_changes': {}
        }
        
        # Analizar cambios en fuentes existentes
        for source in current_ranking:
            if source in previous_ranking:
                current_perf = current_ranking[source]
                previous_perf = previous_ranking[source]
                
                # Calcular cambios
                time_change = (current_perf['avg_response_time'] - previous_perf['avg_response_time']) / previous_perf['avg_response_time']
                success_change = current_perf['success_rate'] - previous_perf['success_rate']
                completeness_change = current_perf['avg_completeness'] - previous_perf['avg_completeness']
                
                # Determinar si el cambio es significativo
                is_significant = (
                    abs(time_change) > self.threshold_change or
                    abs(success_change) > self.threshold_change or
                    abs(completeness_change) > self.threshold_change
                )
                
                changes['performance_changes'][source] = {
                    'time_change': time_change,
                    'success_change': success_change,
                    'completeness_change': completeness_change,
                    'is_significant': is_significant
                }
                
                if is_significant:
                    changes['significant_changes'].append(source)
            else:
                changes['new_sources'].append(source)
        
        # Fuentes removidas
        for source in previous_ranking:
            if source not in current_ranking:
                changes['removed_sources'].append(source)
        
        return changes
    
    def should_update_priorities(self, changes: Dict) -> bool:
        """Determina si se deben actualizar las prioridades"""
        return (
            len(changes['significant_changes']) > 0 or
            len(changes['new_sources']) > 0 or
            len(changes['removed_sources']) > 0
        )
    
    def update_source_priorities(self, current_results: Dict) -> bool:
        """Actualiza el archivo de configuración con las nuevas prioridades"""
        try:
            # Crear configuración actualizada
            config = {
                'last_updated': datetime.now().isoformat(),
                'source_order': current_results['recommended_order'],
                'performance_data': current_results['performance_ranking'],
                'metadata': {
                    'total_sources': len(current_results['recommended_order']),
                    'benchmark_timestamp': current_results['timestamp']
                }
            }
            
            # Crear backup de configuración anterior
            if os.path.exists(self.config_file):
                backup_path = f"{self.backup_dir}/fuentes_priority_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                shutil.copy2(self.config_file, backup_path)
                logging.info(f"💾 Backup creado: {backup_path}")
            
            # Guardar nueva configuración
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logging.info(f"✅ Configuración actualizada: {self.config_file}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error actualizando configuración: {e}")
            return False
    
    def update_backend_config(self) -> bool:
        """Actualiza la configuración del backend con las nuevas prioridades"""
        try:
            if not os.path.exists(self.config_file):
                logging.warning("No existe archivo de configuración para actualizar backend")
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Aquí se actualizaría el backend
            # Por ahora, solo logueamos la acción
            logging.info(f"🔄 Actualizando backend con orden: {config['source_order']}")
            
            # TODO: Implementar actualización real del backend
            # - Modificar binance_service.py
            # - Reiniciar servicio si es necesario
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Error actualizando backend: {e}")
            return False
    
    def create_backup(self) -> bool:
        """Crea backup de los resultados actuales"""
        try:
            if os.path.exists(self.results_file):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{self.backup_dir}/benchmark_results_{timestamp}.json"
                shutil.copy2(self.results_file, backup_path)
                logging.info(f"💾 Backup creado: {backup_path}")
                return True
        except Exception as e:
            logging.error(f"❌ Error creando backup: {e}")
        return False
    
    def send_notification(self, changes: Dict, updated: bool) -> None:
        """Envía notificación sobre los cambios"""
        if not changes['significant_changes'] and not changes['new_sources'] and not changes['removed_sources']:
            logging.info("📧 No hay cambios significativos para notificar")
            return
        
        # Aquí se enviaría la notificación
        # Por ahora, solo logueamos
        logging.info("📧 Enviando notificación de cambios...")
        
        if updated:
            logging.info("✅ Prioridades actualizadas automáticamente")
        else:
            logging.warning("⚠️  Cambios detectados pero no se actualizaron las prioridades")
    
    def run(self) -> bool:
        """Ejecuta el proceso completo de automatización"""
        logging.info("🤖 Iniciando proceso de automatización de benchmark")
        
        # Verificar si debe ejecutarse
        if not self.should_run_benchmark():
            logging.info("⏰ No es momento de ejecutar benchmark (menos de 15 días)")
            return True
        
        # Crear backup de resultados anteriores
        self.create_backup()
        
        # Ejecutar benchmark
        if not self.run_benchmark():
            logging.error("❌ Falló la ejecución del benchmark")
            return False
        
        # Cargar resultados
        current_results = self.load_current_results()
        if not current_results:
            logging.error("❌ No se pudieron cargar los resultados actuales")
            return False
        
        previous_results = self.load_previous_results()
        
        if previous_results:
            # Comparar con resultados anteriores
            changes = self.compare_performance(current_results, previous_results)
            
            # Determinar si actualizar prioridades
            should_update = self.should_update_priorities(changes)
            
            if should_update:
                logging.info("🔄 Cambios significativos detectados. Actualizando prioridades...")
                
                # Actualizar configuración
                if self.update_source_priorities(current_results):
                    # Actualizar backend
                    self.update_backend_config()
                    
                    # Enviar notificación
                    self.send_notification(changes, True)
                    
                    logging.info("✅ Proceso completado exitosamente")
                    return True
                else:
                    logging.error("❌ Error actualizando prioridades")
                    self.send_notification(changes, False)
                    return False
            else:
                logging.info("✅ No hay cambios significativos. Manteniendo configuración actual.")
                return True
        else:
            # Primera ejecución
            logging.info("🆕 Primera ejecución. Configurando prioridades iniciales...")
            
            if self.update_source_priorities(current_results):
                self.update_backend_config()
                logging.info("✅ Configuración inicial completada")
                return True
            else:
                logging.error("❌ Error en configuración inicial")
                return False

def main():
    """Función principal"""
    auto_benchmark = AutoBenchmark()
    
    try:
        success = auto_benchmark.run()
        if success:
            print("✅ Proceso de automatización completado exitosamente")
            sys.exit(0)
        else:
            print("❌ Error en el proceso de automatización")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 