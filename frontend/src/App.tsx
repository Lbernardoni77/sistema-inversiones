import React, { useState, useEffect, useCallback } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter as Router, Routes, Route, useNavigate, useParams } from 'react-router-dom';
import TickerInput from './components/TickerInput';
import TickerCard from './components/TickerCard';
import TickerDetails from './components/TickerDetails';
import TradingViewChart from './components/TradingViewChart';
import HorizonSelector from './components/HorizonSelector';
import apiService, { TickerRecommendation, TickerRecommendationSummary } from './services/api';

const queryClient = new QueryClient();

interface TickerData {
  symbol: string;
  price: number;
  recommendation: string;
  priceChange: number;
  lastUpdate: Date;
  previousPrice?: number;
  hasData?: boolean; // Indica si hay datos reales disponibles
}

// Definir función para calcular el limit según rango e intervalo
function getKlinesLimit(range: string, interval: string): number {
  if (range === '1d') {
    if (interval === '1m') return 60 * 24;
    if (interval === '5m') return 12 * 24;
    if (interval === '15m') return 4 * 24;
    if (interval === '1h') return 24;
    if (interval === '4h') return 6;
    if (interval === '1d') return 1;
    if (interval === '1w') return 1;
  }
  if (range === '1mo') {
    if (interval === '1m') return 60 * 24 * 30;
    if (interval === '5m') return 12 * 24 * 30;
    if (interval === '15m') return 4 * 24 * 30;
    if (interval === '1h') return 24 * 30;
    if (interval === '4h') return 6 * 30;
    if (interval === '1d') return 30;
    if (interval === '1w') return 5;
  }
  if (range === '1y') {
    if (interval === '1d') return 365;
    if (interval === '1w') return 52;
    if (interval === '1h') return 24 * 365;
    if (interval === '4h') return 6 * 365;
  }
  if (range === 'all') {
    if (interval === '1d') return 1000;
    if (interval === '1w') return 200;
    if (interval === '1h') return 24 * 365;
    if (interval === '4h') return 6 * 365;
  }
  return 30;
}

function Dashboard() {
  const [tickers, setTickers] = useState<TickerData[]>([]);
  const [tickerPeriods, setTickerPeriods] = useState<{ [symbol: string]: string }>(() => {
    const saved = localStorage.getItem('tickerPeriods');
    return saved ? JSON.parse(saved) : {};
  });
  const [updateInterval, setUpdateInterval] = useState(5); // segundos
  const [isLoading, setIsLoading] = useState(false);
  const [selectedChartSymbol, setSelectedChartSymbol] = useState<string | null>(null);
  const [chartRange, setChartRange] = useState<string>('1mo');
  const [chartInterval, setChartInterval] = useState<string>('1d');
  // Variables eliminadas: klines y selectedChartRecommendation (ya no son necesarias con LocalChart)
  const [selectedHorizon, setSelectedHorizon] = useState<string>("24h");
  const chartRangeOptions = [
    { value: '1d', label: '1 Día', limit: 1 },
    { value: '1mo', label: '1 Mes', limit: 30 },
    { value: '1y', label: '1 Año', limit: 365 },
    { value: 'all', label: 'Todo', limit: 1000 },
  ];
  const chartIntervalOptions = [
    { value: '1m', label: '1 Minuto' },
    { value: '5m', label: '5 Minutos' },
    { value: '15m', label: '15 Minutos' },
    { value: '1h', label: '1 Hora' },
    { value: '4h', label: '4 Horas' },
    { value: '1d', label: '1 Día' },
    { value: '1w', label: '1 Semana' },
  ];

  // Guardar en localStorage solo tickers con datos válidos
  React.useEffect(() => {
    const validTickers = tickers.filter(ticker => ticker.hasData && ticker.price > 0);
    localStorage.setItem('tickers', JSON.stringify(validTickers));
  }, [tickers]);
  React.useEffect(() => {
    localStorage.setItem('tickerPeriods', JSON.stringify(tickerPeriods));
  }, [tickerPeriods]);

  // Cargar tickers desde el backend al iniciar
  React.useEffect(() => {
    const loadTickersFromBackend = async () => {
      try {
        const backendTickers = await apiService.getTickersFromBackend();
        console.log('Backend tickers response:', backendTickers);
        
        if (backendTickers && backendTickers.tickers && Array.isArray(backendTickers.tickers) && backendTickers.tickers.length > 0) {
          // Cargar datos para cada ticker del backend
          const tickersWithData: TickerData[] = [];
          for (const symbol of backendTickers.tickers) {
            try {
              const price = await apiService.getTickerPrice(symbol, '1d');
              const recommendation = await apiService.getTickerRecommendation(symbol, selectedHorizon);
              
              console.log(`Price data for ${symbol}:`, price);
              console.log(`Recommendation data for ${symbol}:`, recommendation);
              
              const precioNumerico = typeof price.price === 'string' ? parseFloat(String(price.price).replace(',', '.')) : price.price;
              
              if (price && typeof precioNumerico === 'number' && !isNaN(precioNumerico)) {
                tickersWithData.push({
                  symbol,
                  price: precioNumerico,
                  recommendation: recommendation?.recomendacion || 'Mantener',
                  priceChange: price.change_24h ?? 0,
                  lastUpdate: new Date(),
                  hasData: true,
                });
              } else {
                console.warn(`Invalid price data for ${symbol}:`, price);
                tickersWithData.push({
                  symbol,
                  price: 0,
                  recommendation: 'Sin datos',
                  priceChange: 0,
                  lastUpdate: new Date(),
                  hasData: false,
                });
              }
            } catch (error) {
              console.error(`Error cargando datos para ${symbol}:`, error);
              tickersWithData.push({
                symbol,
                price: 0,
                recommendation: 'Sin datos',
                priceChange: 0,
                lastUpdate: new Date(),
                hasData: false,
              });
            }
          }
          console.log('Setting tickers:', tickersWithData);
          setTickers(tickersWithData);
        } else {
          console.warn('No valid tickers from backend:', backendTickers);
          setTickers([]);
        }
      } catch (error) {
        console.error('Error cargando tickers del backend:', error);
        setTickers([]);
      }
    };
    
    loadTickersFromBackend();
  }, [selectedHorizon]);

  // Actualizar el símbolo del gráfico por defecto al primer ticker
  React.useEffect(() => {
    if (!selectedChartSymbol && tickers.length > 0) {
      setSelectedChartSymbol(tickers[0].symbol);
    }
    if (tickers.length === 0) {
      setSelectedChartSymbol(null);
    }
  }, [tickers, selectedChartSymbol]);

  // useEffect eliminados: fetchKlines y fetchRecommendation (LocalChart los maneja internamente)

  const navigate = useNavigate();

  const handleAddTicker = async (symbol: string) => {
    if (tickers.some(t => t.symbol === symbol)) {
      alert('Este ticker ya está en seguimiento');
      return;
    }
    setIsLoading(true);
    try {
      let recommendation, price;
      let period = tickerPeriods[symbol] || '1d';
      try {
        recommendation = await apiService.getTickerRecommendation(symbol, selectedHorizon);
        price = await apiService.getTickerPrice(symbol, period);
        
        // Debug: Log de la respuesta del precio
        console.log('Respuesta del precio:', price);
        console.log('Tipo de price.price:', typeof price.price);
        console.log('Valor de price.price:', price.price);
        
      } catch (err) {
        console.error('Error al obtener datos:', err);
        // En lugar de mostrar alert, agregar el ticker sin datos
        const newTicker: TickerData = {
          symbol,
          price: 0,
          recommendation: 'Sin datos',
          priceChange: 0,
          lastUpdate: new Date(),
          hasData: false, // Marcar que no hay datos disponibles
        };
        setTickers(prev => [...prev, newTicker]);
        setTickerPeriods(prev => ({ ...prev, [symbol]: period }));
        return;
      }
      
      // Convertir el precio a número si es necesario
      const precioNumerico = typeof price.price === 'string' ? parseFloat(String(price.price).replace(',', '.')) : price.price;
      
      if (!price || typeof precioNumerico !== 'number' || isNaN(precioNumerico)) {
        console.error('Precio inválido:', price);
        // En lugar de mostrar alert, agregar el ticker sin datos
        const newTicker: TickerData = {
          symbol,
          price: 0,
          recommendation: 'Sin datos',
          priceChange: 0,
          lastUpdate: new Date(),
          hasData: false, // Marcar que no hay datos disponibles
        };
        setTickers(prev => [...prev, newTicker]);
        setTickerPeriods(prev => ({ ...prev, [symbol]: period }));
        return;
      }
      
      // Si no hay recomendación, usar una por defecto
      const recomendacion = recommendation?.recomendacion || 'Mantener';
      
      // Agregar ticker a la base de datos del backend
      try {
        const backendResponse = await apiService.addTickerToBackend(symbol);
        if (!backendResponse.ok) {
          console.warn(`Advertencia: ${backendResponse.msg}`);
        }
      } catch (backendError) {
        console.error('Error al agregar ticker al backend:', backendError);
        // No bloqueamos la operación si falla el backend
      }
      
      const newTicker: TickerData = {
        symbol,
        price: precioNumerico,
        recommendation: recomendacion,
        priceChange: price.change_percent ?? 0,
        lastUpdate: new Date(),
        hasData: true, // Marcar que hay datos disponibles
      };
      setTickers(prev => [...prev, newTicker]);
      setTickerPeriods(prev => ({ ...prev, [symbol]: period }));
    } catch (error) {
      alert(`Error al agregar ${symbol}: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePeriodChange = async (symbol: string, period: string) => {
    setTickerPeriods(prev => ({ ...prev, [symbol]: period }));
    try {
      const price = await apiService.getTickerPrice(symbol, period);
      setTickers(prev => prev.map(t =>
        t.symbol === symbol
          ? { ...t, price: price.price, priceChange: price.change_percent ?? 0, lastUpdate: new Date(), hasData: true }
          : t
      ));
    } catch (error) {
      console.error(`Error al actualizar el periodo para ${symbol}:`, error);
      // Marcar que no hay datos disponibles
      setTickers(prev => prev.map(t =>
        t.symbol === symbol
          ? { ...t, hasData: false, lastUpdate: new Date() }
          : t
      ));
    }
  };

  const handleHorizonChange = async (newHorizon: string) => {
    setSelectedHorizon(newHorizon);
    setIsLoading(true);
    
    try {
      // Obtener recomendaciones para todos los tickers con el nuevo horizonte
      const recommendations = await apiService.getTickersRecommendations(newHorizon);
      
      // Actualizar los tickers con las nuevas recomendaciones
      setTickers(prev => prev.map(ticker => {
        const newRec = recommendations.resultados.find(r => r.symbol === ticker.symbol);
        if (newRec && !newRec.error) {
          return {
            ...ticker,
            recommendation: newRec.recomendacion,
            lastUpdate: new Date(),
            hasData: true
          };
        }
        return {
          ...ticker,
          hasData: false,
          lastUpdate: new Date()
        };
      }));
    } catch (error) {
      console.error('Error al actualizar recomendaciones:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveTicker = async (symbol: string) => {
    // Eliminar ticker de la base de datos del backend
    try {
      const backendResponse = await apiService.removeTickerFromBackend(symbol);
      if (!backendResponse.ok) {
        console.warn(`Advertencia: ${backendResponse.msg}`);
      }
    } catch (backendError) {
      console.error('Error al eliminar ticker del backend:', backendError);
      // No bloqueamos la operación si falla el backend
    }
    
    // Eliminar del frontend
    setTickers(prev => prev.filter(t => t.symbol !== symbol));
  };

  // Actualización automática
  useEffect(() => {
    if (tickers.length === 0) return;
    const interval = setInterval(() => {
      tickers.forEach(async (ticker) => {
        try {
          const period = tickerPeriods[ticker.symbol] || '1d';
          const price = await apiService.getTickerPrice(ticker.symbol, period);
          const recommendation = await apiService.getTickerRecommendation(ticker.symbol, selectedHorizon);
          setTickers(prev => prev.map(t =>
            t.symbol === ticker.symbol
              ? { 
                  ...t, 
                  price: price.price, 
                  priceChange: price.change_percent ?? 0, 
                  recommendation: recommendation.recomendacion,
                  lastUpdate: new Date() 
                }
              : t
          ));
        } catch (error) {
          // Silenciar errores de actualización automática
        }
      });
    }, updateInterval * 1000);
    return () => clearInterval(interval);
  }, [tickers, updateInterval, tickerPeriods, selectedHorizon]);

  return (
    <div className="dashboard">
      <div className="container">
        {/* Header */}
        <div className="header">
          <h1>🎯 Dashboard de Inversiones</h1>
          <div className="header-controls">
            <span>Intervalo de actualización:</span>
            <select
              value={updateInterval}
              onChange={(e) => setUpdateInterval(Number(e.target.value))}
            >
              <option value={3}>3 segundos</option>
              <option value={5}>5 segundos</option>
              <option value={10}>10 segundos</option>
              <option value={30}>30 segundos</option>
            </select>
          </div>
        </div>
        
        {/* Selector de Horizonte */}
        <HorizonSelector 
          selectedHorizon={selectedHorizon}
          onHorizonChange={handleHorizonChange}
        />
        
        <div className="grid">
          {/* Columna izquierda - Lista de tickers */}
          <div>
            <h2 className="section-title">📈 Tickers en Seguimiento</h2>
            <TickerInput onAddTicker={handleAddTicker} isLoading={isLoading} />
            <div>
              {tickers.map((ticker) => (
                <div key={ticker.symbol} style={{ display: 'flex', alignItems: 'center', background: selectedChartSymbol === ticker.symbol ? 'rgba(102,126,234,0.15)' : 'transparent', border: selectedChartSymbol === ticker.symbol ? '2px solid #667eea' : '2px solid transparent', borderRadius: 10, marginBottom: 4, transition: 'background 0.2s, border 0.2s' }}>
                  <TickerCard
                    symbol={ticker.symbol}
                    price={ticker.price}
                    recommendation={ticker.recommendation}
                    priceChange={ticker.priceChange}
                    onClick={() => window.open(`/detalle/${ticker.symbol}`, '_blank')}
                    onRemove={() => handleRemoveTicker(ticker.symbol)}
                    isSelected={false}
                    period={tickerPeriods[ticker.symbol] || '1d'}
                    onPeriodChange={(period) => handlePeriodChange(ticker.symbol, period)}
                    hasData={ticker.hasData !== false} // true si hasData es true o undefined, false si es false
                  />
                  <button
                    title="Mostrar gráfico"
                    style={{ marginLeft: 8, fontSize: 20, background: 'none', border: 'none', cursor: 'pointer', color: '#667eea' }}
                    onClick={() => setSelectedChartSymbol(ticker.symbol)}
                  >
                    📊
                  </button>
                </div>
              ))}
            </div>
            {tickers.length === 0 && (
              <div className="empty-state">
                <p>No hay tickers en seguimiento</p>
                <p>Agrega un ticker para comenzar</p>
              </div>
            )}
          </div>
          {/* Columna derecha - Gráfico */}
          <div>
            <h2 className="section-title">📊 Gráfico de Velas</h2>
            {selectedChartSymbol ? (
              <>
                <div style={{ marginBottom: 16 }}>
                  <label style={{ fontWeight: 600, marginRight: 8 }}>Rango del gráfico:</label>
                  <select value={chartRange} onChange={e => setChartRange(e.target.value)} style={{ padding: '6px 12px', borderRadius: 6, marginRight: 12 }}>
                    {chartRangeOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                  <label style={{ fontWeight: 600, marginRight: 8 }}>Intervalo:</label>
                  <select value={chartInterval} onChange={e => setChartInterval(e.target.value)} style={{ padding: '6px 12px', borderRadius: 6 }}>
                    {chartIntervalOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div style={{ marginBottom: 32 }}>
                  <TradingViewChart
                    symbol={selectedChartSymbol}
                    interval={chartInterval}
                    theme="dark"
                    width={800}
                    height={400}
                  />
                </div>
                <div style={{ color: '#888', fontSize: 14, marginBottom: 8 }}>
                  Mostrando: <b>{selectedChartSymbol}</b>
                </div>
              </>
            ) : (
              <div className="chart-container">
                <div className="empty-state">
                  <p>Selecciona un ticker para ver el gráfico</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function TickerDetailPage() {
  const { symbol } = useParams<{ symbol: string }>();
  const navigate = useNavigate();
  const [recommendation, setRecommendation] = useState<TickerRecommendation | null>(null);
  const [price, setPrice] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [period, setPeriod] = useState<string>(() => {
    const saved = localStorage.getItem('detailPeriods');
    if (saved && symbol) {
      const obj = JSON.parse(saved);
      return obj[symbol] || '1d';
    }
    return '1d';
  });
  const [chartRange, setChartRange] = useState<string>('1mo');
  const [chartInterval, setChartInterval] = useState<string>('1d');
  // Variable eliminada: klines (LocalChart los maneja internamente)
  const chartRangeOptions = [
    { value: '1d', label: '1 Día', limit: 1 },
    { value: '1mo', label: '1 Mes', limit: 30 },
    { value: '1y', label: '1 Año', limit: 365 },
    { value: 'all', label: 'Todo', limit: 1000 },
  ];
  const chartIntervalOptions = [
    { value: '1m', label: '1 Minuto' },
    { value: '5m', label: '5 Minutos' },
    { value: '15m', label: '15 Minutos' },
    { value: '1h', label: '1 Hora' },
    { value: '4h', label: '4 Horas' },
    { value: '1d', label: '1 Día' },
    { value: '1w', label: '1 Semana' },
  ];

  // Guardar el periodo seleccionado en localStorage
  React.useEffect(() => {
    if (!symbol) return;
    const saved = localStorage.getItem('detailPeriods');
    const obj = saved ? JSON.parse(saved) : {};
    obj[symbol] = period;
    localStorage.setItem('detailPeriods', JSON.stringify(obj));
  }, [period, symbol]);

  const fetchData = React.useCallback(async () => {
    if (!symbol) return;
    console.log('Fetching data for symbol:', symbol);
    setIsLoading(true);
    try {
      console.log('Fetching recommendation for:', symbol);
      const rec = await apiService.getTickerRecommendation(symbol);
      console.log('Recommendation received:', rec);
      console.log('Soportes from API:', rec?.detalle?.soportes);
      console.log('Resistencias from API:', rec?.detalle?.resistencias);
      
      console.log('Fetching price for:', symbol, 'period:', period);
      const priceData = await apiService.getTickerPrice(symbol, period);
      console.log('Price received:', priceData);
      
      // Solo actualizar los datos si la respuesta es exitosa
      setRecommendation(rec);
      setPrice(priceData.price);
      console.log('Data set successfully for:', symbol);
    } catch (e) {
      console.error('Error fetching data for', symbol, ':', e);
      // No vaciar los datos existentes en caso de error
      // setRecommendation(null);
      // setPrice(0);
      // Mostrar un mensaje de error más amigable
      console.warn(`No se pudieron cargar los datos para ${symbol}. El servidor puede estar ocupado.`);
      // No mostrar alert inmediatamente, solo en consola
    } finally {
      console.log('Setting isLoading to false for:', symbol);
      setIsLoading(false);
    }
  }, [symbol, period]);

  // Función eliminada: fetchKlines (LocalChart los maneja internamente)

  React.useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="dashboard">
      <div className="container">
        <button onClick={() => navigate('/')} style={{ margin: '20px 0', padding: '8px 16px', borderRadius: 8, background: '#667eea', color: 'white', border: 'none', fontWeight: 600, cursor: 'pointer' }}>← Volver</button>
        <div style={{ marginBottom: 16 }}>
          <label style={{ fontWeight: 600, marginRight: 8 }}>Periodo de variación:</label>
          <select value={period} onChange={e => setPeriod(e.target.value)} style={{ padding: '6px 12px', borderRadius: 6 }}>
            <option value="1d">Último cierre</option>
            <option value="1mo">Último mes</option>
            <option value="1y">Último año</option>
            <option value="all">Desde lanzamiento</option>
          </select>
        </div>
        <div style={{ marginBottom: 16 }}>
          <label style={{ fontWeight: 600, marginRight: 8 }}>Rango del gráfico:</label>
          <select value={chartRange} onChange={e => setChartRange(e.target.value)} style={{ padding: '6px 12px', borderRadius: 6, marginRight: 12 }}>
            {chartRangeOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
          <label style={{ fontWeight: 600, marginRight: 8 }}>Intervalo:</label>
          <select value={chartInterval} onChange={e => setChartInterval(e.target.value)} style={{ padding: '6px 12px', borderRadius: 6 }}>
            {chartIntervalOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        <div style={{ marginBottom: 32 }}>
          <TradingViewChart
            symbol={symbol || ''}
            interval={chartInterval}
            theme="dark"
            width={800}
            height={400}
          />
        </div>
        <TickerDetails
          symbol={symbol || ''}
          price={price}
          recommendation={recommendation}
          isLoading={isLoading}
          onClose={() => navigate('/')}
        />
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/detalle/:symbol" element={<TickerDetailPage />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
