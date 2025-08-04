import React from 'react';
import { TickerRecommendation } from '../services/api';

interface TickerDetailsProps {
  symbol: string;
  price: number;
  recommendation: TickerRecommendation | null;
  isLoading: boolean;
  onClose: () => void;
}

const TickerDetails: React.FC<TickerDetailsProps> = ({
  symbol,
  price,
  recommendation,
  isLoading,
  onClose,
}) => {
  if (isLoading) {
    return (
      <div className="ticker-details-overlay" onClick={onClose}>
        <div className="ticker-details-modal" onClick={(e) => e.stopPropagation()}>
          <div className="ticker-details-header">
            <h2>{symbol} - Detalles</h2>
            <button className="close-button" onClick={onClose}>✕</button>
          </div>
          <div className="ticker-details-content" style={{textAlign: 'center', padding: '40px'}}>
            <div style={{fontSize: '2rem', marginBottom: '10px'}}>⏳</div>
            <div>Cargando detalles...</div>
          </div>
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return (
      <div className="ticker-details-overlay" onClick={onClose}>
        <div className="ticker-details-modal" onClick={(e) => e.stopPropagation()}>
          <div className="ticker-details-header">
            <h2>{symbol} - Detalles</h2>
            <button className="close-button" onClick={onClose}>✕</button>
          </div>
          <div className="ticker-details-content">
            <p>Cargando detalles...</p>
          </div>
        </div>
      </div>
    );
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const getRecommendationColor = (rec: string) => {
    switch (rec.toLowerCase()) {
      case 'comprar':
        return 'recommendation-buy';
      case 'vender':
        return 'recommendation-sell';
      default:
        return 'recommendation-hold';
    }
  };

  return (
    <div className="ticker-details-overlay" onClick={onClose}>
      <div className="ticker-details-modal" onClick={(e) => e.stopPropagation()}>
        <div className="ticker-details-header">
          <h2>{symbol} - Detalles</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>
        
        <div className="ticker-details-content">
          {/* Precio actual */}
          <div className="detail-section">
            <h3>💰 Precio Actual</h3>
            <div className="current-price">{formatPrice(price)}</div>
          </div>

          {/* Recomendación principal */}
          <div className="detail-section">
            <h3>🎯 Recomendación</h3>
            <div className={`main-recommendation ${getRecommendationColor(recommendation.recomendacion)}`}>
              {recommendation.recomendacion}
            </div>
          </div>

          {/* Resumen de ponderación */}
          {recommendation.detalle.resumen_ponderacion && (
            <div className="detail-section">
              <h3>⚖️ Resumen de Ponderación</h3>
              <div className="weight-summary">
                <div className="weight-item">
                  <strong>Indicadores Técnicos:</strong> {recommendation.detalle.resumen_ponderacion.peso_indicadores_tecnicos}
                </div>
                <div className="weight-item">
                  <strong>Soportes/Resistencias:</strong> {recommendation.detalle.resumen_ponderacion.peso_soportes_resistencias}
                </div>
                <div className="weight-item">
                  <strong>Sentimiento:</strong> {recommendation.detalle.resumen_ponderacion.peso_sentimiento}
                </div>
                <div className="weight-item">
                  <strong>Explicación:</strong> {recommendation.detalle.resumen_ponderacion.explicacion}
                </div>
                {/* Mostrar detalle de influencia de cada indicador */}
                {recommendation.detalle.resumen_ponderacion.detalle_influencia && (
                  <div className="weight-item">
                    <strong>Influencia de cada indicador:</strong>
                    <ul style={{ marginTop: 4 }}>
                      {Object.entries(recommendation.detalle.resumen_ponderacion.detalle_influencia).map(([key, value]) => (
                        <li key={key}><strong>{key}:</strong> {value as string}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Motivos */}
          {recommendation.detalle.motivo && recommendation.detalle.motivo.length > 0 && (
            <div className="detail-section">
              <h3>📊 Motivos de la Recomendación</h3>
              <ul className="motivos-list">
                {recommendation.detalle.motivo.map((motivo, index) => (
                  <li key={index}>{motivo}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Indicadores técnicos */}
          <div className="detail-section">
            <h3>📈 Indicadores Técnicos</h3>
            <div className="indicators-grid">
              {recommendation.detalle.indicadores.rsi && (
                <div className="indicator-item">
                  <span className="indicator-label">RSI:</span>
                  <span className="indicator-value">{recommendation.detalle.indicadores.rsi.toFixed(2)}</span>
                </div>
              )}
              {recommendation.detalle.indicadores.sma_7 && (
                <div className="indicator-item">
                  <span className="indicator-label">SMA 7:</span>
                  <span className="indicator-value">{formatPrice(recommendation.detalle.indicadores.sma_7)}</span>
                </div>
              )}
              {recommendation.detalle.indicadores.sma_21 && (
                <div className="indicator-item">
                  <span className="indicator-label">SMA 21:</span>
                  <span className="indicator-value">{formatPrice(recommendation.detalle.indicadores.sma_21)}</span>
                </div>
              )}
              {recommendation.detalle.indicadores.macd && (
                <div className="indicator-item">
                  <span className="indicator-label">MACD:</span>
                  <span className="indicator-value">{recommendation.detalle.indicadores.macd.toFixed(2)}</span>
                </div>
              )}
              {recommendation.detalle.indicadores.sharpe_ratio && (
                <div className="indicator-item">
                  <span className="indicator-label">Sharpe Ratio:</span>
                  <span className="indicator-value">{recommendation.detalle.indicadores.sharpe_ratio.toFixed(2)}</span>
                </div>
              )}
            </div>
          </div>

          {/* Soportes y resistencias */}
          {/* Mostramos los niveles si existen en la respuesta */}
          {(recommendation.detalle.soportes && recommendation.detalle.soportes.length > 0) || (recommendation.detalle.resistencias && recommendation.detalle.resistencias.length > 0) ? (
            <div className="detail-section">
              <h3>🛡️ Soportes y Resistencias</h3>
              {recommendation.detalle.soportes && recommendation.detalle.soportes.length > 0 && (
                <div style={{ marginBottom: '10px' }}>
                  <strong>Soportes:</strong>
                  <ol>
                    {recommendation.detalle.soportes.map((s, idx) => (
                      <li key={idx}>{formatPrice(s)}</li>
                    ))}
                  </ol>
                </div>
              )}
              {recommendation.detalle.resistencias && recommendation.detalle.resistencias.length > 0 && (
                <div>
                  <strong>Resistencias:</strong>
                  <ol>
                    {recommendation.detalle.resistencias.map((r, idx) => (
                      <li key={idx}>{formatPrice(r)}</li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          ) : null}

          {/* Sentimiento */}
          {recommendation.detalle.sentimiento && (
            <div className="detail-section">
              <h3>😱 Sentimiento de Mercado</h3>
              <div className="sentiment-info">
                {recommendation.detalle.sentimiento.fear_and_greed && (
                  <div className="sentiment-item">
                    <strong>Fear & Greed Index:</strong> {typeof recommendation.detalle.sentimiento.fear_and_greed.value === 'string' || typeof recommendation.detalle.sentimiento.fear_and_greed.value === 'number' ? recommendation.detalle.sentimiento.fear_and_greed.value : 'N/A'}
                  </div>
                )}
                {recommendation.detalle.sentimiento.noticias && (
                  <div className="sentiment-item">
                    <strong>Sentimiento Noticias:</strong> {typeof recommendation.detalle.sentimiento.noticias.score === 'number' ? recommendation.detalle.sentimiento.noticias.score.toFixed(2) : 'N/A'}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Noticias recientes */}
          {recommendation.detalle.noticias && recommendation.detalle.noticias.length > 0 && (
            <div className="detail-section">
              <h3>📰 Noticias Recientes</h3>
              <div className="news-list">
                {recommendation.detalle.noticias.slice(0, 3).map((noticia, index) => (
                  <div key={index} className="news-item">
                    <div className="news-title">{noticia.title}</div>
                    <div className="news-source">
                      {typeof noticia.source === 'string'
                        ? noticia.source
                        : noticia.source && noticia.source.name
                          ? noticia.source.name
                          : JSON.stringify(noticia.source)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TickerDetails; 