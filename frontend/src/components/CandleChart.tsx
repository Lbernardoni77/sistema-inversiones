import React, { useMemo } from 'react';
import ReactApexChart from 'react-apexcharts';

interface CandleChartProps {
  klines: Array<any>; // Espera el formato de Binance
  soportes?: number[];
  resistencias?: number[];
  height?: number;
}

function calcSMA(data: number[], period: number): (number | null)[] {
  return data.map((_, i) =>
    i >= period - 1
      ? +(data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) / period).toFixed(2)
      : null
  );
}

function calcBollinger(data: number[], period = 20, numStd = 2) {
  return data.map((_, i) => {
    if (i < period - 1) return { upper: null, mid: null, lower: null };
    const slice = data.slice(i - period + 1, i + 1);
    const mean = slice.reduce((a, b) => a + b, 0) / period;
    const std = Math.sqrt(slice.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / period);
    return {
      upper: +(mean + numStd * std).toFixed(2),
      mid: +mean.toFixed(2),
      lower: +(mean - numStd * std).toFixed(2),
    };
  });
}

const CandleChart: React.FC<CandleChartProps> = ({ klines, soportes = [], resistencias = [], height = 350 }) => {
  // Todos los hooks deben ir al inicio
  const [showSMA7, setShowSMA7] = React.useState(true);
  const [showSMA21, setShowSMA21] = React.useState(true);
  const [showSMA50, setShowSMA50] = React.useState(false);
  const [showBB, setShowBB] = React.useState(false);
  const [showSoportes, setShowSoportes] = React.useState(true);
  const [showResistencias, setShowResistencias] = React.useState(true);

  // Logs de depuración
  console.log('CandleChart received - klines length:', klines?.length);
  console.log('CandleChart received - soportes:', soportes);
  console.log('CandleChart received - resistencias:', resistencias);

  // Validar que soportes y resistencias sean arrays válidos
  const validSoportes = Array.isArray(soportes) ? soportes : [];
  const validResistencias = Array.isArray(resistencias) ? resistencias : [];
  
  console.log('CandleChart validated - validSoportes:', validSoportes);
  console.log('CandleChart validated - validResistencias:', validResistencias);

  // Extraer precios de cierre
  const closes = useMemo(() => klines.map((k: any) => parseFloat(k[4])), [klines]);
  const times = useMemo(() => klines.map((k: any) => new Date(k[0])), [klines]);

  // Calcular indicadores
  const sma7 = useMemo(() => calcSMA(closes, 7), [closes]);
  const sma21 = useMemo(() => calcSMA(closes, 21), [closes]);
  const sma50 = useMemo(() => calcSMA(closes, 50), [closes]);
  const bb = useMemo(() => calcBollinger(closes, 20, 2), [closes]);

  // Si no hay datos, pasar arrays vacíos a ApexCharts
  const safeKlines = useMemo(() => (Array.isArray(klines) && klines.length > 0 ? klines : []), [klines]);
  // Usar timestamps tal cual vienen de Binance (UTC), ApexCharts los muestra en hora local
  const safeTimes = useMemo(() => safeKlines.map((k: any) => {
    // k[0] es el timestamp en ms UTC
    const utc3 = k[0] - 3 * 60 * 60 * 1000;
    return new Date(utc3);
  }), [safeKlines]);
  const safeCloses = useMemo(() => safeKlines.map((k: any) => parseFloat(k[4])), [safeKlines]);
  const safeSMA7 = useMemo(() => calcSMA(safeCloses, 7), [safeCloses]);
  const safeSMA21 = useMemo(() => calcSMA(safeCloses, 21), [safeCloses]);
  const safeSMA50 = useMemo(() => calcSMA(safeCloses, 50), [safeCloses]);
  const safeBB = useMemo(() => calcBollinger(safeCloses, 20, 2), [safeCloses]);

  // Calcular toques para cada soporte/resistencia
  const calcTouches = (levels: number[], closes: number[], umbral = 0.002) => {
    return levels.map(level =>
      closes.filter(c => Math.abs(c - level) / level < umbral).length
    );
  };

  const soporteTouches = calcTouches(validSoportes, safeCloses);
  const resistenciaTouches = calcTouches(validResistencias, safeCloses);

  // Normalizar opacidad (mínimo 0.1, máximo 0.7)
  const getOpacity = (touches: number, maxTouches: number) => {
    if (maxTouches === 0) return 0.1;
    const min = 0.1, max = 0.7;
    return min + ((touches / maxTouches) * (max - min));
  };

  const maxSoporteTouches = Math.max(...soporteTouches, 1);
  const maxResistenciaTouches = Math.max(...resistenciaTouches, 1);

  const lastClose = safeCloses.length > 0 ? safeCloses[safeCloses.length - 1] : null;
  const priceLineAnnotation = lastClose ? [{
    y: lastClose,
    borderColor: '#00bfff',
    opacity: 0.9,
    strokeDashArray: 4,
    label: {
      borderColor: '#00bfff',
      style: { color: '#fff', background: '#00bfff' },
      text: `Precio actual: $${lastClose.toLocaleString('en-US', {maximumFractionDigits: 2})}`,
      position: 'left',
      offsetY: 0,
    },
  }] : [];

  const yaxisAnnotations = [
    ...priceLineAnnotation,
    ...(showSoportes ? validSoportes.map((s, i) => ({
      y: s,
      borderColor: '#00ff00',
      // label: { text: 'Soporte', style: { background: '#00ff00', color: '#111' } }, // Eliminado para no mostrar leyenda
      opacity: getOpacity(soporteTouches[i], maxSoporteTouches),
      strokeDashArray: 0,
    })) : []),
    ...(showResistencias ? validResistencias.map((r, i) => ({
      y: r,
      borderColor: '#ff3333',
      // label: { text: 'Resistencia', style: { background: '#ff3333', color: '#111' } }, // Eliminado para no mostrar leyenda
      opacity: getOpacity(resistenciaTouches[i], maxResistenciaTouches),
      strokeDashArray: 0,
    })) : []),
  ];

  const options: ApexCharts.ApexOptions = {
    chart: {
      type: 'candlestick',
      height,
      toolbar: { show: true },
      background: 'transparent',
    },
    annotations: {
      yaxis: yaxisAnnotations
    },
    xaxis: {
      type: 'datetime',
      labels: {
        style: {
          colors: '#f5f5f5',
        },
        formatter: function(val) {
          const date = new Date(val);
          const hours = date.getHours();
          const minutes = date.getMinutes();
          return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
        }
      },
      axisBorder: { color: '#888' },
      axisTicks: { color: '#888' },
    },
    yaxis: {
      tooltip: { enabled: true },
      labels: {
        style: {
          colors: '#f5f5f5',
        },
      },
    },
    grid: {
      borderColor: '#444',
    },
    tooltip: {
      enabled: true,
      theme: 'dark',
      x: { format: 'dd MMM yyyy HH:mm' },
    },
    stroke: {
      width: [1, 2, 2, 2, 2, 2],
    },
    legend: {
      show: true,
      labels: { colors: '#f5f5f5' },
    },
  };

  // El array de series debe estar solo aquí:
  const series: ApexAxisChartSeries = [
    {
      type: 'candlestick',
      name: 'Precio',
      data: safeKlines.map((k: any) => ({
        x: new Date(k[0]),
        y: [
          parseFloat(k[1]), // open
          parseFloat(k[2]), // high
          parseFloat(k[3]), // low
          parseFloat(k[4]), // close
        ],
      })),
    },
    ...(showSMA7 ? [{ type: 'line', name: 'SMA 7', data: safeSMA7.map((v, i) => (v !== null ? { x: safeTimes[i], y: v } : undefined)).filter((d): d is {x: Date, y: number} => !!d) }] : []),
    ...(showSMA21 ? [{ type: 'line', name: 'SMA 21', data: safeSMA21.map((v, i) => (v !== null ? { x: safeTimes[i], y: v } : undefined)).filter((d): d is {x: Date, y: number} => !!d) }] : []),
    ...(showSMA50 ? [{ type: 'line', name: 'SMA 50', data: safeSMA50.map((v, i) => (v !== null ? { x: safeTimes[i], y: v } : undefined)).filter((d): d is {x: Date, y: number} => !!d) }] : []),
    ...(showBB ? [
      { type: 'line', name: 'BB Upper', data: safeBB.map((v, i) => (v.upper !== null ? { x: safeTimes[i], y: v.upper } : undefined)).filter((d): d is {x: Date, y: number} => !!d) },
      { type: 'line', name: 'BB Mid', data: safeBB.map((v, i) => (v.mid !== null ? { x: safeTimes[i], y: v.mid } : undefined)).filter((d): d is {x: Date, y: number} => !!d) },
      { type: 'line', name: 'BB Lower', data: safeBB.map((v, i) => (v.lower !== null ? { x: safeTimes[i], y: v.lower } : undefined)).filter((d): d is {x: Date, y: number} => !!d) },
    ] : []),
  ];

  return (
    <div style={{ position: 'relative' }}>
      <div style={{ marginBottom: 8, display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
        <label><input type="checkbox" checked={showSMA7} onChange={e => setShowSMA7(e.target.checked)} /> SMA 7</label>
        <label><input type="checkbox" checked={showSMA21} onChange={e => setShowSMA21(e.target.checked)} /> SMA 21</label>
        <label><input type="checkbox" checked={showSMA50} onChange={e => setShowSMA50(e.target.checked)} /> SMA 50</label>
        <label><input type="checkbox" checked={showBB} onChange={e => setShowBB(e.target.checked)} /> Bollinger Bands</label>
        <label><input type="checkbox" checked={showSoportes} onChange={e => setShowSoportes(e.target.checked)} /> Soportes</label>
        <label><input type="checkbox" checked={showResistencias} onChange={e => setShowResistencias(e.target.checked)} /> Resistencias</label>
      </div>
      <ReactApexChart options={options} series={series} type="candlestick" height={height} />
      
      {/* Leyenda de Soportes y Resistencias */}
      {(validSoportes.length > 0 || validResistencias.length > 0) && (
        <div style={{ 
          marginTop: 16, 
          padding: 12, 
          backgroundColor: '#1a1a1a', 
          borderRadius: 8, 
          border: '1px solid #333' 
        }}>
          <div style={{ 
            fontSize: 14, 
            fontWeight: 600, 
            color: '#f5f5f5', 
            marginBottom: 8 
          }}>
            📊 Leyenda de Niveles
          </div>
          
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
            {/* Leyenda de Soportes */}
            {validSoportes.length > 0 && (
              <div>
                <div style={{ 
                  fontSize: 12, 
                  fontWeight: 600, 
                  color: '#4CAF50', 
                  marginBottom: 4 
                }}>
                  🟢 Soportes (Niveles de Compra)
                </div>
                <div style={{ fontSize: 11, color: '#ccc' }}>
                  {validSoportes.map((soporte, index) => (
                    <div key={index} style={{ marginBottom: 2 }}>
                      • ${soporte.toLocaleString()} 
                      {soporteTouches[index] > 0 && (
                        <span style={{ color: '#888', marginLeft: 8 }}>
                          ({soporteTouches[index]} toques)
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Leyenda de Resistencias */}
            {validResistencias.length > 0 && (
              <div>
                <div style={{ 
                  fontSize: 12, 
                  fontWeight: 600, 
                  color: '#F44336', 
                  marginBottom: 4 
                }}>
                  🔴 Resistencias (Niveles de Venta)
                </div>
                <div style={{ fontSize: 11, color: '#ccc' }}>
                  {validResistencias.map((resistencia, index) => (
                    <div key={index} style={{ marginBottom: 2 }}>
                      • ${resistencia.toLocaleString()} 
                      {resistenciaTouches[index] > 0 && (
                        <span style={{ color: '#888', marginLeft: 8 }}>
                          ({resistenciaTouches[index]} toques)
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          <div style={{ 
            fontSize: 10, 
            color: '#888', 
            marginTop: 8, 
            fontStyle: 'italic' 
          }}>
            💡 Los niveles más intensos (más opacos) han sido tocados más veces por el precio
          </div>
        </div>
      )}
      
      <div style={{ textAlign: 'center', color: '#aaa', fontSize: 13, marginTop: 4 }}>
        Hora local de tu dispositivo
      </div>
      {safeKlines.length === 0 && (
        <div style={{ position: 'absolute', top: 60, left: 0, right: 0, textAlign: 'center', color: '#888', fontWeight: 600 }}>
          No hay datos disponibles para mostrar el gráfico
        </div>
      )}
    </div>
  );
};

export default CandleChart; 