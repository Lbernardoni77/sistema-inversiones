import React, { useState } from 'react';

interface TickerInputProps {
  onAddTicker: (symbol: string) => void;
  isLoading?: boolean;
}

const TickerInput: React.FC<TickerInputProps> = ({ onAddTicker, isLoading = false }) => {
  const [symbol, setSymbol] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (symbol.trim()) {
      onAddTicker(symbol.trim().toUpperCase());
      setSymbol('');
    }
  };

  return (
    <div className="ticker-input">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="Ingresa un ticker (ej: BTCUSDT)"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!symbol.trim() || isLoading}
        >
          {isLoading ? '⏳' : '➕'}
        </button>
      </form>
    </div>
  );
};

export default TickerInput; 