from datetime import datetime, timedelta
from typing import Dict, List
import logging

class ScraperHealthMonitor:
    """
    Monitora saúde dos scrapers e envia alertas
    """
    
    def __init__(self, db_connection, alert_service):
        self.db = db_connection
        self.alert_service = alert_service
        self.logger = logging.getLogger(__name__)
        self.thresholds = {
            'success_rate': 0.70,  # Mínimo 70% de sucesso
            'max_failures': 3,      # Máximo 3 falhas consecutivas
            'stale_data': 24,       # Dados com mais de 24h são antigos
        }
    
    def check_all_scrapers(self) -> Dict[str, Dict]:
        """
        Verifica saúde de todos os scrapers
        """
        scrapers = self.db.get_all_scrapers()
        health_report = {}
        
        for scraper in scrapers:
            health = self.check_scraper_health(scraper['name'])
            health_report[scraper['name']] = health
            
            # Enviar alerta se necessário
            if health['status'] == 'CRITICAL':
                self.alert_service.send_alert({
                    'scraper': scraper['name'],
                    'status': health['status'],
                    'reason': health['reason'],
                    'last_success': health['last_success'],
                    'consecutive_failures': health['consecutive_failures'],
                })
        
        return health_report
    
    def check_scraper_health(self, scraper_name: str) -> Dict:
        """
        Verifica saúde individual de um scraper
        """
        metrics = self.db.get_scraper_metrics(scraper_name, hours=24)
        
        if not metrics:
            return {
                'status': 'UNKNOWN',
                'reason': 'Nenhuma métrica disponível',
                'last_success': None,
            }
        
        total_runs = len(metrics)
        successful_runs = len([m for m in metrics if m['success']])
        success_rate = successful_runs / total_runs if total_runs > 0 else 0
        
        # Calcular falhas consecutivas
        consecutive_failures = 0
        for metric in reversed(metrics):
            if metric['success']:
                break
            consecutive_failures += 1
        
        last_success = self._get_last_success(metrics)
        hours_since_success = self._hours_since(last_success) if last_success else None
        
        # Determinar status
        status = 'HEALTHY'
        reason = 'Funcionando normalmente'
        
        if consecutive_failures >= self.thresholds['max_failures']:
            status = 'CRITICAL'
            reason = f'{consecutive_failures} falhas consecutivas'
        elif success_rate < self.thresholds['success_rate']:
            status = 'DEGRADED'
            reason = f'Taxa de sucesso baixa: {success_rate:.1%}'
        elif hours_since_success and hours_since_success > self.thresholds['stale_data']:
            status = 'STALE'
            reason = f'Sem dados frescos há {hours_since_success}h'
        
        return {
            'status': status,
            'reason': reason,
            'success_rate': success_rate,
            'consecutive_failures': consecutive_failures,
            'total_runs_24h': total_runs,
            'last_success': last_success,
            'hours_since_success': hours_since_success,
        }
    
    def _get_last_success(self, metrics: List) -> datetime:
        for metric in reversed(metrics):
            if metric['success']:
                return metric['timestamp']
        return None
    
    def _hours_since(self, dt: datetime) -> float:
        if not dt:
            return None
        return (datetime.utcnow() - dt).total_seconds() / 3600

# alerts/alert_service.py
class AlertService:
    """Serviço de alertas (integra com Slack, Email, etc)"""
    
    def __init__(self, slack_webhook=None, email_config=None):
        self.slack_webhook = slack_webhook
        self.email_config = email_config
    
    def send_alert(self, alert_data: Dict):
        """Envia alerta para múltiplos canais"""
        message = self._format_alert(alert_data)
        
        if self.slack_webhook:
            self._send_slack(message)
        
        if self.email_config:
            self._send_email(message, alert_data)
    
    def _format_alert(self, alert_data: Dict) -> str:
        return f"""
        ⚠️  ALERTA DE SCRAPER
        
        Scraper: {alert_data['scraper']}
        Status: {alert_data['status']}
        Motivo: {alert_data['reason']}
        Último sucesso: {alert_data['last_success']}
        Falhas consecutivas: {alert_data['consecutive_failures']}
        """
    
    def _send_slack(self, message: str):
        import requests
        requests.post(self.slack_webhook, json={'text': message})
    
    def _send_email(self, message: str, alert_data: Dict):
        # Implementar envio de email
        pass
