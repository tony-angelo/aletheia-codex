#!/bin/bash

# Domain Setup Automation Script for Aletheia Codex
# This script helps automate the custom domain setup process

set -e

PROJECT_ID="aletheia-codex-prod"
DOMAIN="aletheiacodex.app"
DNS_ZONE="aletheiacodex-app"
REGION="us-central1"

echo "=========================================="
echo "Aletheia Codex Custom Domain Setup"
echo "=========================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."
if ! command_exists gcloud; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

if ! command_exists dig; then
    echo "⚠️  dig command not found. Installing dnsutils..."
    sudo apt-get update && sudo apt-get install -y dnsutils
fi

echo "✅ Prerequisites checked"
echo ""

# Check DNS propagation
echo "=========================================="
echo "Step 1: Checking DNS Propagation"
echo "=========================================="
echo ""

echo "Checking current nameservers for $DOMAIN..."
CURRENT_NS=$(dig +short $DOMAIN NS | head -1)

if [[ -z "$CURRENT_NS" ]]; then
    echo "⚠️  No nameservers found. Domain may not be registered or DNS not configured."
    echo ""
    echo "Expected nameservers:"
    gcloud dns managed-zones describe $DNS_ZONE --format="value(nameServers)" | tr ';' '\n'
    echo ""
    echo "Please update your domain registrar to use these nameservers."
    echo "Then run this script again."
    exit 1
fi

echo "Current nameservers:"
dig +short $DOMAIN NS

echo ""
echo "Expected nameservers:"
gcloud dns managed-zones describe $DNS_ZONE --format="value(nameServers)" | tr ';' '\n'

echo ""
read -p "Do the nameservers match? (y/n): " NS_MATCH

if [[ "$NS_MATCH" != "y" ]]; then
    echo ""
    echo "⚠️  Nameservers don't match. Please update at your registrar first."
    echo "Then run this script again after DNS propagation (1-48 hours)."
    exit 1
fi

echo "✅ Nameservers configured correctly"
echo ""

# Check domain verification
echo "=========================================="
echo "Step 2: Domain Verification"
echo "=========================================="
echo ""

echo "Checking if domain is verified..."
VERIFIED=$(gcloud domains list-user-verified 2>/dev/null | grep -c "$DOMAIN" || echo "0")

if [[ "$VERIFIED" == "0" ]]; then
    echo "⚠️  Domain not verified yet."
    echo ""
    echo "Please verify your domain ownership using one of these methods:"
    echo ""
    echo "Option 1: Google Search Console"
    echo "  1. Go to: https://search.google.com/search-console"
    echo "  2. Add property: $DOMAIN"
    echo "  3. Follow verification steps"
    echo ""
    echo "Option 2: Firebase Console"
    echo "  1. Go to: https://console.firebase.google.com/project/$PROJECT_ID/hosting/sites"
    echo "  2. Click 'Add custom domain'"
    echo "  3. Enter: $DOMAIN"
    echo "  4. Follow verification steps"
    echo ""
    read -p "Press Enter after you've completed domain verification..."
    
    # Check again
    VERIFIED=$(gcloud domains list-user-verified 2>/dev/null | grep -c "$DOMAIN" || echo "0")
    if [[ "$VERIFIED" == "0" ]]; then
        echo "❌ Domain still not verified. Please complete verification first."
        exit 1
    fi
fi

echo "✅ Domain verified"
echo ""

# Add DNS records
echo "=========================================="
echo "Step 3: DNS Records Configuration"
echo "=========================================="
echo ""

echo "This step will add DNS records to your Google Cloud DNS zone."
echo ""
read -p "Do you want to proceed with adding DNS records? (y/n): " ADD_RECORDS

if [[ "$ADD_RECORDS" == "y" ]]; then
    echo ""
    echo "Adding DNS records..."
    
    # Check if records already exist
    EXISTING_A=$(gcloud dns record-sets list --zone=$DNS_ZONE --name="$DOMAIN." --type=A 2>/dev/null | grep -c "$DOMAIN" || echo "0")
    
    if [[ "$EXISTING_A" == "0" ]]; then
        echo "Note: Firebase Hosting will provide specific IP addresses."
        echo "Please add the custom domain in Firebase Console first:"
        echo "https://console.firebase.google.com/project/$PROJECT_ID/hosting/sites"
        echo ""
        echo "After Firebase provides the IP addresses, you can add them manually:"
        echo ""
        echo "gcloud dns record-sets create $DOMAIN. \&quot;
        echo "  --zone=$DNS_ZONE \&quot;
        echo "  --type=A \&quot;
        echo "  --ttl=3600 \&quot;
        echo "  --rrdatas=IP1,IP2"
    else
        echo "✅ A records already exist for $DOMAIN"
    fi
    
    echo ""
    
    # Add CNAME for api subdomain
    EXISTING_API=$(gcloud dns record-sets list --zone=$DNS_ZONE --name="api.$DOMAIN." --type=CNAME 2>/dev/null | grep -c "api.$DOMAIN" || echo "0")
    
    if [[ "$EXISTING_API" == "0" ]]; then
        echo "Adding CNAME record for api.$DOMAIN..."
        gcloud dns record-sets create "api.$DOMAIN." \
          --zone=$DNS_ZONE \
          --type=CNAME \
          --ttl=3600 \
          --rrdatas="ghs.googlehosted.com."
        echo "✅ CNAME record added for api.$DOMAIN"
    else
        echo "✅ CNAME record already exists for api.$DOMAIN"
    fi
    
    echo ""
fi

# Test DNS records
echo "=========================================="
echo "Step 4: Testing DNS Configuration"
echo "=========================================="
echo ""

echo "Testing DNS records..."
echo ""

echo "Nameservers:"
dig +short $DOMAIN NS
echo ""

echo "A records for $DOMAIN:"
dig +short $DOMAIN A
echo ""

echo "CNAME record for api.$DOMAIN:"
dig +short api.$DOMAIN CNAME
echo ""

# Domain mapping instructions
echo "=========================================="
echo "Step 5: Cloud Run Domain Mapping"
echo "=========================================="
echo ""

echo "After domain verification is complete, map domains to Cloud Run services:"
echo ""
echo "For Review API:"
echo "gcloud beta run domain-mappings create \&quot;
echo "  --service=review-api \&quot;
echo "  --domain=api.$DOMAIN \&quot;
echo "  --region=$REGION"
echo ""
echo "For Graph API:"
echo "gcloud beta run domain-mappings create \&quot;
echo "  --service=graph \&quot;
echo "  --domain=graph.$DOMAIN \&quot;
echo "  --region=$REGION"
echo ""

read -p "Do you want to attempt domain mapping now? (y/n): " MAP_NOW

if [[ "$MAP_NOW" == "y" ]]; then
    echo ""
    echo "Attempting to map api.$DOMAIN to review-api..."
    if gcloud beta run domain-mappings create \
        --service=review-api \
        --domain=api.$DOMAIN \
        --region=$REGION 2>&1; then
        echo "✅ Successfully mapped api.$DOMAIN to review-api"
    else
        echo "⚠️  Domain mapping failed. This is expected if domain verification is not complete."
        echo "Please complete domain verification first, then run the mapping commands manually."
    fi
fi

echo ""
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo ""
echo "✅ DNS zone created: $DNS_ZONE"
echo "✅ Nameservers configured"
echo "✅ DNS records added (or instructions provided)"
echo ""
echo "Next steps:"
echo "1. Wait for DNS propagation (1-48 hours, typically 2-4 hours)"
echo "2. Verify domain ownership if not already done"
echo "3. Add custom domain in Firebase Console for hosting"
echo "4. Map Cloud Run domains for API endpoints"
echo "5. Test the application at https://$DOMAIN"
echo ""
echo "For detailed instructions, see:"
echo "- CUSTOM_DOMAIN_SETUP.md"
echo "- DNS_RECORDS_REFERENCE.md"
echo ""