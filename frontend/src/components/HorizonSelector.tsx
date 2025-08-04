import React from 'react';

interface HorizonSelectorProps {
  selectedHorizon: string;
  onHorizonChange: (horizon: string) => void;
  className?: string;
}

const horizonOptions = [
  { value: '1h', label: '1 Hora', description: 'Corto plazo' },
  { value: '4h', label: '4 Horas', description: 'Muy corto plazo' },
  { value: '12h', label: '12 Horas', description: 'Corto plazo' },
  { value: '24h', label: '24 Horas', description: 'Mediano plazo' },
  { value: '7d', label: '7 Días', description: 'Largo plazo' },
  { value: '1mes', label: '1 Mes', description: 'Muy largo plazo' },
];

const HorizonSelector: React.FC<HorizonSelectorProps> = ({ 
  selectedHorizon, 
  onHorizonChange, 
  className = "" 
}) => {
  return (
    <div className={`horizon-selector ${className}`}>
      <label className="horizon-label">
        <span className="horizon-title">Horizonte de Recomendación:</span>
        <select 
          value={selectedHorizon} 
          onChange={(e) => onHorizonChange(e.target.value)}
          className="horizon-select"
        >
          {horizonOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label} - {option.description}
            </option>
          ))}
        </select>
      </label>
      <div className="horizon-info">
        <span className="horizon-current">
          Horizonte actual: <strong>{horizonOptions.find(opt => opt.value === selectedHorizon)?.label}</strong>
        </span>
        <span className="horizon-description">
          {horizonOptions.find(opt => opt.value === selectedHorizon)?.description}
        </span>
      </div>
    </div>
  );
};

export default HorizonSelector; 