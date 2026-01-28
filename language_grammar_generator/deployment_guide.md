# Deployment Guide
## Production Deployment Following Gold Standard Patterns

**Primary Gold Standard:** [Chinese Simplified](languages/zh/zh_analyzer.py) - Clean Architecture benchmark  
**Secondary Reference:** [Hindi](languages/hindi/hi_analyzer.py)  
**Critical:** Deploy only implementations matching Chinese Simplified Clean Architecture patterns  
**Prerequisites:** Study gold standards, complete implementation following their patterns  
**Architecture:** Follow [Architecture Guide](architecture_guide.md) with gold standard compliance  
**Time Estimate:** 2-4 weeks for full production deployment

## 🎯 Deployment Philosophy - Gold Standard Compliance

### Production Readiness Principles - Match Gold Standards
- **Gold Standard Verification:** All deployments must match Hindi/Chinese Simplified patterns
- **Natural Validation:** No artificial confidence boosting in production (removed from all implementations)
- **Facade Pattern:** Deploy only clean component orchestration like gold standards
- **External Configuration:** Load all settings from files like gold standards
- **AI Model Restrictions:** Use only gemini-2.5-flash and gemini-3-flash-preview in production
- **Component Isolation:** Deploy loosely coupled components like gold standards

### Deployment Strategy - Gold Standard Validation
- **Pre-Deployment Audit:** Verify implementation matches gold standards before deployment
- **Gold Standard Testing:** All tests must pass against Hindi/Chinese Simplified baselines
- **Configuration Validation:** External configs must load like gold standards
- **AI Integration Check:** Verify allowed models and circuit breaker implementation
- **Automated Rollback:** Instant recovery if gold standard compliance fails

## 🏗️ Infrastructure Setup - Gold Standard Structure

### 1. Directory Structure Matching Gold Standards
```
languages/{language}/
├── {language}_analyzer.py          # Main facade like hi_analyzer.py/zh_analyzer.py
├── {language}_config.py            # External config loading like gold standards
├── {language}_prompt_builder.py    # Prompt generation like gold standards
├── {language}_response_parser.py   # Response parsing like gold standards
├── {language}_validator.py         # NATURAL validation like gold standards (NO boosting)
├── config/                         # External config files like gold standards
│   ├── grammatical_roles.yaml
│   ├── color_schemes.yaml
│   └── prompt_templates.yaml
├── tests/                          # Tests matching gold standard patterns
│   ├── test_{language}_analyzer.py
│   └── test_natural_validation.py  # NO confidence boosting tests
└── deployment/                     # Deployment configs
    ├── Dockerfile                  # Container matching gold standard deployment
    ├── docker-compose.yml
    └── kubernetes/
        ├── deployment.yaml
        └── service.yaml
```

### 2. Pre-Deployment Gold Standard Verification
```bash
# Pre-deployment checklist - compare with gold standards
./verify_gold_standard_compliance.sh {language_code}

# Checks performed:
# - Facade pattern implementation ✓
# - Natural validation (no artificial boosting) ✓
# - External config loading ✓
# - AI model restrictions ✓
# - Component isolation ✓
# - Test coverage matching gold standards ✓
```

### 3. Containerization - Gold Standard Docker
```dockerfile
# Dockerfile - Match gold standard containerization
FROM python:3.11-slim

# Install dependencies like gold standards
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy language implementation matching gold standards
COPY languages/${LANGUAGE_CODE}/ /app/languages/${LANGUAGE_CODE}/
COPY languages/${LANGUAGE_CODE}/config/ /app/languages/${LANGUAGE_CODE}/config/

# Verify gold standard compliance on build
RUN python -c "from languages.${LANGUAGE_CODE}.${LANGUAGE_CODE}_analyzer import *; print('Gold standard compliance verified')"

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🚀 Deployment Process - Gold Standard Validation

### Phase 1: Pre-Deployment Verification
```bash
# 1. Gold standard comparison
compare_with_gold_standards.sh hindi zh ${LANGUAGE_CODE}

# 2. Natural validation audit (no artificial boosting)
audit_natural_validation.sh ${LANGUAGE_CODE}

# 3. Component isolation test
test_component_isolation.sh ${LANGUAGE_CODE}

# 4. AI integration verification
verify_ai_integration.sh ${LANGUAGE_CODE}
```

### Phase 2: Staging Deployment
```bash
# Deploy to staging with gold standard monitoring
deploy_staging.sh ${LANGUAGE_CODE}

# Run gold standard test suite
run_gold_standard_tests.sh staging ${LANGUAGE_CODE}

# Performance benchmark against gold standards
benchmark_against_gold_standards.sh staging hindi zh
```

### Phase 3: Production Deployment
```bash
# Blue-green deployment with gold standard verification
deploy_production_blue_green.sh ${LANGUAGE_CODE}

# Verify production matches gold standards
verify_production_gold_standards.sh ${LANGUAGE_CODE}

# Gradual traffic shift with monitoring
shift_traffic_with_monitoring.sh ${LANGUAGE_CODE}
```

## 📊 Monitoring & Observability - Gold Standard Metrics

### Gold Standard Compliance Metrics
```python
# Monitor gold standard compliance in production
def monitor_gold_standard_compliance():
    metrics = {
        "facade_pattern_active": check_facade_pattern(),
        "natural_validation_only": not detect_artificial_boosting(),  # Critical
        "external_config_loading": verify_config_loading(),
        "allowed_models_only": check_ai_models(),
        "component_isolation": verify_loose_coupling(),
    }
    return metrics
```

### Performance Metrics - Compare with Gold Standards
```python
# Performance monitoring against gold standards
def performance_monitoring():
    gold_standard_baseline = get_gold_standard_performance()  # Hindi/Chinese baseline

    current_metrics = {
        "response_time_ratio": current_time / gold_standard_baseline["response_time"],
        "memory_usage_ratio": current_memory / gold_standard_baseline["memory_usage"],
        "error_rate_ratio": current_errors / gold_standard_baseline["error_rate"],
        "confidence_distribution": get_confidence_distribution(),  # Natural range 0-1
    }

    return current_metrics
```

### Alerting Rules - Gold Standard Deviations
```yaml
# Prometheus alerting rules for gold standard compliance
groups:
  - name: gold_standard_alerts
    rules:
      - alert: ArtificialBoostingDetected
        expr: artificial_boosting_detected > 0
        labels:
          severity: critical
        annotations:
          summary: "Artificial confidence boosting detected - violates gold standards"

      - alert: WrongAIModel
        expr: ai_model_violation > 0
        labels:
          severity: warning
        annotations:
          summary: "Non-allowed AI model detected - should use gemini-2.5-flash or gemini-3-flash-preview"

      - alert: TightCouplingDetected
        expr: component_coupling_violation > 0
        labels:
          severity: warning
        annotations:
          summary: "Tight component coupling detected - should match gold standard loose coupling"
```

## 🔒 Security - Gold Standard Security

### API Key Management - Like Gold Standards
```python
# Secure key management matching gold standards
class SecureAPIKeyManager:
    ALLOWED_MODELS = ["gemini-2.5-flash", "gemini-3-flash-preview"]  # STRICT

    def validate_and_use_key(self, api_key, requested_model):
        if requested_model not in self.ALLOWED_MODELS:
            raise SecurityViolation(f"Model {requested_model} not allowed")

        # Encrypt and store key securely
        encrypted_key = self._encrypt_key(api_key)

        # Use key with circuit breaker (like gold standards)
        return self._call_ai_with_security(encrypted_key, requested_model)
```

### Input Validation - Gold Standard Patterns
```python
# Input validation matching gold standards
def validate_production_input(sentence, target_word, complexity, api_key):
    checks = {
        "sentence_length": 1 <= len(sentence) <= 500,  # Reasonable limits
        "target_word_present": target_word in sentence,
        "complexity_valid": complexity in ["beginner", "intermediate", "advanced"],
        "api_key_format": validate_api_key_format(api_key),  # Google AI format
        "no_malicious_content": not contains_malicious_content(sentence),
    }

    if not all(checks.values()):
        raise ValidationError(f"Input validation failed: {checks}")

    return True
```

## 🔄 Rollback Strategy - Gold Standard Recovery

### Automated Rollback Triggers
```python
# Rollback triggers based on gold standard compliance
ROLLBACK_TRIGGERS = {
    "artificial_boosting_detected": True,  # Critical - rollback immediately
    "gold_standard_performance_degradation": 0.5,  # 50% slower than gold standards
    "error_rate_above_threshold": 0.05,  # 5% error rate
    "ai_model_violation": True,  # Wrong model used
    "component_coupling_violation": True,  # Tight coupling detected
}
```

### Rollback Process
```bash
# Automated rollback to gold standard compliant version
rollback_to_gold_standard.sh ${LANGUAGE_CODE}

# Steps:
# 1. Identify last gold standard compliant deployment
# 2. Verify rollback version matches gold standards
# 3. Execute blue-green rollback
# 4. Run gold standard test suite
# 5. Monitor recovery metrics
```

## 📈 Scaling Strategy - Gold Standard Performance

### Horizontal Scaling - Match Gold Standards
```yaml
# Kubernetes HPA based on gold standard metrics
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: language-analyzer-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: language-analyzer
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: response_time_seconds
        selector:
          matchLabels:
            app: language-analyzer
      target:
        type: AverageValue
        averageValue: "3"  # Match gold standard response time
```

### Caching Strategy - Like Gold Standards
```python
# Multi-level caching matching gold standards
class GoldStandardCache:
    def __init__(self):
        self.l1_cache = {}  # In-memory like gold standards
        self.l2_cache = RedisCache()  # Redis for distributed
        self.l3_cache = CloudCache()  # Cloud for persistence

    def get_with_gold_standard_fallback(self, key):
        # Try caches in order like gold standards
        for cache in [self.l1_cache, self.l2_cache, self.l3_cache]:
            if key in cache:
                return cache[key]

        # Generate and cache new result
        result = self._generate_result(key)
        self._cache_result(key, result)
        return result
```

## 🧪 Testing in Production - Gold Standard Validation

### Production Testing Strategy
```python
# Continuous gold standard validation in production
class ProductionGoldStandardValidator:
    def validate_production_compliance(self):
        """Continuous validation against gold standards"""
        checks = {
            "artificial_boosting_check": self._detect_artificial_boosting(),
            "model_compliance": self._verify_ai_models(),
            "performance_baseline": self._compare_performance_with_gold_standards(),
            "config_integrity": self._verify_external_config_loading(),
        }

        if not all(checks.values()):
            self._trigger_rollback(f"Gold standard violation: {checks}")

        return checks
```

### A/B Testing - Gold Standard Comparison
```python
# A/B testing against gold standards
def ab_test_against_gold_standards(new_version, gold_standard_version):
    """A/B test new implementation against gold standards"""
    results = {
        "new_version_accuracy": test_accuracy(new_version),
        "gold_standard_accuracy": test_accuracy(gold_standard_version),
        "performance_comparison": compare_performance(new_version, gold_standard_version),
        "user_preference": collect_user_feedback(),
    }

    if results["gold_standard_accuracy"] > results["new_version_accuracy"] * 1.1:
        # Gold standard significantly better - keep it
        return "KEEP_GOLD_STANDARD"

    return "CONSIDER_NEW_VERSION"
```

## 📋 Deployment Checklist - Gold Standard Compliance

### Pre-Deployment
- [ ] **Gold Standard Study:** Thoroughly studied Hindi and Chinese Simplified analyzers?
- [ ] **Natural Validation:** Removed all artificial confidence boosting?
- [ ] **Facade Pattern:** Implemented component orchestration like gold standards?
- [ ] **External Config:** Loading all settings from files like gold standards?
- [ ] **AI Models:** Using only gemini-2.5-flash and gemini-3-flash-preview?
- [ ] **Component Isolation:** Verified loose coupling like gold standards?

### Deployment Verification
- [ ] **Container Build:** Dockerfile matches gold standard structure?
- [ ] **Config Loading:** External configs load properly in container?
- [ ] **AI Integration:** Circuit breaker and error handling working?
- [ ] **Performance:** Response times match gold standard baselines?
- [ ] **Security:** API keys properly secured and validated?

### Post-Deployment
- [ ] **Gold Standard Tests:** All tests pass against gold standard baselines?
- [ ] **Monitoring:** Gold standard compliance metrics active?
- [ ] **Alerting:** Rollback triggers configured for violations?
- [ ] **Scaling:** HPA configured for gold standard performance targets?
- [ ] **Rollback:** Automated rollback tested and ready?

### Production Monitoring
- [ ] **Artificial Boosting Detection:** Monitoring active for violations?
- [ ] **Model Compliance:** Alerts for wrong AI model usage?
- [ ] **Performance Baseline:** Comparison with gold standards active?
- [ ] **Config Integrity:** External config loading monitored?
- [ ] **Component Health:** All components isolated and healthy?

---

**Remember:** Only deploy implementations that match the gold standards ([Hindi](languages/hindi/hi_analyzer.py) and [Chinese Simplified](languages/zh/zh_analyzer.py)). They represent the proven working patterns - no artificial confidence boosting, clean facade orchestration, natural validation scoring.
│   │   └── rules.yml
│   ├── grafana/
│   │   └── dashboards/
│   │       └── language_analyzer.json
│   └── alerts/
│       └── alert_rules.yml
└── security/
    ├── secrets/
    │   ├── api_keys.enc
    │   └── certificates/
    └── policies/
        └── security_policy.md
```

### 2. Docker Configuration

**File:** `deployment/docker/Dockerfile`
```dockerfile
# Multi-stage build for optimized production image
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash analyzer

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY languages/{language}/ /app/languages/{language}/
COPY streamlit_app/ /app/streamlit_app/

# Create necessary directories
RUN mkdir -p /app/logs /app/cache /app/output

# Set permissions
RUN chown -R analyzer:analyzer /app
USER analyzer

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/health || exit 1

# Expose port
EXPOSE 8501

# Start application
CMD ["streamlit", "run", "streamlit_app/app_v3.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**File:** `deployment/docker/docker-compose.yml`
```yaml
version: '3.8'

services:
  language-analyzer:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./cache:/app/cache
      - ./output:/app/output
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped

volumes:
  redis_data:
  prometheus_data:
  grafana_data:
```

### 3. Kubernetes Deployment

**File:** `deployment/kubernetes/deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: language-analyzer
  labels:
    app: language-analyzer
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: language-analyzer
  template:
    metadata:
      labels:
        app: language-analyzer
    spec:
      containers:
      - name: analyzer
        image: language-analyzer:latest
        ports:
        - containerPort: 8501
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: cache-volume
          mountPath: /app/cache
        - name: logs-volume
          mountPath: /app/logs
      volumes:
      - name: cache-volume
        persistentVolumeClaim:
          claimName: analyzer-cache-pvc
      - name: logs-volume
        persistentVolumeClaim:
          claimName: analyzer-logs-pvc
```

**File:** `deployment/kubernetes/service.yaml`
```yaml
apiVersion: v1
kind: Service
metadata:
  name: language-analyzer-service
spec:
  selector:
    app: language-analyzer
  ports:
  - port: 8501
    targetPort: 8501
  type: LoadBalancer
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

**File:** `deployment/kubernetes/configmap.yaml`
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: analyzer-config
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  CACHE_TTL: "3600"
  MAX_REQUESTS_PER_MINUTE: "60"
  AI_MODEL_TIMEOUT: "30"
  MAX_RETRIES: "3"
```

**File:** `deployment/kubernetes/ingress.yaml`
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: analyzer-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - analyzer.yourdomain.com
    secretName: analyzer-tls
  rules:
  - host: analyzer.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: language-analyzer-service
            port:
              number: 8501
```

## 📊 Monitoring and Observability

### 1. Prometheus Configuration

**File:** `monitoring/prometheus/prometheus.yml`
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'language-analyzer'
    static_configs:
      - targets: ['language-analyzer-service:8501']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-service:6379']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    scrape_interval: 30s
```

**File:** `monitoring/prometheus/rules.yml`
```yaml
groups:
  - name: language_analyzer_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}%"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time detected"
          description: "95th percentile response time is {{ $value }}s"

      - alert: LowQualityScore
        expr: analyzer_quality_score < 0.7
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low analysis quality detected"
          description: "Average quality score is {{ $value }}"

      - alert: HighMemoryUsage
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}%"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space"
          description: "Available disk space is {{ $value }}%"
```

### 2. Application Metrics

**File:** `streamlit_app/metrics.py`
```python
from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Analysis metrics
ANALYSIS_COUNT = Counter(
    'analysis_requests_total',
    'Total analysis requests',
    ['language', 'complexity', 'status']
)

ANALYSIS_LATENCY = Histogram(
    'analysis_duration_seconds',
    'Analysis request latency',
    ['language', 'complexity']
)

ANALYSIS_QUALITY = Histogram(
    'analysis_quality_score',
    'Analysis quality scores',
    ['language', 'complexity']
)

# AI service metrics
AI_REQUEST_COUNT = Counter(
    'ai_requests_total',
    'Total AI API requests',
    ['model', 'status']
)

AI_LATENCY = Histogram(
    'ai_request_duration_seconds',
    'AI request latency',
    ['model']
)

AI_TOKEN_COUNT = Histogram(
    'ai_tokens_used',
    'Tokens used per AI request',
    ['model']
)

# Cache metrics
CACHE_HITS = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# System metrics
MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Current memory usage'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'Current CPU usage'
)

# Version info
APP_INFO = Info('app_info', 'Application information')
APP_INFO.info({
    'version': '1.0.0',
    'language': '{language}',
    'environment': 'production'
})

def track_request(method: str, endpoint: str):
    """Decorator to track HTTP requests"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status = '200'
                return result
            except Exception as e:
                status = '500'
                raise e
            finally:
                REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
                REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(
                    time.time() - start_time
                )
        return wrapper
    return decorator

def track_analysis(language: str, complexity: str):
    """Decorator to track analysis requests"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status = 'success'
                quality = getattr(result, 'confidence_score', 0.5)
                ANALYSIS_QUALITY.labels(language=language, complexity=complexity).observe(quality)
                return result
            except Exception as e:
                status = 'error'
                raise e
            finally:
                ANALYSIS_COUNT.labels(language=language, complexity=complexity, status=status).inc()
                ANALYSIS_LATENCY.labels(language=language, complexity=complexity).observe(
                    time.time() - start_time
                )
        return wrapper
    return decorator

def track_ai_request(model: str):
    """Decorator to track AI requests"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status = 'success'
                # Extract token count if available
                token_count = getattr(result, 'usage', {}).get('total_tokens', 0)
                if token_count > 0:
                    AI_TOKEN_COUNT.labels(model=model).observe(token_count)
                return result
            except Exception as e:
                status = 'error'
                raise e
            finally:
                AI_REQUEST_COUNT.labels(model=model, status=status).inc()
                AI_LATENCY.labels(model=model).observe(time.time() - start_time)
        return wrapper
    return decorator

def update_system_metrics():
    """Update system resource metrics"""
    import psutil

    MEMORY_USAGE.set(psutil.virtual_memory().used)
    CPU_USAGE.set(psutil.cpu_percent(interval=1))

# Initialize metrics on startup
def init_metrics():
    """Initialize metrics collection"""
    import threading
    import time

    def collect_system_metrics():
        while True:
            update_system_metrics()
            time.sleep(60)  # Update every minute

    # Start background thread for system metrics
    thread = threading.Thread(target=collect_system_metrics, daemon=True)
    thread.start()
```

### 3. Grafana Dashboard

**File:** `monitoring/grafana/dashboards/language_analyzer.json`
```json
{
  "dashboard": {
    "title": "Language Analyzer Dashboard",
    "tags": ["language", "analyzer", "ai"],
    "timezone": "UTC",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "Analysis Quality",
        "type": "graph",
        "targets": [
          {
            "expr": "analysis_quality_score",
            "legendFormat": "{{language}} {{complexity}}"
          }
        ]
      },
      {
        "title": "AI Service Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "ai_request_duration_seconds",
            "legendFormat": "{{model}} latency"
          },
          {
            "expr": "ai_tokens_used",
            "legendFormat": "{{model}} tokens"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error rate %"
          }
        ]
      },
      {
        "title": "Cache Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) * 100",
            "legendFormat": "Cache hit rate %"
          }
        ]
      },
      {
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "memory_usage_bytes / 1024 / 1024",
            "legendFormat": "Memory usage MB"
          },
          {
            "expr": "cpu_usage_percent",
            "legendFormat": "CPU usage %"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

## 🔒 Security Implementation

### 1. Secret Management

**File:** `security/secrets/api_keys.enc`
```bash
# Encrypted API keys - use tools like sops or vault
# Never store plaintext API keys in repository
GEMINI_API_KEY: ENC[AES256_GCM,data:...,type:str]
FIREBASE_API_KEY: ENC[AES256_GCM,data:...,type:str]
REDIS_PASSWORD: ENC[AES256_GCM,data:...,type:str]
```

**File:** `deployment/kubernetes/secret.yaml`
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: analyzer-secrets
type: Opaque
data:
  # Base64 encoded values
  gemini-api-key: <base64-encoded-key>
  firebase-api-key: <base64-encoded-key>
  redis-password: <base64-encoded-password>
```

### 2. Security Middleware

**File:** `streamlit_app/security_middleware.py`
```python
import streamlit as st
import time
import logging
from typing import Dict, Any
from functools import wraps
import hashlib
import hmac

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Security middleware for request validation and rate limiting"""

    def __init__(self, max_requests_per_minute: int = 60, max_requests_per_hour: int = 1000):
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_hour = max_requests_per_hour

        # In-memory rate limiting (use Redis in production)
        self.request_counts = {}
        self.hourly_counts = {}

    def validate_request(self, request_data: Dict[str, Any]) -> bool:
        """Validate incoming request"""
        # Check rate limits
        if not self._check_rate_limits():
            logger.warning("Rate limit exceeded")
            return False

        # Validate input data
        if not self._validate_input(request_data):
            logger.warning("Invalid input data")
            return False

        # Check for malicious content
        if self._contains_malicious_content(request_data):
            logger.warning("Malicious content detected")
            return False

        return True

    def _check_rate_limits(self) -> bool:
        """Check if request is within rate limits"""
        current_time = int(time.time())
        client_ip = self._get_client_ip()

        # Per-minute limit
        minute_key = f"{client_ip}:{current_time // 60}"
        if minute_key not in self.request_counts:
            self.request_counts[minute_key] = 0
        self.request_counts[minute_key] += 1

        if self.request_counts[minute_key] > self.max_requests_per_minute:
            return False

        # Per-hour limit
        hour_key = f"{client_ip}:{current_time // 3600}"
        if hour_key not in self.hourly_counts:
            self.hourly_counts[hour_key] = 0
        self.hourly_counts[hour_key] += 1

        if self.hourly_counts[hour_key] > self.max_requests_per_hour:
            return False

        # Clean up old entries
        self._cleanup_old_entries(current_time)

        return True

    def _validate_input(self, request_data: Dict[str, Any]) -> bool:
        """Validate input data structure and content"""
        required_fields = ['sentence', 'complexity']

        # Check required fields
        for field in required_fields:
            if field not in request_data:
                return False

        # Validate sentence
        sentence = request_data.get('sentence', '')
        if not isinstance(sentence, str) or len(sentence.strip()) == 0:
            return False

        if len(sentence) > 1000:  # Reasonable limit
            return False

        # Validate complexity
        complexity = request_data.get('complexity', '')
        if complexity not in ['beginner', 'intermediate', 'advanced']:
            return False

        # Validate target_word if provided
        target_word = request_data.get('target_word', '')
        if target_word and len(target_word) > 100:
            return False

        return True

    def _contains_malicious_content(self, request_data: Dict[str, Any]) -> bool:
        """Check for potentially malicious content"""
        text_fields = ['sentence', 'target_word']

        malicious_patterns = [
            r'<script',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'on\w+\s*=',  # Event handlers
            r'\\x[0-9a-fA-F]{2}',  # Hex encoding
            r'%[0-9a-fA-F]{2}',  # URL encoding
        ]

        for field in text_fields:
            content = request_data.get(field, '')
            if isinstance(content, str):
                for pattern in malicious_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return True

        return False

    def _get_client_ip(self) -> str:
        """Get client IP address"""
        try:
            # In Streamlit, get from session state or headers
            return st.session_state.get('client_ip', 'unknown')
        except:
            return 'unknown'

    def _cleanup_old_entries(self, current_time: int):
        """Clean up old rate limiting entries"""
        # Remove entries older than 1 hour
        cutoff_minute = (current_time // 60) - 60
        cutoff_hour = (current_time // 3600) - 1

        self.request_counts = {
            k: v for k, v in self.request_counts.items()
            if int(k.split(':')[1]) > cutoff_minute
        }

        self.hourly_counts = {
            k: v for k, v in self.hourly_counts.items()
            if int(k.split(':')[1]) > cutoff_hour
        }

def require_security_check(func):
    """Decorator to enforce security checks"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        security = SecurityMiddleware()

        # Extract request data from args/kwargs
        request_data = kwargs.get('request_data', {})

        if not security.validate_request(request_data):
            st.error("Request validation failed. Please check your input.")
            return None

        return func(*args, **kwargs)
    return wrapper
```

## 🚀 Deployment Automation

### 1. CI/CD Pipeline

**File:** `.github/workflows/deploy.yml`
```yaml
name: Deploy Language Analyzer

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        cd languages/{language}
        pytest tests/ -v --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./languages/{language}/coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: |
        docker build -f deployment/docker/Dockerfile -t language-analyzer:${{ github.sha }} .

    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker tag language-analyzer:${{ github.sha }} ${{ secrets.DOCKER_REGISTRY }}/language-analyzer:${{ github.sha }}
        docker push ${{ secrets.DOCKER_REGISTRY }}/language-analyzer:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Kubernetes
      run: |
        # Update deployment image
        sed -i 's|image: language-analyzer:latest|image: ${{ secrets.DOCKER_REGISTRY }}/language-analyzer:${{ github.sha }}|g' deployment/kubernetes/deployment.yaml

        # Deploy using kubectl
        kubectl apply -f deployment/kubernetes/

        # Wait for rollout
        kubectl rollout status deployment/language-analyzer

---

**Remember:** Only deploy implementations that match the gold standards ([Hindi](languages/hindi/hi_analyzer.py) and [Chinese Simplified](languages/zh/zh_analyzer.py)). They represent the proven working patterns - no artificial confidence boosting, clean facade orchestration, natural validation scoring.
        # Wait for service to be ready
        kubectl wait --for=condition=available --timeout=300s deployment/language-analyzer

        # Run health check script
        bash deployment/scripts/health_check.sh

    - name: Rollback on failure
      if: failure()
      run: |
        bash deployment/scripts/rollback.sh
```

### 2. Deployment Scripts

**File:** `deployment/scripts/deploy.sh`
```bash
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Configuration
ENVIRONMENT=${1:-production}
VERSION=$(git rev-parse --short HEAD)
REGISTRY=${DOCKER_REGISTRY:-your-registry.com}

# Build and push Docker image
echo "📦 Building Docker image..."
docker build -f deployment/docker/Dockerfile -t language-analyzer:$VERSION .
docker tag language-analyzer:$VERSION $REGISTRY/language-analyzer:$VERSION
docker push $REGISTRY/language-analyzer:$VERSION

# Update Kubernetes deployment
echo "⚙️ Updating Kubernetes deployment..."
sed -i "s|image:.*|image: $REGISTRY/language-analyzer:$VERSION|g" deployment/kubernetes/deployment.yaml

# Apply Kubernetes manifests
echo "🚢 Applying Kubernetes manifests..."
kubectl apply -f deployment/kubernetes/

# Wait for rollout
echo "⏳ Waiting for rollout to complete..."
kubectl rollout status deployment/language-analyzer --timeout=300s

# Run health checks
echo "🔍 Running health checks..."
bash deployment/scripts/health_check.sh

# Clean up old images
echo "🧹 Cleaning up old images..."
docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || true

echo "✅ Deployment completed successfully!"
```

**File:** `deployment/scripts/health_check.sh`
```bash
#!/bin/bash

echo "🔍 Running health checks..."

# Configuration
SERVICE_URL=${SERVICE_URL:-http://localhost:8501}
TIMEOUT=30

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local expected_status=${2:-200}

    echo "Checking $url..."

    local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT $url)

    if [ "$response" -eq "$expected_status" ]; then
        echo "✅ $url is healthy"
        return 0
    else
        echo "❌ $url returned status $response (expected $expected_status)"
        return 1
    fi
}

# Health checks
failures=0

# Check main application
if ! check_endpoint "$SERVICE_URL/health"; then
    ((failures++))
fi

# Check metrics endpoint
if ! check_endpoint "$SERVICE_URL/metrics" 200; then
    ((failures++))
fi

# Check database connectivity (if applicable)
# Add more checks as needed

if [ $failures -eq 0 ]; then
    echo "🎉 All health checks passed!"
    exit 0
else
    echo "💥 $failures health check(s) failed!"
    exit 1
fi
```

**File:** `deployment/scripts/rollback.sh`
```bash
#!/bin/bash

echo "🔄 Rolling back deployment..."

# Get previous deployment
PREVIOUS_IMAGE=$(kubectl get deployment language-analyzer -o jsonpath='{.spec.template.spec.containers[0].image}')

echo "Previous image: $PREVIOUS_IMAGE"

# Rollback to previous version
kubectl rollout undo deployment/language-analyzer

# Wait for rollback to complete
echo "⏳ Waiting for rollback to complete..."
kubectl rollout status deployment/language-analyzer --timeout=300s

# Run health checks
echo "🔍 Running health checks after rollback..."
bash deployment/scripts/health_check.sh

if [ $? -eq 0 ]; then
    echo "✅ Rollback completed successfully!"
else
    echo "💥 Rollback completed but health checks failed!"
    exit 1
fi
```

## 📈 Performance Optimization

### 1. Caching Strategy

**File:** `streamlit_app/advanced_cache.py`
```python
import redis
import json
import hashlib
from typing import Dict, Any, Optional
import time

class AdvancedCache:
    """Advanced caching with semantic similarity and TTL management"""

    def __init__(self, redis_url: str = "redis://localhost:6379", default_ttl: int = 3600):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached result"""
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        return None

    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None):
        """Set cached result"""
        try:
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

    def get_semantic_key(self, sentence: str, target_word: str, complexity: str) -> str:
        """Generate semantic cache key"""
        # Normalize sentence for caching
        normalized = sentence.lower().strip()

        # Create semantic hash
        content = f"{normalized}|{target_word or ''}|{complexity}"
        semantic_hash = hashlib.md5(content.encode()).hexdigest()

        return f"semantic:{semantic_hash}"

    def find_similar_result(self, sentence: str, target_word: str, complexity: str,
                          similarity_threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """Find semantically similar cached result"""
        # This is a simplified implementation
        # In practice, you'd use embeddings or other similarity measures

        key = self.get_semantic_key(sentence, target_word, complexity)
        return self.get(key)

    def cache_with_semantic_key(self, sentence: str, target_word: str, complexity: str,
                               result: Dict[str, Any], ttl: Optional[int] = None):
        """Cache result with semantic key"""
        key = self.get_semantic_key(sentence, target_word, complexity)
        self.set(key, result, ttl)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            info = self.redis.info()
            return {
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'keys': self.redis.dbsize(),
                'memory_used': info.get('used_memory', 0),
                'hit_rate': info.get('keyspace_hits', 0) / max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1)
            }
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {}

    def cleanup_expired_keys(self):
        """Clean up expired cache keys"""
        # Redis handles TTL automatically, but we can add custom cleanup logic
        pass
```

### 2. Load Balancing and Scaling

**File:** `deployment/kubernetes/hpa.yaml`
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: language-analyzer-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: language-analyzer
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
```

## ✅ Success Criteria

### Infrastructure Readiness
- [ ] **Containerization:** Docker image builds successfully and runs in isolation
- [ ] **Orchestration:** Kubernetes manifests deploy without errors
- [ ] **Load Balancing:** Traffic distributes evenly across pods
- [ ] **Auto-scaling:** HPA scales based on resource utilization

### Monitoring and Observability
- [ ] **Metrics Collection:** Prometheus scrapes all defined metrics
- [ ] **Alerting:** Critical alerts trigger appropriate notifications
- [ ] **Dashboards:** Grafana displays comprehensive system overview
- [ ] **Logging:** Structured logs with appropriate levels

### Security and Compliance
- [ ] **Secret Management:** API keys encrypted and rotated regularly
- [ ] **Access Control:** Rate limiting and input validation prevent abuse
- [ ] **Audit Logging:** Security events logged and monitored
- [ ] **Compliance:** GDPR/CCPA compliance for user data handling

### Performance and Reliability
- [ ] **Response Time:** P95 < 5 seconds for complex analysis
- [ ] **Availability:** 99.9% uptime with automatic recovery
- [ ] **Scalability:** Handles 10x traffic increase without degradation
- [ ] **Caching:** 80%+ cache hit rate for repeated requests

### Deployment Automation
- [ ] **CI/CD Pipeline:** Automated testing and deployment on commits
- [ ] **Zero-Downtime:** Blue-green deployments with instant rollback
- [ ] **Health Checks:** Automated verification of deployment success
- [ ] **Rollback:** One-click rollback to previous version

## 🚨 Common Deployment Pitfalls

### 1. Resource Constraints
**Problem:** Pods crash due to insufficient memory/CPU
**Prevention:** Proper resource requests/limits and monitoring

### 2. Configuration Drift
**Problem:** Different environments have inconsistent configurations
**Prevention:** Infrastructure as Code and configuration management

### 3. Missing Health Checks
**Problem:** Unhealthy pods remain in service
**Prevention:** Comprehensive readiness and liveness probes

### 4. Inadequate Monitoring
**Problem:** Issues discovered too late
**Prevention:** Comprehensive metrics and alerting from day one

### 5. Security Vulnerabilities
**Problem:** Exposed secrets or unpatched containers
**Prevention:** Security scanning and secret management

---

**🎯 Ready for production deployment?** Start with Docker Compose for initial testing, then progress to Kubernetes for scalability. Remember: monitor everything, automate everything, and have rollback plans!

**Need help with deployment?** Refer to the [Troubleshooting Guide](troubleshooting_guide.md) for common deployment issues, or check the [AI Prompting Guide](ai_prompting_guide.md) for performance optimization.

**📊 Pro tip:** Implement comprehensive monitoring before going to production - you can't fix what you can't see!</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\language_grammar_generator\deployment_guide.md