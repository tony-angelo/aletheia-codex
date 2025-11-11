# Custom Domain Setup Guide for Aletheia Codex

## Overview
This guide will help you set up `aletheiacodex.app` as a custom domain for your Aletheia Codex application to potentially bypass the GCP organization policy restrictions.

## Current Status
✅ Cloud DNS zone created: `aletheiacodex-app`
✅ DNS Administrator permissions granted
✅ Service Usage Admin permissions granted
⏳ Domain verification needed
⏳ DNS records need to be added at registrar

## Step 1: Point Your Domain to Google Cloud DNS

You need to update the nameservers at your domain registrar to point to Google Cloud DNS.

### Nameservers to Use:
```
ns-cloud-c1.googledomains.com
ns-cloud-c2.googledomains.com
ns-cloud-c3.googledomains.com
ns-cloud-c4.googledomains.com
```

### How to Update Nameservers:
1. Log in to your domain registrar (where you purchased aletheiacodex.app)
2. Find the DNS or Nameserver settings
3. Replace the existing nameservers with the Google Cloud nameservers listed above
4. Save the changes
5. Wait for DNS propagation (can take 24-48 hours, but often faster)

## Step 2: Verify Domain Ownership

Once the nameservers are updated and propagated, we need to verify domain ownership.

### Option A: Using Google Search Console (Recommended)
1. Go to [Google Search Console](https://search.google.com/search-console)
2. Add property: `aletheiacodex.app`
3. Choose verification method:
   - **DNS record** (recommended): Add a TXT record to your DNS
   - **HTML file upload**: Upload a file to your website
   - **HTML tag**: Add a meta tag to your homepage

### Option B: Using Firebase Hosting
1. Go to [Firebase Console](https://console.firebase.google.com/project/aletheia-codex-prod/hosting/sites)
2. Click on your hosting site
3. Click "Add custom domain"
4. Enter `aletheiacodex.app`
5. Follow the verification steps provided

## Step 3: DNS Records Configuration

After domain verification, we'll need to add the following DNS records:

### For Firebase Hosting (Main Site)
```
Type: A
Name: @
Value: [Firebase will provide IP addresses]
TTL: 3600

Type: A
Name: www
Value: [Firebase will provide IP addresses]
TTL: 3600
```

### For API Subdomain
```
Type: CNAME
Name: api
Value: ghs.googlehosted.com.
TTL: 3600
```

### For SSL Certificate Verification
Firebase will provide additional TXT records for SSL certificate verification.

## Step 4: Alternative Approach - Direct Cloud Run Domain Mapping

If the Firebase Hosting approach doesn't bypass the organization policy, we can try direct Cloud Run domain mappings:

### Prerequisites:
1. Domain must be verified in Google Search Console
2. Add DNS records as instructed by Cloud Run

### Commands to Run:
```bash
# Map api.aletheiacodex.app to review-api
gcloud beta run domain-mappings create \
  --service=review-api \
  --domain=api.aletheiacodex.app \
  --region=us-central1

# Map graph.aletheiacodex.app to graph function
gcloud beta run domain-mappings create \
  --service=graph \
  --domain=graph.aletheiacodex.app \
  --region=us-central1
```

## Step 5: Update Frontend Configuration

Once domains are mapped, update the frontend to use the custom domains:

```typescript
// web/src/services/api.ts
const API_BASE_URL = 'https://api.aletheiacodex.app';

// web/src/services/graphService.ts
const GRAPH_API_URL = 'https://graph.aletheiacodex.app';
```

## Testing the Setup

After all DNS records are propagated and domains are mapped:

1. Test main site: `https://aletheiacodex.app`
2. Test API endpoint: `https://api.aletheiacodex.app/health`
3. Test Graph API: `https://graph.aletheiacodex.app/health`

## Troubleshooting

### DNS Not Propagating
- Use `dig aletheiacodex.app` to check DNS records
- Use online tools like [whatsmydns.net](https://www.whatsmydns.net/)
- Wait up to 48 hours for full propagation

### Domain Verification Failing
- Ensure nameservers are correctly updated
- Wait for DNS propagation before attempting verification
- Try alternative verification methods (HTML file, meta tag)

### SSL Certificate Issues
- Firebase automatically provisions SSL certificates
- This can take 24-48 hours after domain verification
- Ensure all required DNS records are added

### Organization Policy Still Blocking
If custom domains don't bypass the policy, we'll need to:
1. Contact GCP organization administrator for policy exception
2. OR implement API Gateway as a workaround
3. OR migrate to App Engine

## Timeline

- **Nameserver Update**: 5 minutes (at registrar)
- **DNS Propagation**: 1-48 hours (typically 2-4 hours)
- **Domain Verification**: 5-10 minutes (after propagation)
- **Domain Mapping**: 5-10 minutes
- **SSL Certificate**: 1-48 hours (automatic)
- **Total**: 2-96 hours (typically 4-8 hours)

## Next Steps

1. ✅ Update nameservers at your registrar (do this first)
2. ⏳ Wait for DNS propagation
3. ⏳ Verify domain ownership
4. ⏳ Add DNS records for domain mapping
5. ⏳ Test the application

## Support

If you encounter any issues during this process, please provide:
- Current step you're on
- Error messages (if any)
- Output of `dig aletheiacodex.app` command
- Screenshots of registrar DNS settings (if relevant)