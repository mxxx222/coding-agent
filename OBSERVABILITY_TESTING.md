# 🧪 Observability Testing Guide

## Quick Test Commands

### 1. Start Services

```bash
# Terminal 1: Start API server
cd server
export SENTRY_DSN="your_sentry_dsn_here"  # Optional
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/codingagent"
python -m uvicorn api.main:app --reload

# Terminal 2: Start Web UI
cd web-ui
npm run dev
```

### 2. Test Metrics Endpoint

```bash
# Check Prometheus metrics
curl http://localhost:8000/api/metrics

# Expected output:
# # HELP http_requests_total Total HTTP requests
# # TYPE http_requests_total counter
# http_requests_total{method="GET",endpoint="/api/metrics",status="200"} 1.0
```

### 3. Test Metrics JSON

```bash
curl http://localhost:8000/api/metrics/json | jq

# Expected: JSON formatted metrics
```

### 4. Test Sentry Integration

```bash
# Trigger test error
curl http://localhost:8000/api/observability/sentry-test

# Expected: HTTP 500 error
# Check Sentry dashboard for the error
```

### 5. Test Metrics Collection

```bash
# Generate test traffic
for i in {1..50}; do
  curl -s http://localhost:8000/api/observability/metrics-test > /dev/null
done

# Check metrics
curl http://localhost:8000/api/metrics | grep http_requests_total
```

### 6. Load Test (optional)

```bash
# Using hey (install: brew install hey)
hey -n 1000 -c 50 http://localhost:8000/api/observability/metrics-test

# Using Apache Bench
ab -n 1000 -c 50 http://localhost:8000/api/observability/metrics-test
```

## Validation Checklist

### ✅ Prometheus Metrics

- [ ] `/api/metrics` returns 200
- [ ] Metrics in Prometheus text format
- [ ] `http_requests_total` counter present
- [ ] `http_request_duration_seconds` histogram present
- [ ] Metrics values increasing with requests

### ✅ Sentry Integration

- [ ] SENTRY_DSN configured
- [ ] Sentry SDK initialized (check logs)
- [ ] `/api/observability/sentry-test` returns 500
- [ ] Error appears in Sentry dashboard
- [ ] Stack trace visible in Sentry

### ✅ Metrics Collection

- [ ] Test traffic visible in metrics
- [ ] Request counts increasing
- [ ] Latency measurements recorded
- [ ] Success/failure rates tracked

### ✅ Grafana Dashboard

- [ ] Dashboard imports successfully
- [ ] Data sources configured
- [ ] Panels showing metrics
- [ ] Graphs updating in real-time

## Troubleshooting

### Metrics Not Showing

```bash
# Check if middleware is registered
grep -r "MetricsMiddleware" server/api/main.py

# Check metrics endpoint
curl -v http://localhost:8000/api/metrics

# Check logs
tail -f logs/api-audit.log
```

### Sentry Not Working

```bash
# Check DSN is set
echo $SENTRY_DSN

# Check Sentry SDK version
pip list | grep sentry

# Test with debug mode
export SENTRY_DEBUG=true
python -m uvicorn api.main:app --reload
```

### High Latency

```bash
# Check metrics for latency
curl http://localhost:8000/api/metrics | grep duration

# Check database connections
# Check Redis connections
# Check external API calls
```

## Production Checklist

### Before Deploying

- [ ] SENTRY_DSN set in production env
- [ ] Prometheus configured to scrape
- [ ] Grafana dashboard tested
- [ ] Alert rules configured
- [ ] Metrics retention policy set
- [ ] Sentry release version set

### After Deploying

- [ ] Verify metrics endpoint accessible
- [ ] Check Sentry receiving errors
- [ ] Validate dashboard data
- [ ] Test alert notifications
- [ ] Monitor for 24 hours

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Sentry Documentation](https://docs.sentry.io/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

---

**Ready to test!** 🚀

