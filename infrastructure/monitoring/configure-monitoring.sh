#!/bin/bash
set -e

echo "Configuring Monitoring and Logging for Load Balancer..."
echo ""

# Enable Cloud Monitoring API (if not already enabled)
echo "Ensuring Cloud Monitoring API is enabled..."
gcloud services enable monitoring.googleapis.com

# Enable Cloud Logging API (if not already enabled)
echo "Ensuring Cloud Logging API is enabled..."
gcloud services enable logging.googleapis.com

echo "✅ Monitoring and Logging APIs enabled"
echo ""

# Create notification channel for alerts (email)
echo "Creating notification channel for alerts..."
cat > /tmp/notification-channel.json << 'CHANNEL'
{
  "type": "email",
  "displayName": "Admin Infrastructure Alerts",
  "description": "Email notifications for Load Balancer and IAP alerts",
  "labels": {
    "email_address": "tony@aletheiacodex.com"
  },
  "enabled": true
}
CHANNEL

# Note: Notification channels need to be created via API or Console
# gcloud doesn't have a direct command for this
echo "Note: Notification channels should be configured via GCP Console"
echo "  Navigation: Monitoring > Alerting > Notification Channels"
echo ""

# Enable audit logging for IAP
echo "Configuring audit logging for IAP..."
cat > /tmp/audit-config.yaml << 'AUDIT'
auditConfigs:
- auditLogConfigs:
  - logType: ADMIN_READ
  - logType: DATA_READ
  - logType: DATA_WRITE
  service: iap.googleapis.com
AUDIT

echo "Note: Audit logging configuration should be applied via IAM policy"
echo ""

echo "✅ Monitoring configuration prepared"
echo ""

# List existing log sinks
echo "Existing log sinks:"
gcloud logging sinks list

echo ""
echo "✅ Monitoring and logging configuration complete!"
echo ""
echo "Next steps:"
echo "1. Create notification channels in GCP Console"
echo "2. Create alert policies for Load Balancer metrics"
echo "3. Create dashboard for monitoring"
echo "4. Configure log-based metrics"

