# Monitoring and Logging Configuration

**Date**: 2025-01-18  
**Sprint**: Sprint 1 - Feature 5  
**Status**: Configuration Documented (Manual setup required via Console)  

---

## Overview

This document provides comprehensive monitoring and logging configuration for the AletheiaCodex Load Balancer and IAP infrastructure. Due to service account permission limitations, alert policies and dashboards should be created via GCP Console.

---

## Monitoring APIs Enabled

- ✅ Cloud Monitoring API (`monitoring.googleapis.com`)
- ✅ Cloud Logging API (`logging.googleapis.com`)

---

## Alert Policies to Create

### 1. Load Balancer - High 5xx Error Rate

**Purpose**: Detect backend service issues causing server errors

**Configuration**:
- **Metric**: `loadbalancing.googleapis.com/https/request_count`
- **Filter**: `response_code_class="500"`
- **Condition**: Error rate > 5% of total requests
- **Duration**: 5 minutes
- **Severity**: Critical

**Alert Policy YAML**:
```yaml
displayName: "Load Balancer - High 5xx Error Rate"
documentation:
  content: "The Load Balancer is experiencing a high rate of 5xx errors (>5% of requests). This indicates backend service issues."
  mimeType: "text/markdown"
conditions:
  - displayName: "5xx error rate > 5%"
    conditionThreshold:
      filter: 'resource.type="https_lb_rule" AND metric.type="loadbalancing.googleapis.com/https/request_count" AND metric.label.response_code_class="500"'
      aggregations:
        - alignmentPeriod: "60s"
          perSeriesAligner: "ALIGN_RATE"
          crossSeriesReducer: "REDUCE_SUM"
          groupByFields:
            - "resource.url_map_name"
      comparison: "COMPARISON_GT"
      thresholdValue: 0.05
      duration: "300s"
combiner: "OR"
enabled: true
```

**Manual Creation Steps**:
1. Go to GCP Console → Monitoring → Alerting → Create Policy
2. Select metric: `Load Balancer Rule` → `Request count`
3. Filter: `response_code_class = "500"`
4. Set threshold: > 5% of requests
5. Set duration: 5 minutes
6. Add notification channel
7. Save policy

---

### 2. Load Balancer - High Latency

**Purpose**: Detect performance degradation

**Configuration**:
- **Metric**: `loadbalancing.googleapis.com/https/total_latencies`
- **Condition**: Average latency > 2 seconds
- **Duration**: 5 minutes
- **Severity**: Warning

**Alert Policy YAML**:
```yaml
displayName: "Load Balancer - High Latency"
documentation:
  content: "The Load Balancer is experiencing high latency (>2 seconds). This may indicate backend performance issues."
  mimeType: "text/markdown"
conditions:
  - displayName: "Latency > 2 seconds"
    conditionThreshold:
      filter: 'resource.type="https_lb_rule" AND metric.type="loadbalancing.googleapis.com/https/total_latencies"'
      aggregations:
        - alignmentPeriod: "60s"
          perSeriesAligner: "ALIGN_MEAN"
          crossSeriesReducer: "REDUCE_MEAN"
          groupByFields:
            - "resource.url_map_name"
      comparison: "COMPARISON_GT"
      thresholdValue: 2000
      duration: "300s"
combiner: "OR"
enabled: true
```

**Manual Creation Steps**:
1. Go to GCP Console → Monitoring → Alerting → Create Policy
2. Select metric: `Load Balancer Rule` → `Total latencies`
3. Set threshold: > 2000 ms (2 seconds)
4. Set duration: 5 minutes
5. Add notification channel
6. Save policy

---

### 3. IAP - High Authentication Failure Rate

**Purpose**: Detect authentication issues or unauthorized access attempts

**Configuration**:
- **Metric**: `loadbalancing.googleapis.com/https/request_count`
- **Filter**: `response_code="401"`
- **Condition**: > 10 failures per minute
- **Duration**: 5 minutes
- **Severity**: Warning

**Alert Policy YAML**:
```yaml
displayName: "IAP - High Authentication Failure Rate"
documentation:
  content: "IAP is experiencing a high rate of authentication failures. This may indicate configuration issues or unauthorized access attempts."
  mimeType: "text/markdown"
conditions:
  - displayName: "IAP auth failures > 10 per minute"
    conditionThreshold:
      filter: 'resource.type="gce_backend_service" AND metric.type="loadbalancing.googleapis.com/https/request_count" AND metric.label.response_code="401"'
      aggregations:
        - alignmentPeriod: "60s"
          perSeriesAligner: "ALIGN_RATE"
          crossSeriesReducer: "REDUCE_SUM"
      comparison: "COMPARISON_GT"
      thresholdValue: 10
      duration: "300s"
combiner: "OR"
enabled: true
```

**Manual Creation Steps**:
1. Go to GCP Console → Monitoring → Alerting → Create Policy
2. Select metric: `Backend Service` → `Request count`
3. Filter: `response_code = "401"`
4. Set threshold: > 10 per minute
5. Set duration: 5 minutes
6. Add notification channel
7. Save policy

---

### 4. Backend Service - Unhealthy

**Purpose**: Detect when backend services become unhealthy

**Configuration**:
- **Metric**: `loadbalancing.googleapis.com/https/backend_request_count`
- **Filter**: Backend service health status
- **Condition**: Any backend unhealthy
- **Duration**: 2 minutes
- **Severity**: Critical

**Manual Creation Steps**:
1. Go to GCP Console → Monitoring → Alerting → Create Policy
2. Select metric: `Backend Service` → `Health check status`
3. Set condition: Health status != HEALTHY
4. Set duration: 2 minutes
5. Add notification channel
6. Save policy

---

### 5. SSL Certificate - Expiring Soon

**Purpose**: Alert before SSL certificate expires

**Configuration**:
- **Metric**: `compute.googleapis.com/ssl_certificate/expiration_time`
- **Condition**: < 30 days until expiration
- **Severity**: Warning

**Manual Creation Steps**:
1. Go to GCP Console → Monitoring → Alerting → Create Policy
2. Select metric: `SSL Certificate` → `Expiration time`
3. Set condition: < 30 days
4. Add notification channel
5. Save policy

---

## Notification Channels

### Email Notification Channel

**Configuration**:
- **Type**: Email
- **Display Name**: Admin Infrastructure Alerts
- **Email Address**: tony@aletheiacodex.com
- **Description**: Email notifications for Load Balancer and IAP alerts

**Manual Creation Steps**:
1. Go to GCP Console → Monitoring → Alerting → Notification Channels
2. Click "Add New"
3. Select "Email"
4. Enter email address: tony@aletheiacodex.com
5. Enter display name: "Admin Infrastructure Alerts"
6. Save

---

## Monitoring Dashboard

### Dashboard Configuration

**Dashboard Name**: AletheiaCodex Load Balancer Monitoring

**Widgets to Include**:

1. **Request Rate**
   - Metric: `loadbalancing.googleapis.com/https/request_count`
   - Chart type: Line chart
   - Aggregation: Rate per minute
   - Group by: URL map

2. **Error Rate**
   - Metric: `loadbalancing.googleapis.com/https/request_count`
   - Filter: `response_code_class="500"`
   - Chart type: Line chart
   - Aggregation: Rate per minute

3. **Latency**
   - Metric: `loadbalancing.googleapis.com/https/total_latencies`
   - Chart type: Line chart
   - Aggregation: Mean
   - Percentiles: 50th, 95th, 99th

4. **Backend Health**
   - Metric: `loadbalancing.googleapis.com/https/backend_request_count`
   - Chart type: Stacked area chart
   - Group by: Backend service

5. **IAP Authentication Status**
   - Metric: `loadbalancing.googleapis.com/https/request_count`
   - Filter: `response_code IN ("200", "401", "403")`
   - Chart type: Stacked bar chart
   - Group by: Response code

6. **SSL Certificate Status**
   - Metric: `compute.googleapis.com/ssl_certificate/expiration_time`
   - Chart type: Scorecard
   - Display: Days until expiration

**Manual Creation Steps**:
1. Go to GCP Console → Monitoring → Dashboards → Create Dashboard
2. Name: "AletheiaCodex Load Balancer Monitoring"
3. Add widgets as described above
4. Arrange widgets in logical layout
5. Save dashboard

---

## Log-Based Metrics

### 1. IAP Authentication Failures

**Purpose**: Track IAP authentication failures over time

**Configuration**:
- **Metric Name**: `iap_auth_failures`
- **Metric Type**: Counter
- **Log Filter**: 
  ```
  resource.type="gce_backend_service"
  httpRequest.status=401
  ```

**Manual Creation Steps**:
1. Go to GCP Console → Logging → Logs-based Metrics
2. Click "Create Metric"
3. Select "Counter"
4. Enter metric name: `iap_auth_failures`
5. Enter log filter (above)
6. Save metric

---

### 2. Load Balancer 5xx Errors

**Purpose**: Track server errors over time

**Configuration**:
- **Metric Name**: `lb_5xx_errors`
- **Metric Type**: Counter
- **Log Filter**:
  ```
  resource.type="http_load_balancer"
  httpRequest.status>=500
  httpRequest.status<600
  ```

**Manual Creation Steps**:
1. Go to GCP Console → Logging → Logs-based Metrics
2. Click "Create Metric"
3. Select "Counter"
4. Enter metric name: `lb_5xx_errors`
5. Enter log filter (above)
6. Save metric

---

### 3. Backend Latency Distribution

**Purpose**: Track backend latency distribution

**Configuration**:
- **Metric Name**: `backend_latency_distribution`
- **Metric Type**: Distribution
- **Log Filter**:
  ```
  resource.type="gce_backend_service"
  httpRequest.latency>0
  ```
- **Value Field**: `httpRequest.latency`

**Manual Creation Steps**:
1. Go to GCP Console → Logging → Logs-based Metrics
2. Click "Create Metric"
3. Select "Distribution"
4. Enter metric name: `backend_latency_distribution`
5. Enter log filter (above)
6. Set value field: `httpRequest.latency`
7. Save metric

---

## Audit Logging Configuration

### IAP Audit Logging

**Purpose**: Track all IAP access and authentication events

**Configuration**:
- **Service**: `iap.googleapis.com`
- **Log Types**:
  - Admin Activity (ADMIN_READ)
  - Data Access (DATA_READ, DATA_WRITE)

**Manual Configuration Steps**:
1. Go to GCP Console → IAM & Admin → Audit Logs
2. Find "Cloud IAP API"
3. Enable:
   - Admin Read
   - Data Read
   - Data Write
4. Save configuration

---

### Load Balancer Audit Logging

**Purpose**: Track Load Balancer configuration changes

**Configuration**:
- **Service**: `compute.googleapis.com`
- **Log Types**:
  - Admin Activity (enabled by default)

**Verification**:
```bash
# View Load Balancer audit logs
gcloud logging read "resource.type=http_load_balancer" --limit=10
```

---

## Log Queries

### Useful Log Queries

**1. View all Load Balancer requests**:
```
resource.type="http_load_balancer"
```

**2. View 5xx errors**:
```
resource.type="http_load_balancer"
httpRequest.status>=500
httpRequest.status<600
```

**3. View IAP authentication failures**:
```
resource.type="gce_backend_service"
httpRequest.status=401
```

**4. View high latency requests (>2 seconds)**:
```
resource.type="http_load_balancer"
httpRequest.latency>2s
```

**5. View requests by backend service**:
```
resource.type="gce_backend_service"
resource.labels.backend_service_name="backend-graphfunction"
```

**6. View IAP access logs**:
```
protoPayload.serviceName="iap.googleapis.com"
```

---

## Monitoring Best Practices

### 1. Regular Review
- Review dashboards daily
- Check alert policies weekly
- Review logs for anomalies

### 2. Alert Tuning
- Adjust thresholds based on actual traffic patterns
- Reduce false positives
- Ensure critical alerts are actionable

### 3. Log Retention
- Default retention: 30 days
- Consider longer retention for audit logs
- Export logs to Cloud Storage for long-term retention

### 4. Performance Monitoring
- Monitor latency percentiles (50th, 95th, 99th)
- Track error rates by endpoint
- Monitor backend health continuously

### 5. Security Monitoring
- Monitor IAP authentication failures
- Track unauthorized access attempts
- Review audit logs regularly

---

## Troubleshooting with Logs

### Debugging 5xx Errors

```bash
# Find recent 5xx errors
gcloud logging read "resource.type=http_load_balancer AND httpRequest.status>=500" \
  --limit=50 \
  --format=json

# Group by backend service
gcloud logging read "resource.type=gce_backend_service AND httpRequest.status>=500" \
  --limit=50 \
  --format="table(resource.labels.backend_service_name, httpRequest.status, timestamp)"
```

### Debugging IAP Issues

```bash
# View IAP authentication failures
gcloud logging read "resource.type=gce_backend_service AND httpRequest.status=401" \
  --limit=50 \
  --format=json

# View IAP access logs
gcloud logging read "protoPayload.serviceName=iap.googleapis.com" \
  --limit=50 \
  --format=json
```

### Debugging Latency Issues

```bash
# Find slow requests
gcloud logging read "resource.type=http_load_balancer AND httpRequest.latency>2s" \
  --limit=50 \
  --format="table(httpRequest.requestUrl, httpRequest.latency, timestamp)"
```

---

## Monitoring Checklist

### Initial Setup
- [ ] Create notification channels
- [ ] Create alert policies (5 policies)
- [ ] Create monitoring dashboard
- [ ] Create log-based metrics (3 metrics)
- [ ] Enable IAP audit logging
- [ ] Test alert notifications

### Ongoing Maintenance
- [ ] Review dashboards daily
- [ ] Check alert policies weekly
- [ ] Review logs for anomalies
- [ ] Tune alert thresholds as needed
- [ ] Export logs for long-term retention

---

## Next Steps

1. **Create Notification Channels** (Priority 1):
   - Email channel for admin alerts
   - Consider Slack/PagerDuty integration

2. **Create Alert Policies** (Priority 2):
   - High 5xx error rate
   - High latency
   - IAP authentication failures
   - Backend service health
   - SSL certificate expiration

3. **Create Dashboard** (Priority 3):
   - Request rate and error rate
   - Latency percentiles
   - Backend health
   - IAP authentication status

4. **Create Log-Based Metrics** (Priority 4):
   - IAP authentication failures
   - Load Balancer 5xx errors
   - Backend latency distribution

5. **Enable Audit Logging** (Priority 5):
   - IAP audit logging
   - Verify Load Balancer audit logging

---

## Resources

- [Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs)
- [Cloud Logging Documentation](https://cloud.google.com/logging/docs)
- [Load Balancer Monitoring](https://cloud.google.com/load-balancing/docs/https/https-logging-monitoring)
- [IAP Monitoring](https://cloud.google.com/iap/docs/monitoring)

---

**Status**: Configuration documented and ready for manual setup via GCP Console

**Estimated Setup Time**: 30-45 minutes

---

**Admin-Infrastructure**  
Sprint 1 - Feature 5  
2025-01-18