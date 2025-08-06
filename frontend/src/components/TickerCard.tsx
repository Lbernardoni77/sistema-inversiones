import React, { useState } from 'react';

interface TickerCardProps {
  symbol: string;
  price: number;
  recommendation: string;
  priceChange: number;
  onClick: () => void;
  onRemove: () => void;
  isSelected: boolean;
  period?: string;
  onPeriodChange?: (period: string) => void;
  hasData?: boolean; // Nueva prop para indicar si hay datos disponibles
}

const PERIODS = [
  { value: '1d', label: '1D', desc: 'Último cierre' },
  { value: '1mo', label: '1M', desc: 'Último mes' },
  { value: '1y', label: '1A', desc: 'Último año' },
  { value: 'all', label: 'ALL', desc: 'Desde lanzamiento' },
];

const TickerCard: React.FC<TickerCardProps> = ({
  symbol,
  price,
  recommendation,
  priceChange,
  onClick,
  onRemove,
  isSelected,
  period = '1d',
  onPeriodChange,
  hasData = true, // Por defecto asumimos que hay datos
}) => {
  const [showMenu, setShowMenu] = useState(false);

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

  const getRecommendationIcon = (rec: string) => {
    switch (rec.toLowerCase()) {
      case 'comprar':
        return '📈';
      case 'vender':
        return '📉';
      default:
        return '➡️';
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const formatPriceChange = (change: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)}%`;
  };

  const handlePeriodClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowMenu((prev) => !prev);
  };

  const handleSelectPeriod = (value: string) => {
    setShowMenu(false);
    if (onPeriodChange) onPeriodChange(value);
  };

  const periodLabel = PERIODS.find(p => p.value === period)?.label || '1D';

  return (
    <div
      className={`ticker-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      style={{ padding: 12, marginBottom: 10, borderRadius: 10, position: 'relative', minWidth: 0 }}
    >
      {/* Primera fila: símbolo y recomendación */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', minWidth: 0 }}>
        <h3 className="ticker-symbol" style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{symbol}</h3>
        {hasData ? (
          <span className={`recommendation-badge ${getRecommendationColor(recommendation)}`} style={{ marginLeft: 8, fontSize: '0.95rem', minWidth: 80, textAlign: 'right' }}>
            {getRecommendationIcon(recommendation)} {recommendation}
          </span>
        ) : (
          <span style={{ marginLeft: 8, fontSize: '0.9rem', color: '#888', minWidth: 80, textAlign: 'right' }}>
            ⚠️ Sin datos
          </span>
        )}
        <button 
          className="remove-button" 
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          title="Eliminar ticker"
          style={{ marginLeft: 8, fontSize: 13, width: 22, height: 22, padding: 0, background: 'rgba(244,67,54,0.7)' }}
        >
          ✕
        </button>
      </div>
      {/* Segunda fila: precio, porcentaje y periodo */}
      {hasData ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 8, minWidth: 0 }}>
          <div className="ticker-price" style={{ fontSize: '1.1rem', fontWeight: 600, color: 'white', minWidth: 0, flex: 1 }}>{formatPrice(price)}</div>
          <div className={`price-change ${priceChange >= 0 ? 'positive' : 'negative'}`} style={{ fontWeight: 600, fontSize: '1rem', display: 'flex', alignItems: 'center', gap: 4, minWidth: 0 }}>
            {formatPriceChange(priceChange)}
            <span
              className="period-selector"
              title="Seleccionar periodo de variación"
              style={{ cursor: 'pointer', marginLeft: 4, fontWeight: 'bold', userSelect: 'none', color: '#667eea' }}
              onClick={handlePeriodClick}
            >
              📈 {periodLabel}
            </span>
            {showMenu && (
              <div className="period-menu" onClick={e => e.stopPropagation()} style={{ position: 'absolute', background: '#fff', color: '#333', border: '1px solid #ccc', borderRadius: 8, zIndex: 10, marginTop: 30, right: 0, minWidth: 120 }}>
                {PERIODS.map(p => (
                  <div
                    key={p.value}
                    className="period-menu-item"
                    style={{ padding: '8px 12px', cursor: 'pointer', background: p.value === period ? '#eee' : 'transparent' }}
                    onClick={() => handleSelectPeriod(p.value)}
                  >
                    {p.label} <span style={{ fontSize: 12, color: '#888' }}>({p.desc})</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          marginTop: 8, 
          padding: '12px',
          backgroundColor: '#1a1a1a',
          borderRadius: '6px',
          border: '1px solid #333'
        }}>
          <span style={{ color: '#888', fontSize: '0.9rem', fontWeight: 500 }}>
            📊 Datos no disponibles para este ticker
          </span>
        </div>
      )}
    </div>
  );
};

export default TickerCard; 