"""
Prometheus metrics collection for observability.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from typing import Dict, Any
import time

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size',
    ['method', 'endpoint']
)

# Automation metrics
automation_jobs_total = Counter(
    'automation_jobs_total',
    'Total automation jobs',
    ['status']
)

automation_job_duration_seconds = Histogram(
    'automation_job_duration_seconds',
    'Automation job duration',
    ['job_type']
)

automation_job_steps_total = Counter(
    'automation_job_steps_total',
    'Total automation job steps',
    ['step', 'status']
)

# Notion metrics
notion_requests_total = Counter(
    'notion_requests_total',
    'Total Notion API requests',
    ['operation', 'status']
)

notion_request_duration_seconds = Histogram(
    'notion_request_duration_seconds',
    'Notion API request duration',
    ['operation']
)

# Vercel metrics
vercel_deployments_total = Counter(
    'vercel_deployments_total',
    'Total Vercel deployments',
    ['status']
)

vercel_deployment_duration_seconds = Histogram(
    'vercel_deployment_duration_seconds',
    'Vercel deployment duration'
)

# Cost metrics
ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI API requests',
    ['model', 'status']
)

ai_tokens_total = Counter(
    'ai_tokens_total',
    'Total AI tokens used',
    ['model']
)

ai_cost_usd = Histogram(
    'ai_cost_usd',
    'AI API cost in USD',
    ['model']
)

# System metrics
active_users = Gauge(
    'active_users',
    'Currently active users'
)

active_jobs = Gauge(
    'active_jobs',
    'Currently active jobs'
)

database_connections = Gauge(
    'database_connections',
    'Current database connections'
)


class MetricsCollector:
    """Collect and expose metrics."""
    
    @staticmethod
    def record_http_request(method: str, endpoint: str, status: int, duration: float, size: int = 0):
        """Record HTTP request metrics."""
        http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
        if size > 0:
            http_request_size_bytes.labels(method=method, endpoint=endpoint).observe(size)
    
    @staticmethod
    def record_automation_job(job_type: str, status: str, duration: float):
        """Record automation job metrics."""
        automation_jobs_total.labels(status=status).inc()
        automation_job_duration_seconds.labels(job_type=job_type).observe(duration)
    
    @staticmethod
    def record_automation_step(step: str, status: str):
        """Record automation step metrics."""
        automation_job_steps_total.labels(step=step, status=status).inc()
    
    @staticmethod
    def record_notion_request(operation: str, status: str, duration: float):
        """Record Notion API request metrics."""
        notion_requests_total.labels(operation=operation, status=status).inc()
        notion_request_duration_seconds.labels(operation=operation).observe(duration)
    
    @staticmethod
    def record_vercel_deployment(status: str, duration: float):
        """Record Vercel deployment metrics."""
        vercel_deployments_total.labels(status=status).inc()
        vercel_deployment_duration_seconds.observe(duration)
    
    @staticmethod
    def record_ai_request(model: str, status: str, tokens: int = 0, cost: float = 0):
        """Record AI API request metrics."""
        ai_requests_total.labels(model=model, status=status).inc()
        if tokens > 0:
            ai_tokens_total.labels(model=model).inc(tokens)
        if cost > 0:
            ai_cost_usd.labels(model=model).observe(cost)
    
    @staticmethod
    def set_active_users(count: int):
        """Set active users count."""
        active_users.set(count)
    
    @staticmethod
    def set_active_jobs(count: int):
        """Set active jobs count."""
        active_jobs.set(count)
    
    @staticmethod
    def set_database_connections(count: int):
        """Set database connections count."""
        database_connections.set(count)
    
    @staticmethod
    def get_metrics():
        """Get metrics in Prometheus format."""
        return generate_latest()
    
    @staticmethod
    def get_metrics_dict() -> Dict[str, Any]:
        """Get metrics as dictionary (for JSON API)."""
        from prometheus_client import CollectorRegistry, REGISTRY
        
        metrics_dict = {}
        for metric_family in REGISTRY.collect():
            metrics_dict[metric_family.name] = {
                'type': metric_family.type,
                'samples': [
                    {
                        'labels': sample.labels,
                        'value': sample.value
                    }
                    for sample in metric_family.samples
                ]
            }
        
        return metrics_dict

