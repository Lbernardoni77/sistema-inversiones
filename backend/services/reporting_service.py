import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import pandas as pd

from models import OptimizationHistory, RecommendationPerformance

class ReportingService:
    """Servicio para generar reportes y auditoría del sistema de recomendaciones"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def registrar_optimizacion(self, 
                             tipo_optimizacion: str,
                             descripcion: str,
                             pesos_anteriores: Dict,
                             pesos_nuevos: Dict,
                             parametros_anteriores: Optional[Dict] = None,
                             parametros_nuevos: Optional[Dict] = None,
                             motivo_ajuste: str = "",
                             metricas_resultado: Optional[Dict] = None,
                             usuario: str = "sistema") -> OptimizationHistory:
        """Registra una nueva optimización en el historial"""
        
        optimizacion = OptimizationHistory(
            tipo_optimizacion=tipo_optimizacion,
            descripcion=descripcion,
            pesos_anteriores=pesos_anteriores,
            pesos_nuevos=pesos_nuevos,
            parametros_anteriores=parametros_anteriores,
            parametros_nuevos=parametros_nuevos,
            motivo_ajuste=motivo_ajuste,
            metricas_resultado=metricas_resultado,
            usuario=usuario
        )
        
        self.db.add(optimizacion)
        self.db.commit()
        self.db.refresh(optimizacion)
        
        return optimizacion
    
    def registrar_recomendacion(self,
                              simbolo: str,
                              recomendacion: str,
                              precio_recomendacion: float,
                              pesos_utilizados: Dict,
                              indicadores_utilizados: Dict,
                              contexto_mercado: Optional[Dict] = None) -> RecommendationPerformance:
        """Registra una nueva recomendación para seguimiento posterior"""
        
        performance = RecommendationPerformance(
            fecha_recomendacion=datetime.utcnow(),
            simbolo=simbolo,
            recomendacion=recomendacion,
            precio_recomendacion=precio_recomendacion,
            pesos_utilizados=pesos_utilizados,
            indicadores_utilizados=indicadores_utilizados,
            contexto_mercado=contexto_mercado
        )
        
        self.db.add(performance)
        self.db.commit()
        self.db.refresh(performance)
        
        return performance
    
    def verificar_recomendacion(self, 
                              id_recomendacion: int,
                              precio_verificacion: float,
                              resultado: str) -> RecommendationPerformance:
        """Verifica el resultado de una recomendación previa"""
        
        performance = self.db.query(RecommendationPerformance).filter(
            RecommendationPerformance.id == id_recomendacion
        ).first()
        
        if performance:
            performance.fecha_verificacion = datetime.utcnow()
            performance.precio_verificacion = precio_verificacion
            performance.resultado = resultado
            
            # Calcular precisión
            if resultado == "exitoso":
                performance.precision = 1.0
            elif resultado == "fallido":
                performance.precision = 0.0
            else:
                performance.precision = 0.5
            
            self.db.commit()
            self.db.refresh(performance)
        
        return performance
    
    def obtener_resumen_ejecutivo(self, 
                                 fecha_inicio: Optional[datetime] = None,
                                 fecha_fin: Optional[datetime] = None) -> Dict:
        """Genera un resumen ejecutivo del rendimiento del sistema"""
        
        if not fecha_inicio:
            fecha_inicio = datetime.utcnow() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = datetime.utcnow()
        
        # Estadísticas generales
        total_recomendaciones = self.db.query(RecommendationPerformance).filter(
            RecommendationPerformance.fecha_recomendacion.between(fecha_inicio, fecha_fin)
        ).count()
        
        exitosas = self.db.query(RecommendationPerformance).filter(
            RecommendationPerformance.fecha_recomendacion.between(fecha_inicio, fecha_fin),
            RecommendationPerformance.resultado == "exitoso"
        ).count()
        
        fallidas = self.db.query(RecommendationPerformance).filter(
            RecommendationPerformance.fecha_recomendacion.between(fecha_inicio, fecha_fin),
            RecommendationPerformance.resultado == "fallido"
        ).count()
        
        precision_global = exitosas / total_recomendaciones if total_recomendaciones > 0 else 0
        
        # Optimizaciones recientes
        optimizaciones_recientes = self.db.query(OptimizationHistory).filter(
            OptimizationHistory.fecha.between(fecha_inicio, fecha_fin)
        ).order_by(desc(OptimizationHistory.fecha)).limit(5).all()
        
        return {
            "metadata": {
                "fecha_consulta": datetime.utcnow().isoformat(),
                "periodo_analizado": f"{fecha_inicio.date()} a {fecha_fin.date()}",
                "total_recomendaciones": total_recomendaciones
            },
            "resumen_ejecutivo": {
                "precision_global": round(precision_global, 3),
                "recomendaciones_exitosas": exitosas,
                "recomendaciones_fallidas": fallidas,
                "recomendaciones_pendientes": total_recomendaciones - exitosas - fallidas
            },
            "optimizaciones_recientes": [
                {
                    "fecha": opt.fecha.isoformat(),
                    "tipo": opt.tipo_optimizacion,
                    "descripcion": opt.descripcion,
                    "motivo": opt.motivo_ajuste
                }
                for opt in optimizaciones_recientes
            ]
        }
    
    def obtener_detalle_por_simbolo(self, 
                                   simbolo: str,
                                   fecha_inicio: Optional[datetime] = None,
                                   fecha_fin: Optional[datetime] = None) -> Dict:
        """Genera un análisis detallado por símbolo"""
        
        if not fecha_inicio:
            fecha_inicio = datetime.utcnow() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = datetime.utcnow()
        
        recomendaciones = self.db.query(RecommendationPerformance).filter(
            RecommendationPerformance.simbolo == simbolo,
            RecommendationPerformance.fecha_recomendacion.between(fecha_inicio, fecha_fin)
        ).all()
        
        total = len(recomendaciones)
        exitosas = sum(1 for r in recomendaciones if r.resultado == "exitoso")
        fallidas = sum(1 for r in recomendaciones if r.resultado == "fallido")
        precision = exitosas / total if total > 0 else 0
        
        # Análisis por tipo de recomendación
        compras = [r for r in recomendaciones if r.recomendacion == "comprar"]
        ventas = [r for r in recomendaciones if r.recomendacion == "vender"]
        
        return {
            "simbolo": simbolo,
            "periodo_analizado": f"{fecha_inicio.date()} a {fecha_fin.date()}",
            "metricas_generales": {
                "total_recomendaciones": total,
                "precision": round(precision, 3),
                "exitosas": exitosas,
                "fallidas": fallidas
            },
            "analisis_por_tipo": {
                "compras": {
                    "total": len(compras),
                    "exitosas": sum(1 for r in compras if r.resultado == "exitoso"),
                    "precision": sum(1 for r in compras if r.resultado == "exitoso") / len(compras) if compras else 0
                },
                "ventas": {
                    "total": len(ventas),
                    "exitosas": sum(1 for r in ventas if r.resultado == "exitoso"),
                    "precision": sum(1 for r in ventas if r.resultado == "exitoso") / len(ventas) if ventas else 0
                }
            },
            "recomendaciones_recientes": [
                {
                    "fecha": r.fecha_recomendacion.isoformat(),
                    "recomendacion": r.recomendacion,
                    "precio_recomendacion": r.precio_recomendacion,
                    "resultado": r.resultado,
                    "precision": r.precision
                }
                for r in recomendaciones[-10:]  # Últimas 10
            ]
        }
    
    def obtener_evolucion_pesos(self, 
                               fecha_inicio: Optional[datetime] = None,
                               fecha_fin: Optional[datetime] = None) -> List[Dict]:
        """Obtiene la evolución de los pesos del motor de decisión"""
        
        if not fecha_inicio:
            fecha_inicio = datetime.utcnow() - timedelta(days=90)
        if not fecha_fin:
            fecha_fin = datetime.utcnow()
        
        optimizaciones = self.db.query(OptimizationHistory).filter(
            OptimizationHistory.tipo_optimizacion == "pesos",
            OptimizationHistory.fecha.between(fecha_inicio, fecha_fin)
        ).order_by(OptimizationHistory.fecha).all()
        
        return [
            {
                "fecha": opt.fecha.isoformat(),
                "pesos_anteriores": opt.pesos_anteriores,
                "pesos_nuevos": opt.pesos_nuevos,
                "motivo_ajuste": opt.motivo_ajuste,
                "metricas_resultado": opt.metricas_resultado
            }
            for opt in optimizaciones
        ]
    
    def exportar_datos(self, 
                      formato: str = "json",
                      fecha_inicio: Optional[datetime] = None,
                      fecha_fin: Optional[datetime] = None) -> str:
        """Exporta los datos en el formato especificado"""
        
        if not fecha_inicio:
            fecha_inicio = datetime.utcnow() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = datetime.utcnow()
        
        # Obtener datos
        recomendaciones = self.db.query(RecommendationPerformance).filter(
            RecommendationPerformance.fecha_recomendacion.between(fecha_inicio, fecha_fin)
        ).all()
        
        optimizaciones = self.db.query(OptimizationHistory).filter(
            OptimizationHistory.fecha.between(fecha_inicio, fecha_fin)
        ).all()
        
        if formato.lower() == "csv":
            return self._exportar_csv(recomendaciones, optimizaciones)
        else:
            return self._exportar_json(recomendaciones, optimizaciones)
    
    def _exportar_csv(self, recomendaciones, optimizaciones) -> str:
        """Exporta datos en formato CSV"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_recomendaciones_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header para recomendaciones
            writer.writerow(['=== RECOMENDACIONES ==='])
            writer.writerow(['Fecha', 'Símbolo', 'Recomendación', 'Precio', 'Resultado', 'Precisión'])
            
            for r in recomendaciones:
                writer.writerow([
                    r.fecha_recomendacion.strftime("%Y-%m-%d %H:%M"),
                    r.simbolo,
                    r.recomendacion,
                    r.precio_recomendacion,
                    r.resultado or "pendiente",
                    r.precision or "N/A"
                ])
            
            writer.writerow([])
            writer.writerow(['=== OPTIMIZACIONES ==='])
            writer.writerow(['Fecha', 'Tipo', 'Descripción', 'Motivo'])
            
            for o in optimizaciones:
                writer.writerow([
                    o.fecha.strftime("%Y-%m-%d %H:%M"),
                    o.tipo_optimizacion,
                    o.descripcion,
                    o.motivo_ajuste
                ])
        
        return filename
    
    def _exportar_json(self, recomendaciones, optimizaciones) -> str:
        """Exporta datos en formato JSON"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_recomendaciones_{timestamp}.json"
        
        data = {
            "metadata": {
                "fecha_exportacion": datetime.utcnow().isoformat(),
                "total_recomendaciones": len(recomendaciones),
                "total_optimizaciones": len(optimizaciones)
            },
            "recomendaciones": [
                {
                    "fecha": r.fecha_recomendacion.isoformat(),
                    "simbolo": r.simbolo,
                    "recomendacion": r.recomendacion,
                    "precio_recomendacion": r.precio_recomendacion,
                    "resultado": r.resultado,
                    "precision": r.precision,
                    "pesos_utilizados": r.pesos_utilizados
                }
                for r in recomendaciones
            ],
            "optimizaciones": [
                {
                    "fecha": o.fecha.isoformat(),
                    "tipo": o.tipo_optimizacion,
                    "descripcion": o.descripcion,
                    "pesos_anteriores": o.pesos_anteriores,
                    "pesos_nuevos": o.pesos_nuevos,
                    "motivo_ajuste": o.motivo_ajuste
                }
                for o in optimizaciones
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filename 