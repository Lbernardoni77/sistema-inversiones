#!/usr/bin/env python3
"""
Servicio de cache para optimizar el rendimiento de las recomendaciones
"""
import json
import time
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import os

class RecommendationCache:
    """Cache simple para recomendaciones con expiración"""
    
    def __init__(self, cache_duration_minutes: int = 10):
        self.cache_duration = cache_duration_minutes * 60  # Convertir a segundos
        self.cache_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'recommendation_cache.json')
        self._ensure_cache_file()
    
    def _ensure_cache_file(self):
        """Asegura que el archivo de cache existe"""
        cache_dir = os.path.dirname(self.cache_file)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        if not os.path.exists(self.cache_file):
            self._save_cache({})
    
    def _load_cache(self) -> Dict:
        """Carga el cache desde archivo"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_cache(self, cache_data: Dict):
        """Guarda el cache en archivo"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando cache: {e}")
    
    def get(self, key: str) -> Optional[Dict]:
        """Obtiene un valor del cache si no ha expirado"""
        cache = self._load_cache()
        
        if key not in cache:
            return None
        
        cache_entry = cache[key]
        timestamp = cache_entry.get('timestamp', 0)
        current_time = time.time()
        
        # Verificar si ha expirado
        if current_time - timestamp > self.cache_duration:
            # Eliminar entrada expirada
            del cache[key]
            self._save_cache(cache)
            return None
        
        return cache_entry.get('data')
    
    def set(self, key: str, data: Dict):
        """Guarda un valor en el cache con timestamp"""
        cache = self._load_cache()
        
        cache[key] = {
            'data': data,
            'timestamp': time.time(),
            'created_at': datetime.now().isoformat()
        }
        
        self._save_cache(cache)
    
    def clear_expired(self):
        """Limpia entradas expiradas del cache"""
        cache = self._load_cache()
        current_time = time.time()
        expired_keys = []
        
        for key, entry in cache.items():
            timestamp = entry.get('timestamp', 0)
            if current_time - timestamp > self.cache_duration:
                expired_keys.append(key)
        
        for key in expired_keys:
            del cache[key]
        
        if expired_keys:
            self._save_cache(cache)
            print(f"Cache limpiado: {len(expired_keys)} entradas expiradas eliminadas")
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del cache"""
        cache = self._load_cache()
        current_time = time.time()
        active_entries = 0
        expired_entries = 0
        
        for entry in cache.values():
            timestamp = entry.get('timestamp', 0)
            if current_time - timestamp <= self.cache_duration:
                active_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(cache),
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'cache_duration_minutes': self.cache_duration // 60
        }

# Instancia global del cache
recommendation_cache = RecommendationCache(cache_duration_minutes=10)

def get_cached_recommendation(symbol: str, horizonte: str) -> Optional[Dict]:
    """Obtiene una recomendación del cache"""
    cache_key = f"{symbol}_{horizonte}"
    return recommendation_cache.get(cache_key)

def cache_recommendation(symbol: str, horizonte: str, data: Dict):
    """Guarda una recomendación en el cache"""
    cache_key = f"{symbol}_{horizonte}"
    recommendation_cache.set(cache_key, data)

def get_cache_stats() -> Dict:
    """Obtiene estadísticas del cache"""
    return recommendation_cache.get_stats()

def clear_expired_cache():
    """Limpia el cache expirado"""
    recommendation_cache.clear_expired() 