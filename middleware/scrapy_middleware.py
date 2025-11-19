# middleware/scrapy_middleware.py
from scrapy import signals
from scrapy.exceptions import IgnoreRequest

class RateLimitMiddleware:
    """Middleware Scrapy que aplica rate limiting e circuit breaker"""
    
    def __init__(self, crawler):
        self.crawler = crawler
        self.rate_limiters = {}  # Por domínio
        self.circuit_breakers = {}  # Por domínio
        
        crawler.signals.connect(
            self.spider_opened,
            signal=signals.spider_opened
        )
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)
    
    def spider_opened(self, spider):
        self.logger = spider.logger
    
    def process_request(self, request, spider):
        """Aplicar rate limiting antes de fazer requisição"""
        
        domain = request.url.split('/')[2]
        
        # Inicializar se necessário
        if domain not in self.rate_limiters:
            self.rate_limiters[domain] = RateLimiter(requests_per_minute=30)
        if domain not in self.circuit_breakers:
            self.circuit_breakers[domain] = CircuitBreaker()
        
        breaker = self.circuit_breakers[domain]
        
        # Verificar circuit breaker
        if not breaker.can_execute():
            self.logger.warning(
                f"Circuit breaker aberto para {domain}. "
                f"Status: {breaker.get_status()}"
            )
            raise IgnoreRequest(f"Circuit breaker aberto para {domain}")
        
        # Aplicar rate limiting
        limiter = self.rate_limiters[domain]
        wait_time = limiter.get_wait_time()
        
        if wait_time > 0:
            self.logger.debug(f"Rate limiting: aguardando {wait_time:.2f}s")
            time.sleep(wait_time)
        
        limiter.acquire()
        return None
    
    def process_response(self, request, response, spider):
        """Registrar resultado para circuit breaker"""
        
        domain = request.url.split('/')[2]
        breaker = self.circuit_breakers.get(domain)
        
        if not breaker:
            return response
        
        # 429 = Too Many Requests (rate limiting)
        # 403 = Forbidden (possível bloqueio)
        # 5xx = Server errors
        if response.status in [429, 403, 500, 502, 503]:
            breaker.record_failure()
            self.logger.warning(
                f"Falha detectada para {domain}: HTTP {response.status}"
            )
        else:
            breaker.record_success()
        
        return response
    
    def process_exception(self, request, exception, spider):
        """Registrar exceções para circuit breaker"""
        
        domain = request.url.split('/')[2]
        breaker = self.circuit_breakers.get(domain)
        
        if breaker:
            breaker.record_failure()
            spider.logger.warning(
                f"Exceção para {domain}: {str(exception)}"
            )
        
        return None
