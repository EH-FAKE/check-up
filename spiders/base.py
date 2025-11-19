import scrapy
from selectors.selector_manager import SelectorsRegistry

class BaseSpider(scrapy.Spider):
    """
    Spider base que usa SelectorsRegistry para fallback automático
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selector_registry = SelectorsRegistry(db)
        self.selector_history = {}
    
    def extract_field(self, response, field: str, fallback_text: str = ""):
        """Tenta extrair campo usando múltiplos seletores em ordem"""
        
        selectors = self.selector_registry.get_selectors(self.name, field)
        
        for i, selector in enumerate(selectors):
            try:
                extracted = response.css(selector)
                
                if extracted:
                    self.selector_history[field] = {
                        'selector': selector,
                        'attempt': i + 1,
                    }
                    return extracted.get()
                    
            except Exception as e:
                self.logger.warning(
                    f"Seletor falhou para {field}: {selector} - {str(e)}"
                )
                continue
        
        self.logger.error(f"Nenhum seletor funcionou para {field}")
        return fallback_text
