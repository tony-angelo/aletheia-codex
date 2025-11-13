# Monitoring and Logging Configuration

**Date**: 2025-01-18  
**Sprint**: Sprint 1 - Feature 5  
**Status**: ✅ COMPLETED - Alert Policies Created  

---

## Overview

This document provides comprehensive monitoring and logging configuration for the AletheiaCodeex Load Balancer and IAP infrastructure. All alert policies have been successfully created and are actively monitoring the infrastructure.

---

## Monitoring APIs Enabled

- ✅ Cloud Monitoring API (`monitoring.googleapis.com`)
- ✅ Cloud Logging API (`logging.googleapis.com`)

---

## Alert Policies Created

All alert policies have been successfully created and are enabled. They can be viewed and managed in the GCP Console under **Monitoring > Alerting**.

### 1. High 5xx Error Rate - Load Balancer

**Status**: ✅ Created  
**Policy ID**: `projects/aletheia-codex-prod/alertPolicies/11807777933107518504`

**Purpose**: Detect backend service issues causing server errors

**Configuration**:
- **Metric**: `loadbalancing.googleapis.com/https/request_count`
- **Filter**: `response_code_class="500"`
- **Condition**: Error rate > 5% of total requests
- **Duration**: 5 minutes
- **Severity**: Critical

**What it monitors**: Tracks the rate of 5xx errors from the load balancer. If more than 5% of requests result in 5xx errors for 5 consecutive minutes, an alert is triggered.

**Response Actions**:
1. Check Cloud Functions logs for errors
2. Verify backend service health
3. Check for recent deployments or configuration changes
4. Review IAP authentication status

---

### 2. High Latency - Load Balancer

**Status**: ✅ Created  
**Policy ID**: `projects/aletheia-codex-prod/alertPolicies/16910070354310142149`

**Purpose**: Detect performance degradation

**Configuration**:
- **Metric**: `loadbalancing.googleapis.com/https/total_latencies`
- **Condition**: 95th percentile latency > 2000ms
- **Duration**: 5 minutes
- **Severity**: Warning

**What it monitors**: Tracks the 95th percentile of request latency. If latency exceeds 2000ms for 5 consecutive minutes, an alert is triggered.

**Response Actions**:
1. Check Cloud Functions performance metrics
2. Review backend service capacity
3. Investigate network issues
4. Check for resource constraints

---

### 3. IAP Authentication Failures

**Status**: ✅ Created  
**Policy ID**: `projects/aletheia-codex-prod/alertPolicies/1396428189256821344`

**Purpose**: Detect IAP authentication issues

**Configuration**:
- **Metric**: `loadbalancing.googleapis.com/https/request_count`
- **Filter**: `response_code="401"`
- **Condition**: > 10 authentication failures per minute
- **Duration**: 1 minute
- **Severity**: Warning

**What it monitors**: Tracks 401 (Unauthorized) responses from the load balancer. If more than 10 authentication failures occur within a minute, an alert is triggered.

**Response Actions**:
1. Review IAP configuration
2. Check OAuth consent screen settings
3. Verify user permissions
4. Review audit logs for unauthorized access attempts

---

### 4. Backend Service Unhealthy

**Status**: ✅ Created  
**Policy ID**: `projects/aletheia-codex-prod/alertPolicies/6446748369727870470`

**Purpose**: Detect backend service failures

**Configuration**:
- **Metric**: `loadbalancing.googleapis.com/https/backend_request_count`
- **Filter**: `response_code_class="500"`
- **Condition**: > 1 error per minute
- **Duration**: 5 minutes
- **Severity**: Critical

**What it monitors**: Tracks 5xx errors from backend services. If any backend consistently returns errors for 5 minutes, an alert is triggered.

**Response Actions**:
1. Check specific Cloud Function status
2. Review function logs for errors
3. Verify function configuration
4. Check for resource limits or quotas

---

### 5. SSL Certificate Issues

**Status**: ✅ Created  
**Policy ID**: `projects/aletheia-codex-prod/alertPolicies/3481716832413018000`

**Purpose**: Detect SSL/TLS certificate problems

**Configuration**:
- **Metric**: `loadbalancing.googleapis.com/https/request_count`
- **Filter**: `response_code_class="400"`
- **Condition**: > 5 errors per 5 minutes
- **Duration**: 5 minutes
- **Severity**: Warning

**What it monitors**: Tracks 4xx errors that may indicate SSL handshake failures or certificate issues.

**Response Actions**:
1. Verify SSL certificate status in Load Balancer settings
2. Check certificate expiration date
3. Verify DNS configuration
4. Review certificate provisioning logs

---

## Adding Notification Channels

Alert policies are created but do not have notification channels configured. To receive alerts:

### Via GCP Console:

1. Navigate to **Cloud Console > Monitoring > Alerting**
2. Click on an alert policy
3. Click **Edit**
4. Under **Notifications**, click **Add Notification Channel**
5. Select or create a notification channel (Email, Slack, PagerDuty, etc.)
6. Save the policy

### Supported Notification Channel Types:

- **Email**: Send alerts to email addresses
- **Slack**: Post alerts to Slack channels
- **PagerDuty**: Create incidents in PagerDuty
- **Webhooks**: Send alerts to custom endpoints
- **SMS**: Send text message alerts (via third-party integrations)
- **Mobile Push**: Send push notifications to mobile devices

---

## Monitoring Dashboard

### Recommended Dashboard Widgets:

Create a custom dashboard in **Cloud Console > Monitoring > Dashboards** with the following widgets:

1. **Request Rate**
   - Metric: `loadbalancing.googleapis.com/https/request_count`
   - Chart Type: Line chart
   - Aggregation: Rate

2. **Error Rate**
   - Metric: `loadbalancing.googleapis.com/https/request_count`
   - Filter: `response_code_class="500"`
   - Chart Type: Line chart
   - Aggregation: Rate

3. **Latency (95th Percentile)**
   - Metric: `loadbalancing.googleapis.com/https/total_latencies`
   - Chart Type: Line chart
   - Aggregation: 95th percentile

4. **Backend Health**
   - Metric: `loadbalancing.googleapis.com/https/backend_request_count`
   - Chart Type: Stacked area chart
   - Group by: `backend_target_name`

5. **IAP Authentication Status**
   - Metric: `loadbalancing.googleapis.com/https/request_count`
   - Filter: `response_code IN ("200", "401", "403")`
   - Chart Type: Stacked bar chart
   - Group by: `response_code`

---

## Log-Based Metrics

### Recommended Log-Based Metrics:

Create these in **Cloud Console > Logging > Logs-based Metrics**:

1. **IAP Access Denied**
   - **Filter**: 
     ```
     resource.type="gce_backend_service"
     protoPayload.status.code=7
     protoPayload.authenticationInfo.principalEmail!=""
     ```
   - **Metric Type**: Counter
   - **Purpose**: Track IAP access denials

2. **Backend Function Errors**
   - **Filter**:
     ```
     resource.type="cloud_function"
     severity="ERROR"
     ```
   - **Metric Type**: Counter
   - **Purpose**: Track Cloud Function errors

3. **Load Balancer 5xx Errors**
   - **Filter**:
     ```
     resource.type="http_load_balancer"
     httpRequest.status>=500
     ```
   - **Metric Type**: Counter
   - **Purpose**: Track all 5xx errors

---

## IAP Audit Logging

IAP audit logs are automatically enabled and can be viewed in Cloud Logging.

### Key Log Types:

1. **IAP Authentication Events**
   - Log Name: `projects/aletheia-codex-prod/logs/cloudaudit.googleapis.com%2Fdata_access`
   - Resource Type: `gce_backend_service`

2. **IAP Policy Changes**
   - Log Name: `projects/aletheia-codex-prod/logs/cloudaudit.googleapis.com%2Factivity`
   - Resource Type: `iap_web`

### Useful Log Queries:

**View all IAP authentication attempts:**
```
resource.type="gce_backend_service"
protoPayload.serviceName="iap.googleapis.com"
```

**View failed authentication attempts:**
```
resource.type="gce_backend_service"
protoPayload.serviceName="iap.googleapis.com"
protoPayload.status.code!=0
```

**View successful authentications:**
```
resource.type="gce_backend_service"
protoPayload.serviceName="iap.googleapis.com"
protoPayload.status.code=0
```

---

## Troubleshooting Guide

### High 5xx Error Rate

**Symptoms**: Alert triggered for high 5xx error rate

**Investigation Steps**:
1. Check Cloud Functions logs:
   ```bash
   gcloud functions logs read --limit=50
   ```

2. Check backend service status:
   ```bash
   gcloud compute backend-services list
   ```

3. Review recent deployments:
   ```bash
   gcloud functions list --format="table(name,status,updateTime)"
   ```

**Common Causes**:
- Cloud Function errors or crashes
- Resource exhaustion (memory, CPU)
- Timeout issues
- Dependency failures

---

### High Latency

**Symptoms**: Alert triggered for high latency

**Investigation Steps**:
1. Check function execution times in Cloud Console
2. Review function logs for slow operations
3. Check for cold starts
4. Verify backend service configuration

**Common Causes**:
- Cold starts (first invocation after idle period)
- Slow database queries
- External API calls
- Insufficient resources

---

### IAP Authentication Failures

**Symptoms**: Alert triggered for authentication failures

**Investigation Steps**:
1. Check IAP configuration:
   ```bash
   gcloud iap web get-iam-policy --resource-type=backend-services --service=<service-name>
   ```

2. Review audit logs for access attempts
3. Verify OAuth consent screen configuration
4. Check user permissions

**Common Causes**:
- Incorrect IAM permissions
- OAuth consent screen issues
- Expired or invalid tokens
- User not in allowed list

---

### Backend Service Unhealthy

**Symptoms**: Alert triggered for backend errors

**Investigation Steps**:
1. Check specific backend service:
   ```bash
   gcloud compute backend-services describe <service-name> --global
   ```

2. Check Cloud Function status:
   ```bash
   gcloud functions describe <function-name>
   ```

3. Review function logs for errors

**Common Causes**:
- Function deployment issues
- Configuration errors
- Resource limits exceeded
- Network connectivity problems

---

## Maintenance Tasks

### Weekly:
- Review alert policy effectiveness
- Check for false positives
- Verify notification channels are working

### Monthly:
- Review dashboard metrics for trends
- Adjust alert thresholds if needed
- Archive old logs (if needed)
- Review IAP access patterns

### Quarterly:
- Review and update alert policies
- Optimize log-based metrics
- Update documentation
- Review monitoring costs

---

## Scripts

### Setup Alert Policies

All alert policies have been created using:

```bash
./infrastructure/monitoring/setup-alert-policies.sh
```

This script creates all 5 alert policies from YAML configuration files.

### List Alert Policies

```bash
gcloud alpha monitoring policies list --format="table(name,displayName,enabled)"
```

### View Specific Alert Policy

```bash
gcloud alpha monitoring policies describe <policy-id>
```

---

## Resources

- [Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs)
- [Cloud Logging Documentation](https://cloud.google.com/logging/docs)
- [IAP Monitoring Guide](https://cloud.google.com/iap/docs/monitoring)
- [Load Balancer Monitoring](https://cloud.google.com/load-balancing/docs/https/https-logging-monitoring)

---

## Summary

✅ **Monitoring APIs**: Enabled  
✅ **Alert Policies**: 5 policies created and enabled  
⚠️ **Notification Channels**: Need to be configured manually  
📊 **Dashboard**: Recommended widgets documented  
📝 **Log-Based Metrics**: Recommended metrics documented  
🔍 **Audit Logging**: Enabled and documented  

**Next Steps**:
1. Add notification channels to alert policies
2. Create monitoring dashboard with recommended widgets
3. Create log-based metrics
4. Test alert policies by triggering conditions
5. Document incident response procedures