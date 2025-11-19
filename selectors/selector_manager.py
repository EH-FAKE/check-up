from datetime import datetime
from typing import List, Dict
import json

class SelectorVersion:
    """Representa uma versão de um seletor"""
    
    def __init__(self, selector: str, description: str = ""):
        self.selector = selector
        self.description = description
        self.created_at = datetime.utcnow()
        self.status = 'active'  # active, deprecated, broken
        self.last_tested = None
        self.success_rate = 1.0
    
    def to_dict(self):
        return {
            'selector': self.selector,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'status': self.status,
            'last_tested': self.last_tested.isoformat() if self.last_tested else None,
            'success_rate': self.success_rate,
        }

class SelectorsRegistry:
    """
    Registry centralizado de seletores com histórico de versões
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.selectors_cache = {}
    
    def add_selector(self, scraper_name: str, field: str, selector: str, 
                    description: str = "", is_fallback: bool = False):
        """Adiciona novo seletor ao registro"""
        
        version = SelectorVersion(selector, description)
        
        self.db.execute("""
            INSERT INTO selector_versions 
            (scraper_name, field, selector, description, created_at, status, is_fallback)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (scraper_name, field, selector, description, version.created_at, 
              'active', is_fallback))
        
        # Invalidar cache
        del self.selectors_cache[f"{scraper_name}:{field}"]
    
    def get_selectors(self, scraper_name: str, field: str) -> List[str]:
        """
        Retorna lista de seletores ordenados por:
        1. Status (active > deprecated)
        2. Taxa de sucesso (maior primeiro)
        3. Recente primeiro
        """
        
        cache_key = f"{scraper_name}:{field}"
        if cache_key in self.selectors_cache:
            return self.selectors_cache[cache_key]
        
        rows = self.db.query("""
            SELECT selector, status, success_rate
            FROM selector_versions
            WHERE scraper_name = %s AND field = %s
            ORDER BY 
                CASE status 
                    WHEN 'active' THEN 1 
                    WHEN 'deprecated' THEN 2 
                    WHEN 'broken' THEN 3 
                END,
                success_rate DESC,
                created_at DESC
        """, (scraper_name, field))
        
        selectors = [row['selector'] for row in rows if row['status'] != 'broken']
        self.selectors_cache[cache_key] = selectors
        
        return selectors
    
    def mark_selector_broken(self, scraper_name: str, field: str, selector: str):
        """Marca um seletor como quebrado"""
        
        self.db.execute("""
            UPDATE selector_versions
            SET status = 'broken'
            WHERE scraper_name = %s AND field = %s AND selector = %s
        """, (scraper_name, field, selector))
        
        del self.selectors_cache[f"{scraper_name}:{field}"]
    
    def update_selector_success_rate(self, scraper_name: str, field: str, 
                                     selector: str, success_rate: float):
        """Atualiza taxa de sucesso de um seletor"""
        
        self.db.execute("""
            UPDATE selector_versions
            SET success_rate = %s, last_tested = %s
            WHERE scraper_name = %s AND field = %s AND selector = %s
        """, (success_rate, datetime.utcnow(), scraper_name, field, selector))
    
    def export_selectors_config(self, scraper_name: str) -> Dict:
        """Exporta configuração de seletores para spider"""
        
        fields = self.db.query("""
            SELECT DISTINCT field FROM selector_versions
            WHERE scraper_name = %s AND status != 'broken'
        """, (scraper_name,))
        
        config = {}
        for row in fields:
            field = row['field']
            config[field] = self.get_selectors(scraper_name, field)
        
        return config
