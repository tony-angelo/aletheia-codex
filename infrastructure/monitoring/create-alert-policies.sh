#!/bin/bash
set -e

echo "Creating alert policies for Load Balancer monitoring..."
echo ""

# Create alert policy for high error rate
echo "Creating alert policy for high error rate (5xx errors)..."
cat > /tmp/alert-5xx-errors.yaml << 'ALERT'
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
ALERT

gcloud alpha monitoring policies create --policy-from-file=/tmp/alert-5xx-errors.yaml 2>&1 || echo "Note: Alert policy creation may require alpha API or Console"

echo ""

# Create alert policy for high latency
echo "Creating alert policy for high latency..."
cat > /tmp/alert-high-latency.yaml << 'ALERT'
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
ALERT

gcloud alpha monitoring policies create --policy-from-file=/tmp/alert-high-latency.yaml 2>&1 || echo "Note: Alert policy creation may require alpha API or Console"

echo ""

# Create alert policy for IAP authentication failures
echo "Creating alert policy for IAP authentication failures..."
cat > /tmp/alert-iap-failures.yaml << 'ALERT'
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
ALERT

gcloud alpha monitoring policies create --policy-from-file=/tmp/alert-iap-failures.yaml 2>&1 || echo "Note: Alert policy creation may require alpha API or Console"

echo ""
echo "✅ Alert policy configurations created"
echo ""
echo "Note: Alert policies may need to be created via GCP Console if alpha API is not available"
echo "  Navigation: Monitoring > Alerting > Create Policy"
echo ""

# List existing alert policies
echo "Listing existing alert policies..."
gcloud alpha monitoring policies list 2>&1 || echo "Use GCP Console to view alert policies"

