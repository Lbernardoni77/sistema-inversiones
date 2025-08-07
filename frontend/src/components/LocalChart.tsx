import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

interface LocalChartProps {
  symbol: string;
  interval?: string;
  limit?: number;
  showIndicators?: boolean;
  showSupportResistance?: boolean;
  width?: number;
  height?: number;
  chartType?: 'candlestick' | 'price';
}

interface ChartData {
  image_base64?: string;
  error?: string;
  symbol?: string;
  interval?: string;
  data_points?: number;
  time_range?: {
    start: string;
    end: string;
  };
  statistics?: {
    current_price: number;
    price_change: number;
    price_change_percent: number;
    high: number;
    low: number;
    volume_total: number;
    volume_avg: number;
  };
}

const LocalChart: React.FC<LocalChartProps> = ({
  symbol,
  interval = '1h',
  limit = 100,
  showIndicators = true,
  showSupportResistance = true,
  width = 1200,
  height = 600,
  chartType = 'candlestick'
}) => {
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchChart = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let response;
      
      if (chartType === 'candlestick') {
        response = await fetch(
          `${apiService.baseURL}/charts/candlestick/${symbol}?` +
          `interval=${interval}&limit=${limit}&` +
          `show_indicators=${showIndicators}&` +
          `show_support_resistance=${showSupportResistance}&` +
          `width=${width}&height=${height}`
        );
      } else {
        response = await fetch(
          `${apiService.baseURL}/charts/price/${symbol}?` +
          `width=${width}&height=${height}`
        );
      }
      
      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setChartData(data);
      }
    } catch (err) {
      setError(`Error cargando gráfico: ${err instanceof Error ? err.message : 'Error desconocido'}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChart();
  }, [symbol, interval, limit, showIndicators, showSupportResistance, width, height, chartType]);

  const handleRefresh = () => {
    fetchChart();
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: height,
        backgroundColor: '#1a1a1a',
        borderRadius: '8px',
        border: '1px solid #333'
      }}>
        <div style={{ textAlign: 'center', color: '#f5f5f5' }}>
          <div style={{ fontSize: '18px', marginBottom: '10px' }}>🔄</div>
          <div>Generando gráfico...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: height,
        backgroundColor: '#1a1a1a',
        borderRadius: '8px',
        border: '1px solid #333',
        padding: '20px'
      }}>
        <div style={{ textAlign: 'center', color: '#f5f5f5' }}>
          <div style={{ fontSize: '18px', marginBottom: '10px' }}>❌</div>
          <div style={{ marginBottom: '10px' }}>{error}</div>
          <button 
            onClick={handleRefresh}
            style={{
              padding: '8px 16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  if (!chartData || !chartData.image_base64) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: height,
        backgroundColor: '#1a1a1a',
        borderRadius: '8px',
        border: '1px solid #333'
      }}>
        <div style={{ textAlign: 'center', color: '#888' }}>
          📊 No hay datos disponibles para este ticker
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: 'relative' }}>
      {/* Controles */}
      <div style={{ 
        marginBottom: '10px', 
        display: 'flex', 
        gap: '10px', 
        alignItems: 'center',
        flexWrap: 'wrap'
      }}>
        <button 
          onClick={handleRefresh}
          style={{
            padding: '6px 12px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          🔄 Actualizar
        </button>
        
        {chartData.statistics && (
          <div style={{ 
            display: 'flex', 
            gap: '15px', 
            fontSize: '12px', 
            color: '#ccc',
            flexWrap: 'wrap'
          }}>
            <span>💰 ${chartData.statistics.current_price?.toLocaleString()}</span>
            <span style={{ 
              color: chartData.statistics.price_change_percent >= 0 ? '#00ff88' : '#ff4444' 
            }}>
              {chartData.statistics.price_change_percent >= 0 ? '↗' : '↘'} 
              {chartData.statistics.price_change_percent?.toFixed(2)}%
            </span>
            <span>📈 Máx: ${chartData.statistics.high?.toLocaleString()}</span>
            <span>📉 Mín: ${chartData.statistics.low?.toLocaleString()}</span>
          </div>
        )}
      </div>

      {/* Gráfico */}
      <div style={{
        backgroundColor: '#1a1a1a',
        borderRadius: '8px',
        border: '1px solid #333',
        overflow: 'hidden'
      }}>
        <img 
          src={`data:image/png;base64,${chartData.image_base64}`}
          alt={`Gráfico de ${symbol}`}
          style={{
            width: '100%',
            height: 'auto',
            display: 'block'
          }}
        />
      </div>

      {/* Información adicional */}
      {chartData.time_range && (
        <div style={{
          marginTop: '10px',
          padding: '8px 12px',
          backgroundColor: '#2a2a2a',
          borderRadius: '4px',
          fontSize: '12px',
          color: '#ccc',
          textAlign: 'center'
        }}>
          📅 {new Date(chartData.time_range.start).toLocaleString()} - {new Date(chartData.time_range.end).toLocaleString()}
          {chartData.data_points && ` • ${chartData.data_points} puntos de datos`}
        </div>
      )}
    </div>
  );
};

export default LocalChart;
