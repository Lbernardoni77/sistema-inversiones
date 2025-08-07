#!/usr/bin/env python3
"""
Servicio para generar gráficos localmente con los datos obtenidos
"""

import json
import base64
from io import BytesIO
from typing import List, Dict, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime, timedelta

class ChartGenerator:
    """Generador de gráficos local usando matplotlib"""
    
    def __init__(self):
        # Configurar estilo para gráficos oscuros
        plt.style.use('dark_background')
        self.colors = {
            'candle_up': '#00ff88',
            'candle_down': '#ff4444',
            'sma_7': '#ffaa00',
            'sma_21': '#00aaff',
            'sma_50': '#ff00ff',
            'bb_upper': '#888888',
            'bb_mid': '#cccccc',
            'bb_lower': '#888888',
            'support': '#00ff00',
            'resistance': '#ff3333',
            'volume': '#444444'
        }
    
    def generate_candlestick_chart(
        self, 
        klines: List[List], 
        symbol: str,
        interval: str = "1h",
        show_indicators: bool = True,
        show_support_resistance: bool = True,
        support_levels: List[float] = None,
        resistance_levels: List[float] = None,
        width: int = 1200,
        height: int = 600
    ) -> Dict:
        """
        Genera un gráfico de velas con indicadores técnicos
        
        Args:
            klines: Lista de klines en formato [timestamp, open, high, low, close, volume]
            symbol: Símbolo del ticker
            interval: Intervalo de tiempo
            show_indicators: Mostrar indicadores técnicos
            show_support_resistance: Mostrar niveles de soporte/resistencia
            support_levels: Lista de niveles de soporte
            resistance_levels: Lista de niveles de resistencia
            width: Ancho del gráfico
            height: Alto del gráfico
        
        Returns:
            Dict con la imagen en base64 y metadatos
        """
        
        if not klines or len(klines) < 2:
            return {
                "error": "Datos insuficientes para generar gráfico",
                "klines_count": len(klines) if klines else 0
            }
        
        try:
            # Crear figura
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(width/100, height/100), 
                                           gridspec_kw={'height_ratios': [3, 1]})
            
            # Procesar datos
            timestamps = [datetime.fromtimestamp(k[0]/1000) for k in klines]
            opens = [float(k[1]) for k in klines]
            highs = [float(k[2]) for k in klines]
            lows = [float(k[3]) for k in klines]
            closes = [float(k[4]) for k in klines]
            volumes = [float(k[5]) if len(k) > 5 else 0 for k in klines]
            
            # Determinar colores de velas
            candle_colors = [self.colors['candle_up'] if close >= open else self.colors['candle_down'] 
                           for open, close in zip(opens, closes)]
            
            # Gráfico principal (velas)
            ax1.set_title(f'{symbol} - {interval.upper()}', color='white', fontsize=14, fontweight='bold')
            
            # Dibujar velas
            for i in range(len(timestamps)):
                # Cuerpo de la vela
                body_height = closes[i] - opens[i]
                body_bottom = min(opens[i], closes[i])
                
                # Rectángulo del cuerpo
                rect = plt.Rectangle((i-0.3, body_bottom), 0.6, abs(body_height), 
                                   facecolor=candle_colors[i], edgecolor='white', linewidth=0.5)
                ax1.add_patch(rect)
                
                # Líneas de sombra
                ax1.plot([i, i], [lows[i], highs[i]], color='white', linewidth=1)
            
            # Calcular y mostrar indicadores técnicos
            if show_indicators:
                self._add_technical_indicators(ax1, timestamps, closes)
            
            # Agregar niveles de soporte y resistencia
            if show_support_resistance and (support_levels or resistance_levels):
                self._add_support_resistance(ax1, timestamps, support_levels, resistance_levels)
            
            # Configurar eje X
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax1.tick_params(axis='x', rotation=45, colors='white')
            ax1.tick_params(axis='y', colors='white')
            ax1.grid(True, alpha=0.3, color='gray')
            
            # Gráfico de volumen
            ax2.bar(range(len(timestamps)), volumes, color=self.colors['volume'], alpha=0.7)
            ax2.set_title('Volumen', color='white', fontsize=12)
            ax2.tick_params(axis='x', rotation=45, colors='white')
            ax2.tick_params(axis='y', colors='white')
            ax2.grid(True, alpha=0.3, color='gray')
            
            # Configurar eje X del volumen
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            
            # Ajustar layout
            plt.tight_layout()
            
            # Convertir a imagen
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', 
                       facecolor='black', edgecolor='none')
            img_buffer.seek(0)
            
            # Convertir a base64
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            
            # Calcular estadísticas
            stats = self._calculate_statistics(opens, highs, lows, closes, volumes)
            
            plt.close(fig)
            
            return {
                "image_base64": img_base64,
                "symbol": symbol,
                "interval": interval,
                "data_points": len(klines),
                "time_range": {
                    "start": timestamps[0].isoformat(),
                    "end": timestamps[-1].isoformat()
                },
                "statistics": stats,
                "indicators_shown": show_indicators,
                "support_resistance_shown": show_support_resistance
            }
            
        except Exception as e:
            return {
                "error": f"Error generando gráfico: {str(e)}",
                "klines_count": len(klines) if klines else 0
            }
    
    def _add_technical_indicators(self, ax, timestamps, closes):
        """Agrega indicadores técnicos al gráfico"""
        
        # SMA 7
        sma_7 = self._calculate_sma(closes, 7)
        if len(sma_7) > 0:
            ax.plot(timestamps[6:], sma_7, color=self.colors['sma_7'], 
                   linewidth=1, label='SMA 7', alpha=0.8)
        
        # SMA 21
        sma_21 = self._calculate_sma(closes, 21)
        if len(sma_21) > 0:
            ax.plot(timestamps[20:], sma_21, color=self.colors['sma_21'], 
                   linewidth=1, label='SMA 21', alpha=0.8)
        
        # Bollinger Bands
        bb_upper, bb_mid, bb_lower = self._calculate_bollinger_bands(closes, 20, 2)
        if len(bb_upper) > 0:
            ax.plot(timestamps[19:], bb_upper, color=self.colors['bb_upper'], 
                   linewidth=1, label='BB Upper', alpha=0.6, linestyle='--')
            ax.plot(timestamps[19:], bb_mid, color=self.colors['bb_mid'], 
                   linewidth=1, label='BB Mid', alpha=0.6, linestyle='--')
            ax.plot(timestamps[19:], bb_lower, color=self.colors['bb_lower'], 
                   linewidth=1, label='BB Lower', alpha=0.6, linestyle='--')
        
        ax.legend(loc='upper left', fontsize=8)
    
    def _add_support_resistance(self, ax, timestamps, support_levels, resistance_levels):
        """Agrega niveles de soporte y resistencia"""
        
        if support_levels:
            for level in support_levels:
                ax.axhline(y=level, color=self.colors['support'], 
                          linestyle='-', alpha=0.7, linewidth=1)
        
        if resistance_levels:
            for level in resistance_levels:
                ax.axhline(y=level, color=self.colors['resistance'], 
                          linestyle='-', alpha=0.7, linewidth=1)
    
    def _calculate_sma(self, data, period):
        """Calcula la media móvil simple"""
        if len(data) < period:
            return []
        
        sma = []
        for i in range(period - 1, len(data)):
            sma.append(sum(data[i-period+1:i+1]) / period)
        
        return sma
    
    def _calculate_bollinger_bands(self, data, period, std_dev):
        """Calcula las Bandas de Bollinger"""
        if len(data) < period:
            return [], [], []
        
        upper, mid, lower = [], [], []
        
        for i in range(period - 1, len(data)):
            slice_data = data[i-period+1:i+1]
            mean = sum(slice_data) / period
            variance = sum((x - mean) ** 2 for x in slice_data) / period
            std = variance ** 0.5
            
            mid.append(mean)
            upper.append(mean + (std_dev * std))
            lower.append(mean - (std_dev * std))
        
        return upper, mid, lower
    
    def _calculate_statistics(self, opens, highs, lows, closes, volumes):
        """Calcula estadísticas básicas"""
        return {
            "current_price": closes[-1] if closes else 0,
            "price_change": closes[-1] - opens[0] if closes and opens else 0,
            "price_change_percent": ((closes[-1] - opens[0]) / opens[0] * 100) if opens and opens[0] != 0 else 0,
            "high": max(highs) if highs else 0,
            "low": min(lows) if lows else 0,
            "volume_total": sum(volumes) if volumes else 0,
            "volume_avg": sum(volumes) / len(volumes) if volumes else 0
        }
    
    def generate_price_chart(
        self, 
        prices: List[Tuple[datetime, float]], 
        symbol: str,
        width: int = 800,
        height: int = 400
    ) -> Dict:
        """
        Genera un gráfico simple de precios
        
        Args:
            prices: Lista de tuplas (timestamp, price)
            symbol: Símbolo del ticker
            width: Ancho del gráfico
            height: Alto del gráfico
        
        Returns:
            Dict con la imagen en base64 y metadatos
        """
        
        if not prices or len(prices) < 2:
            return {
                "error": "Datos insuficientes para generar gráfico",
                "prices_count": len(prices) if prices else 0
            }
        
        try:
            # Crear figura
            fig, ax = plt.subplots(figsize=(width/100, height/100))
            
            # Separar datos
            timestamps = [p[0] for p in prices]
            price_values = [p[1] for p in prices]
            
            # Dibujar línea de precios
            ax.plot(timestamps, price_values, color='#00aaff', linewidth=2)
            
            # Configurar gráfico
            ax.set_title(f'{symbol} - Precio', color='white', fontsize=14, fontweight='bold')
            ax.set_xlabel('Tiempo', color='white')
            ax.set_ylabel('Precio (USD)', color='white')
            
            # Configurar ejes
            ax.tick_params(axis='x', rotation=45, colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.grid(True, alpha=0.3, color='gray')
            
            # Formato de fecha
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            
            # Ajustar layout
            plt.tight_layout()
            
            # Convertir a imagen
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', 
                       facecolor='black', edgecolor='none')
            img_buffer.seek(0)
            
            # Convertir a base64
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            
            plt.close(fig)
            
            return {
                "image_base64": img_base64,
                "symbol": symbol,
                "data_points": len(prices),
                "time_range": {
                    "start": timestamps[0].isoformat(),
                    "end": timestamps[-1].isoformat()
                },
                "current_price": price_values[-1] if price_values else 0
            }
            
        except Exception as e:
            return {
                "error": f"Error generando gráfico: {str(e)}",
                "prices_count": len(prices) if prices else 0
            }
