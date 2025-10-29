# 📊 Observability Guide (Option D)

## Overview

Complete observability setup with Prometheus metrics and Sentry error tracking.

## Features

### 1. Prometheus Metrics

#### Metrics Collected

**HTTP Metrics:**
- `http_requests_total` - Total requests by method, endpoint, status
- `http_request_duration_seconds` - Request duration histogram
- `http_request_size_bytes` - Request size histogram

**Automation Metrics:**
- `automation_jobs_total` - Total jobs by status
- `automation_job_duration_seconds` - Job duration by type
- `automation_job_steps_total` - Steps by name and status

**Notion Metrics:**
- `notion_requests_total` - Notion API requests
- `notion_request_duration_seconds` - Notion API duration

**Vercel Metrics:**
- `vercel_deployments_total` - Deployments by status
- `vercel_deployment_duration_seconds` - Deployment duration

**AI Metrics:**
- `ai_requests_total` - AI requests by model and status
- `ai_tokens_total` - Tokens used by model
- `ai_cost_usd` - Cost in USD by model

**System Metrics:**
- `active_users` - Currently active users
- `active_jobs` - Currently active jobs
- `database_connections` - Current DB connections

### 2. Sentry Error Tracking

#### Features
- ✅ Automatic error capture
- ✅ Stack traces
- ✅ Context information
- ✅ Release tracking
- ✅ Performance monitoring
- ✅ User context (optional)

#### Integrations
- FastAPI integration
- SQLAlchemy integration
- Redis integration

### 3. Metrics API Endpoints

```
GET /api/metrics           # Prometheus format
GET /api/metrics/json      # JSON format
GET /api/metrics/health    # Health check
```

## Setup

### 1. Install Dependencies

```bash
cd server
pip install prometheus-client sentry-sdk
```

### 2. Configure Environment Variables

```bash
# Sentry (optional but recommended)
SENTRY_DSN=https://xxx@sentry.io/xxx
ENVIRONMENT=production
APP_VERSION=1.0.0

# Metrics
METRICS_ENABLED=true
PROMETHEUS_PORT=9090
```

### 3. Setup Prometheus (Local)

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'coding-agent'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/metrics'
```

### 4. Start Services

```bash
# Start API (with metrics)
cd server
python -m uvicorn api.main:app --reload

# Start Prometheus
prometheus --config.file=prometheus.yml

# Access Prometheus UI
open http://localhost:9090
```

## Usage

### View Metrics

```bash
# Prometheus format
curl http://localhost:8000/api/metrics

# JSON format
curl http://localhost:8000/api/metrics/json | jq
```

### Example Output

```
# HTTP Request Rate
http_requests_total{method="GET",endpoint="/api/health",status="200"} 1250

# Request Duration
http_request_duration_seconds_bucket{method="POST",endpoint="/api/automation/start",le="1.0"} 45

# Automation Jobs
automation_jobs_total{status="success"} 234
automation_jobs_total{status="failed"} 12

# AI Cost
ai_cost_usd_sum{model="gpt-4"} 45.67
```

### Record Custom Metrics

```python
from services.metrics.prometheus import MetricsCollector

# Record automation job
MetricsCollector.record_automation_job(
    job_type="notion_vercel",
    status="success",
    duration=12.5
)

# Record automation step
MetricsCollector.record_automation_step(
    step="generate_code",
    status="success"
)

# Record AI request
MetricsCollector.record_ai_request(
    model="gpt-4",
    status="success",
    tokens=1500,
    cost=0.05
)
```

### Use Sentry

```python
from config.sentry import capture_exception, capture_message

try:
    # Your code
    pass
except Exception as e:
    # Capture with context
    capture_exception(e, context={"user_id": user_id, "job_id": job_id})

# Capture messages
capture_message("Deployment failed", level="error", context={"project_id": project_id})
```

## Grafana Dashboard

### Import Dashboard

1. Open Grafana
2. Go to Dashboards → Import
3. Upload `grafana/dashboards/coding-agent.json`
4. Configure Prometheus data source
5. View metrics!

### Dashboard Panels

- ✅ HTTP Request Rate
- ✅ HTTP Request Duration (p95, p99)
- ✅ Automation Jobs (success/failed)
- ✅ AI Cost Over Time
- ✅ Active Users
- ✅ API Error Rate
- ✅ Database Connections
- ✅ Job Duration by Type

## Alerts

### Configure Alerts

```yaml
# prometheus-alerts.yml
groups:
  - name: coding_agent
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: SlowRequests
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 5
        for: 10m
        annotations:
          summary: "Requests are slow"
      
      - alert: HighAICost
        expr: sum(rate(ai_cost_usd_sum[1h])) > 10
        for: 1h
        annotations:
          summary: "AI costs are high"
```

## Monitoring Strategy

### Key Metrics to Watch

1. **Request Rate** - Traffic volume
2. **Error Rate** - System health
3. **Response Time** - Performance
4. **Automation Success Rate** - Business metrics
5. **AI Cost** - Cost control
6. **Active Users** - User engagement

### Alert Thresholds

- Error rate > 5% for 5 minutes
- Response time p95 > 5 seconds for 10 minutes
- AI cost > $10/hour for 1 hour
- Automation failure rate > 20%

## Production Recommendations

### 1. Use Prometheus Operator (K8s)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: coding-agent
spec:
  selector:
    matchLabels:
      app: coding-agent
  endpoints:
  - port: http
    path: /api/metrics
```

### 2. Use Grafana Cloud (Managed)

- Free tier available
- Automatic backups
- Team collaboration
- Pre-built dashboards

### 3. Configure Sentry Alerts

- Error rate thresholds
- New issue notifications
- Release tracking
- Performance budgets

### 4. Centralized Logging

```python
# Use structured logging
import logging
logging.basicConfig(
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    level=logging.INFO
)
```

## Files Added

```
✅ server/services/metrics/prometheus.py (178 lines)
✅ server/api/routes/metrics.py (31 lines)
✅ server/api/middleware/metrics.py (46 lines)
✅ server/config/sentry.py (67 lines)
✅ grafana/dashboards/coding-agent.json (47 lines)
✅ OBSERVABILITY_GUIDE.md (complete documentation)
```

---

**Option D complete - Full observability enabled!** 📊

