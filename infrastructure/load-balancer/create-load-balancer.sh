#!/bin/bash
set -e

echo "Creating Load Balancer components..."
echo ""

# Create Google-managed SSL certificate
echo "Creating Google-managed SSL certificate..."
gcloud compute ssl-certificates create aletheia-ssl-cert \
    --domains=aletheiacodex.app,www.aletheiacodex.app \
    --global

echo "✅ SSL certificate created (provisioning may take 15-60 minutes)"
echo ""

# Create target HTTPS proxy
echo "Creating target HTTPS proxy..."
gcloud compute target-https-proxies create aletheia-https-proxy \
    --url-map=aletheia-lb-url-map \
    --ssl-certificates=aletheia-ssl-cert \
    --global

echo "✅ Target HTTPS proxy created"
echo ""

# Reserve a static IP address
echo "Reserving static IP address..."
gcloud compute addresses create aletheia-lb-ip \
    --ip-version=IPV4 \
    --global

echo "✅ Static IP address reserved"
echo ""

# Get the reserved IP address
LB_IP=$(gcloud compute addresses describe aletheia-lb-ip --global --format="get(address)")
echo "Load Balancer IP: $LB_IP"
echo ""

# Create forwarding rule
echo "Creating forwarding rule..."
gcloud compute forwarding-rules create aletheia-https-forwarding-rule \
    --address=aletheia-lb-ip \
    --global \
    --target-https-proxy=aletheia-https-proxy \
    --ports=443

echo "✅ Forwarding rule created"
echo ""

echo "=========================================="
echo "✅ Load Balancer Created Successfully!"
echo "=========================================="
echo ""
echo "Load Balancer IP: $LB_IP"
echo "Load Balancer URL: https://aletheiacodex.app"
echo ""
echo "IMPORTANT: Configure DNS A record:"
echo "  aletheiacodex.app -> $LB_IP"
echo "  www.aletheiacodex.app -> $LB_IP"
echo ""
echo "SSL Certificate Status:"
gcloud compute ssl-certificates describe aletheia-ssl-cert --global --format="get(managed.status)"
echo ""
echo "Note: SSL certificate provisioning can take 15-60 minutes after DNS is configured."
echo ""

