#!/usr/bin/env python3
"""
Dashboard Web para Monitoreo de Fuentes de Datos
Proporciona una interfaz web para ver el estado de las fuentes
"""

import json
import os
from datetime import datetime
from pathlib import Path
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from typing import Dict, List, Optional

class FuentesDashboard(BaseHTTPRequestHandler):
    """Servidor HTTP simple para el dashboard"""
    
    def do_GET(self):
        """Maneja las peticiones GET"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_content = self.generate_dashboard_html()
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            status_data = self.get_status_data()
            self.wfile.write(json.dumps(status_data, ensure_ascii=False).encode('utf-8'))
            
        elif self.path == '/api/benchmark':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            benchmark_data = self.get_benchmark_data()
            self.wfile.write(json.dumps(benchmark_data, ensure_ascii=False).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def get_status_data(self) -> Dict:
        """Obtiene datos de estado actual"""
        try:
            # Cargar configuración actual
            config_file = 'config/fuentes_priority.json'
            config = {
                'source_order': [],
                'last_updated': datetime.now().isoformat(),
                'performance_data': []
            }
            
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                except Exception as e:
                    print(f"Error leyendo config: {e}")
            
            # Cargar último benchmark
            results_file = 'benchmark_results.json'
            results = {
                'timestamp': datetime.now().isoformat(),
                'performance_ranking': [],
                'recommended_order': []
            }
            
            if os.path.exists(results_file):
                try:
                    with open(results_file, 'r', encoding='utf-8') as f:
                        results = json.load(f)
                except Exception as e:
                    print(f"Error leyendo benchmark: {e}")
            
            return {
                'config': config,
                'last_benchmark': results,
                'current_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error en get_status_data: {e}")
            return {
                'error': str(e),
                'current_time': datetime.now().isoformat()
            }
    
    def get_benchmark_data(self) -> Dict:
        """Obtiene datos históricos de benchmark"""
        try:
            # Cargar todos los archivos de backup
            backup_dir = Path('backups')
            benchmark_files = []
            
            if backup_dir.exists():
                for file in backup_dir.glob('benchmark_results_*.json'):
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            benchmark_files.append({
                                'file': file.name,
                                'timestamp': data.get('timestamp', ''),
                                'date': datetime.fromisoformat(data.get('timestamp', '')).strftime('%Y-%m-%d %H:%M'),
                                'sources_count': len(data.get('recommended_order', []))
                            })
                    except Exception:
                        continue
            
            # Ordenar por fecha
            benchmark_files.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return {
                'history': benchmark_files,
                'total_files': len(benchmark_files)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'history': [],
                'total_files': 0
            }
    
    def generate_dashboard_html(self) -> str:
        """Genera el HTML del dashboard"""
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Fuentes de Datos</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            border-left: 5px solid #667eea;
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .status-item:last-child {
            border-bottom: none;
        }
        
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .status-good {
            background: #d4edda;
            color: #155724;
        }
        
        .status-warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-error {
            background: #f8d7da;
            color: #721c24;
        }
        
        .performance-chart {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .source-ranking {
            list-style: none;
        }
        
        .source-ranking li {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .source-ranking li:last-child {
            border-bottom: none;
        }
        
        .rank-number {
            background: #667eea;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9rem;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: background 0.3s ease;
        }
        
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #6c757d;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard de Fuentes</h1>
            <p>Monitoreo automático de fuentes de datos de criptomonedas</p>
        </div>
        
        <div class="content">
            <div class="grid">
                <div class="card">
                    <h3>🎯 Estado Actual</h3>
                    <div id="current-status">
                        <div class="loading">Cargando...</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🏆 Ranking de Fuentes</h3>
                    <div id="source-ranking">
                        <div class="loading">Cargando...</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📈 Performance</h3>
                    <div id="performance-data">
                        <div class="loading">Cargando...</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📅 Historial</h3>
                    <div id="benchmark-history">
                        <div class="loading">Cargando...</div>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <button class="refresh-btn" onclick="refreshData()">🔄 Actualizar Datos</button>
            </div>
        </div>
    </div>
    
    <script>
        // Cargar datos al iniciar
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboardData();
        });
        
        function loadDashboardData() {
            console.log('🔄 Cargando datos del dashboard...');
            
            // Cargar estado actual
            fetch('/api/status')
                .then(response => {
                    console.log('📊 Respuesta de /api/status:', response.status);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('✅ Datos de estado cargados:', data);
                    updateCurrentStatus(data);
                    updateSourceRanking(data);
                    updatePerformanceData(data);
                })
                .catch(error => {
                    console.error('❌ Error cargando estado:', error);
                    document.getElementById('current-status').innerHTML = 
                        '<div class="error">Error cargando datos de estado: ' + error.message + '</div>';
                });
            
            // Cargar historial
            fetch('/api/benchmark')
                .then(response => {
                    console.log('📊 Respuesta de /api/benchmark:', response.status);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('✅ Datos de historial cargados:', data);
                    updateBenchmarkHistory(data);
                })
                .catch(error => {
                    console.error('❌ Error cargando historial:', error);
                    document.getElementById('benchmark-history').innerHTML = 
                        '<div class="error">Error cargando historial: ' + error.message + '</div>';
                });
        }
        
        function updateCurrentStatus(data) {
            const container = document.getElementById('current-status');
            
            if (data.error) {
                container.innerHTML = '<div class="error">Error: ' + data.error + '</div>';
                return;
            }
            
            const config = data.config;
            const lastBenchmark = data.last_benchmark;
            
            let html = '';
            
            // Última actualización
            const lastUpdated = new Date(config.last_updated).toLocaleString('es-ES');
            html += `
                <div class="status-item">
                    <span>Última actualización:</span>
                    <span>${lastUpdated}</span>
                </div>
            `;
            
            // Total de fuentes
            html += `
                <div class="status-item">
                    <span>Fuentes configuradas:</span>
                    <span class="status-badge status-good">${config.source_order.length}</span>
                </div>
            `;
            
            // Estado del último benchmark
            if (lastBenchmark.timestamp) {
                const benchmarkDate = new Date(lastBenchmark.timestamp).toLocaleString('es-ES');
                html += `
                    <div class="status-item">
                        <span>Último benchmark:</span>
                        <span>${benchmarkDate}</span>
                    </div>
                `;
            }
            
            // Días desde último benchmark
            if (lastBenchmark.timestamp) {
                const daysSince = Math.floor((new Date() - new Date(lastBenchmark.timestamp)) / (1000 * 60 * 60 * 24));
                const statusClass = daysSince > 15 ? 'status-warning' : 'status-good';
                const statusText = daysSince > 15 ? 'Requiere actualización' : 'Actualizado';
                
                html += `
                    <div class="status-item">
                        <span>Estado del benchmark:</span>
                        <span class="status-badge ${statusClass}">${statusText}</span>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        function updateSourceRanking(data) {
            const container = document.getElementById('source-ranking');
            
            if (data.error || !data.config.source_order) {
                container.innerHTML = '<div class="error">No hay datos de ranking disponibles</div>';
                return;
            }
            
            const sources = data.config.source_order;
            let html = '<ul class="source-ranking">';
            
            sources.forEach((source, index) => {
                html += `
                    <li>
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <span class="rank-number">${index + 1}</span>
                            <span style="font-weight: 600; text-transform: uppercase;">${source}</span>
                        </div>
                        <span class="status-badge status-good">Activo</span>
                    </li>
                `;
            });
            
            html += '</ul>';
            container.innerHTML = html;
        }
        
        function updatePerformanceData(data) {
            const container = document.getElementById('performance-data');
            
            if (data.error || !data.last_benchmark.performance_ranking) {
                container.innerHTML = '<div class="error">No hay datos de performance disponibles</div>';
                return;
            }
            
            const performance = data.last_benchmark.performance_ranking;
            let html = '';
            
                         performance.slice(0, 5).forEach((perf, index) => {
                 const successRate = (perf.success_rate * 100).toFixed(1);
                 const avgTime = perf.avg_response_time === "inf" ? "∞" : perf.avg_response_time.toFixed(2);
                
                html += `
                    <div class="status-item">
                        <span><strong>${perf.source.toUpperCase()}</strong></span>
                        <span>${successRate}% éxito</span>
                    </div>
                    <div class="status-item">
                        <span>Tiempo promedio:</span>
                        <span>${avgTime}s</span>
                    </div>
                    <div class="status-item">
                        <span>Tests exitosos:</span>
                        <span>${perf.successful_tests}/${perf.total_tests}</span>
                    </div>
                    <hr style="margin: 15px 0; border: none; border-top: 1px solid #e9ecef;">
                `;
            });
            
            container.innerHTML = html;
        }
        
        function updateBenchmarkHistory(data) {
            const container = document.getElementById('benchmark-history');
            
            if (data.error || !data.history) {
                container.innerHTML = '<div class="error">No hay historial disponible</div>';
                return;
            }
            
            const history = data.history.slice(0, 5); // Mostrar solo los últimos 5
            let html = '';
            
            if (history.length === 0) {
                html = '<div style="color: #6c757d; text-align: center;">No hay historial disponible</div>';
            } else {
                history.forEach(item => {
                    html += `
                        <div class="status-item">
                            <span>${item.date}</span>
                            <span class="status-badge status-good">${item.sources_count} fuentes</span>
                        </div>
                    `;
                });
            }
            
            container.innerHTML = html;
        }
        
        function refreshData() {
            // Mostrar indicador de carga
            document.querySelectorAll('.loading').forEach(el => {
                el.style.display = 'block';
            });
            
            // Recargar datos
            loadDashboardData();
        }
        
        // Auto-refresh cada 30 segundos
        setInterval(loadDashboardData, 30000);
    </script>
</body>
</html>
        """
    
    def log_message(self, format, *args):
        """Suprime los logs del servidor"""
        pass

def start_dashboard(port: int = 8080):
    """Inicia el servidor del dashboard"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, FuentesDashboard)
    
    print(f"🚀 Dashboard iniciado en http://localhost:{port}")
    print("📱 Presiona Ctrl+C para detener")
    
    # Abrir navegador automáticamente
    try:
        webbrowser.open(f'http://localhost:{port}')
    except:
        pass
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard detenido")
        httpd.server_close()

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dashboard de Fuentes de Datos')
    parser.add_argument('--port', type=int, default=8080, help='Puerto del servidor (default: 8080)')
    
    args = parser.parse_args()
    
    print("📊 Iniciando Dashboard de Fuentes de Datos...")
    start_dashboard(args.port)

if __name__ == "__main__":
    main() 