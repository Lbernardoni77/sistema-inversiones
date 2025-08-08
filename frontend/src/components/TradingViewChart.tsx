import React, { useEffect, useRef } from 'react';

interface TradingViewChartProps {
  symbol: string;
  interval?: string;
  theme?: 'light' | 'dark';
  width?: number;
  height?: number;
}

declare global {
  interface Window {
    TradingView: any;
  }
}

const TradingViewChart: React.FC<TradingViewChartProps> = ({
  symbol,
  interval = '1D',
  theme = 'dark',
  width = 800,
  height = 400
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Cargar el script de TradingView si no está cargado
    if (!window.TradingView) {
      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/tv.js';
      script.async = true;
      script.onload = createWidget;
      document.head.appendChild(script);
    } else {
      createWidget();
    }

    function createWidget() {
      if (containerRef.current && window.TradingView) {
        // Limpiar el contenedor
        containerRef.current.innerHTML = '';

        // Mapear símbolos a formatos correctos para TradingView
        const symbolMapping: { [key: string]: string } = {
          'BTCUSDT': 'BINANCE:BTCUSDT',
          'ETHUSDT': 'BINANCE:ETHUSDT',
          'ADAUSDT': 'BINANCE:ADAUSDT',
          'SOLUSDT': 'BINANCE:SOLUSDT',
          'MATICUSDT': 'BINANCE:MATICUSDT',
          'DOTUSDT': 'BINANCE:DOTUSDT',
          'SHIBUSDT': 'BINANCE:SHIBUSDT',
          'SANDUSDT': 'BINANCE:SANDUSDT',
          'THETAUSDT': 'BINANCE:THETAUSDT',
          'MANAUSDT': 'BINANCE:MANAUSDT',
          'SUSDT': 'BINANCE:SUSDT'
        };

        const tradingViewSymbol = symbolMapping[symbol] || `BINANCE:${symbol}`;

        try {
          new window.TradingView.widget({
            autosize: true,
            symbol: tradingViewSymbol,
            interval: interval,
            timezone: 'America/New_York',
            theme: theme,
            style: '1',
            locale: 'es',
            toolbar_bg: '#f1f3f6',
            enable_publishing: false,
            allow_symbol_change: false,
            container_id: containerRef.current.id,
            width: width,
            height: height,
            studies: [
              'RSI@tv-basicstudies',
              'MACD@tv-basicstudies',
              'BB@tv-basicstudies'
            ],
            disabled_features: [
              'use_localstorage_for_settings',
              'volume_force_overlay'
            ],
            enabled_features: [
              'study_templates'
            ],
            overrides: {
              'mainSeriesProperties.candleStyle.upColor': '#26a69a',
              'mainSeriesProperties.candleStyle.downColor': '#ef5350',
              'mainSeriesProperties.candleStyle.wickUpColor': '#26a69a',
              'mainSeriesProperties.candleStyle.wickDownColor': '#ef5350'
            }
          });
        } catch (error) {
          console.error('Error creating TradingView widget:', error);
          // Mostrar mensaje de error en el contenedor
          if (containerRef.current) {
            containerRef.current.innerHTML = `
              <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">
                <div style="text-align: center;">
                  <p>No se pudo cargar el gráfico para ${symbol}</p>
                  <p style="font-size: 12px;">Error: ${error}</p>
                </div>
              </div>
            `;
          }
        }
      }
    }

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [symbol, interval, theme, width, height]);

  return (
    <div 
      ref={containerRef}
      id={`tradingview-widget-${symbol}`}
      style={{ width: '100%', height: `${height}px` }}
    />
  );
};

export default TradingViewChart;
