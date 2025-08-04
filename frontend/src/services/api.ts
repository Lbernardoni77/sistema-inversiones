import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Aumentado a 30 segundos
});

export interface TickerPrice {
  symbol: string;
  price: number;
  close_yesterday?: number;
  change_percent?: number;
}

export interface TickerRecommendation {
  recomendacion: string;
  horizonte?: string;
  detalle: {
    motivo: string[];
    indicadores: {
      rsi: number | null;
      sma_7: number | null;
      sma_21: number | null;
      sma_50: number | null;
      sma_200: number | null;
      macd: number | null;
      macd_signal: number | null;
      macd_hist: number | null;
      bb_upper: number | null;
      bb_mid: number | null;
      bb_lower: number | null;
      obv: number | null;
      vwap: number | null;
      sharpe_ratio: number | null;
    };
    soportes?: number[];
    resistencias?: number[];
    fundamental: any;
    onchain: any;
    sentimiento: any;
    noticias: any[];
    resumen_ponderacion: any;
  };
}

export interface TickerRecommendationSummary {
  symbol: string;
  recomendacion: string;
  horizonte: string;
  precio: number;
  indicadores: {
    rsi: number | null;
    macd: number | null;
    sma_7: number | null;
    sma_21: number | null;
    sma_50: number | null;
    sma_200: number | null;
  };
  soportes: number[];
  resistencias: number[];
  error?: string;
}

export const apiService = {
  // Obtener precio de un ticker
  getTickerPrice: async (symbol: string, period: string = '1d'): Promise<TickerPrice> => {
    const response = await api.get(`/binance/price/${symbol}?period=${period}`);
    return response.data;
  },

  // Obtener recomendación completa de un ticker
  getTickerRecommendation: async (symbol: string, horizonte: string = "24h"): Promise<TickerRecommendation> => {
    const response = await api.get(`/binance/recommendation/${symbol}?horizonte=${horizonte}`);
    return response.data;
  },

  // Obtener datos históricos para gráficos (placeholder)
  getTickerHistory: async (symbol: string, interval: string = '1h', limit: number = 100) => {
    // Por ahora retornamos datos simulados
    // En el futuro se puede conectar con el endpoint de klines del backend
    return [];
  },

  // Obtener klines para el gráfico de velas
  getKlines: async (symbol: string, interval: string = '1d', limit: number = 30) => {
    const response = await api.get(`/binance/klines/${symbol}?interval=${interval}&limit=${limit}`);
    return response.data;
  },

  // Agregar ticker a la base de datos del backend
  addTickerToBackend: async (symbol: string): Promise<{ok: boolean, msg: string}> => {
    const response = await api.post(`/tickers/add?symbol=${symbol}`);
    return response.data;
  },

  // Eliminar ticker de la base de datos del backend
  removeTickerFromBackend: async (symbol: string): Promise<{ok: boolean, msg: string}> => {
    const response = await api.post(`/tickers/remove?symbol=${symbol}`);
    return response.data;
  },

  // Obtener lista de tickers desde la base de datos del backend
  getTickersFromBackend: async (): Promise<{tickers: string[]}> => {
    const response = await api.get('/tickers/list');
    return response.data;
  },

  // Obtener recomendaciones para todos los tickers con un horizonte específico
  getTickersRecommendations: async (horizonte: string = "24h"): Promise<{horizonte: string, resultados: TickerRecommendationSummary[]}> => {
    const response = await api.get(`/tickers/recommendations?horizonte=${horizonte}`);
    return response.data;
  },
};

export default apiService; 