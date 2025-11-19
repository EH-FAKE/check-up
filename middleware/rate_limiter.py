from datetime import datetime, timedelta
from collections import deque
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"        # Funcionando normalmente
    OPEN = "open"            # Falhas detectadas, não fazer requisições
    HALF_OPEN = "half_open"  # Testando se voltou ao normal

class RateLimiter:
    """
    Rate limiter com histórico de requisições
    Implementa token bucket algorithm
    """
    
    def __init__(self, requests_per_minute: int = 20):
        self.rate = requests_per_minute / 60  # requests per second
        self.tokens = requests_per_minute
        self.last_update = time.time()
        self.request_history = deque(maxlen=100)
    
    def acquire(self, wait: bool = True) -> bool:
        """
        Adquire permissão para fazer requisição
        """
        now = time.time()
        elapsed = now - self.last_update
        
        # Adicionar tokens baseado no tempo passado
        self.tokens = min(
            self.rate * (self.tokens + elapsed * self.rate),
            self.rate
        )
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            self.request_history.append(now)
            return True
        elif wait:
            sleep_time = (1 - self.tokens) / self.rate
            time.sleep(sleep_time)
            return self.acquire(wait=False)
        else:
            return False
    
    def get_wait_time(self) -> float:
        """Retorna tempo em segundos até próxima requisição"""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.rate * (self.tokens + elapsed * self.rate),
            self.rate
        )
        
        if self.tokens >= 1:
            return 0
        return (1 - self.tokens) / self.rate

class CircuitBreaker:
    """
    Circuit breaker para proteger contra cascatas de falhas
    """
    
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout  # segundos
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.opened_at = None
    
    def record_success(self):
        """Registra sucesso"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 2:
                self.close()
        else:
            self.failure_count = 0
    
    def record_failure(self):
        """Registra falha"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.open()
    
    def open(self):
        """Abre o circuit breaker"""
        self.state = CircuitState.OPEN
        self.opened_at = datetime.utcnow()
        self.failure_count = 0
    
    def close(self):
        """Fecha o circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.opened_at = None
    
    def half_open(self):
        """Muda para half-open (testando recuperação)"""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
    
    def can_execute(self) -> bool:
        """Determina se pode fazer requisição"""
        
        if self.state == CircuitState.CLOSED:
            return True
        
        elif self.state == CircuitState.OPEN:
            # Verificar se timeout de recuperação passou
            elapsed = datetime.utcnow() - self.opened_at
            if elapsed.total_seconds() > self.recovery_timeout:
                self.half_open()
                return True
            return False
        
        elif self.state == CircuitState.HALF_OPEN:
            # Permitir algumas requisições de teste
            return True
        
        return False
    
    def get_status(self) -> dict:
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'last_failure': self.last_failure_time.isoformat() if self.last_failure_time else None,
        }
