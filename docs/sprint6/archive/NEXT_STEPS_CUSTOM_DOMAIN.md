# Next Steps for Custom Domain Setup

## Current Status

✅ **Completed:**
- Cloud DNS zone created for `aletheiacodex.app`
- DNS Administrator permissions granted to service account
- Service Usage Admin permissions granted to service account
- Automation scripts and documentation created

⏳ **Pending (Your Action Required):**
- Update nameservers at domain registrar
- Verify domain ownership
- Add DNS records
- Map domains to Cloud Run services

## Immediate Action Required

### Step 1: Update Nameservers at Your Registrar

You need to log in to your domain registrar (where you purchased `aletheiacodex.app`) and update the nameservers to:

```
ns-cloud-c1.googledomains.com
ns-cloud-c2.googledomains.com
ns-cloud-c3.googledomains.com
ns-cloud-c4.googledomains.com
```

**How to do this:**
1. Log in to your domain registrar's control panel
2. Find DNS settings or Nameserver settings
3. Replace existing nameservers with the Google Cloud nameservers above
4. Save changes
5. Wait for DNS propagation (1-48 hours, typically 2-4 hours)

### Step 2: Verify DNS Propagation

After updating nameservers, check if they've propagated:

```bash
# Check nameservers
dig aletheiacodex.app NS

# Or use online tools
# https://www.whatsmydns.net/
# https://dnschecker.org/
```

### Step 3: Verify Domain Ownership

Once nameservers are propagated, verify domain ownership using one of these methods:

**Option A: Google Search Console (Recommended)**
1. Go to https://search.google.com/search-console
2. Add property: `aletheiacodex.app`
3. Choose DNS verification method
4. Add the TXT record provided by Google to your DNS zone
5. Click "Verify"

**Option B: Firebase Console**
1. Go to https://console.firebase.google.com/project/aletheia-codex-prod/hosting/sites
2. Click on your hosting site
3. Click "Add custom domain"
4. Enter `aletheiacodex.app`
5. Follow the verification steps

### Step 4: Run the Automation Script

After domain verification, run the automation script to help with DNS configuration:

```bash
cd aletheia-codex
./DOMAIN_SETUP_AUTOMATION.sh
```

This script will:
- Check DNS propagation
- Verify domain ownership status
- Add DNS records to Google Cloud DNS
- Provide instructions for domain mapping

### Step 5: Add Custom Domain in Firebase Console

1. Go to https://console.firebase.google.com/project/aletheia-codex-prod/hosting/sites
2. Click on your hosting site (`aletheia-codex-prod`)
3. Click "Add custom domain"
4. Enter `aletheiacodex.app`
5. Firebase will provide specific IP addresses for A records
6. Add these A records to your DNS zone (the script can help with this)

### Step 6: Map API Domains to Cloud Run

After domain verification is complete, map the API subdomains:

```bash
# Map api.aletheiacodex.app to review-api
gcloud beta run domain-mappings create \
  --service=review-api \
  --domain=api.aletheiacodex.app \
  --region=us-central1

# Map graph.aletheiacodex.app to graph function (optional)
gcloud beta run domain-mappings create \
  --service=graph \
  --domain=graph.aletheiacodex.app \
  --region=us-central1
```

### Step 7: Update Frontend Configuration

Once domains are mapped and working, update the frontend to use custom domains:

```typescript
// web/src/services/api.ts
const API_BASE_URL = 'https://api.aletheiacodex.app';

// web/src/services/graphService.ts
const GRAPH_API_URL = 'https://graph.aletheiacodex.app';
```

Then redeploy the frontend:

```bash
cd aletheia-codex
firebase deploy --only hosting
```

## Testing the Setup

After all steps are complete, test the application:

1. **Main site**: https://aletheiacodex.app
2. **API health check**: https://api.aletheiacodex.app/health
3. **Graph API health check**: https://graph.aletheiacodex.app/health

## Timeline Estimate

- **Nameserver update**: 5 minutes (at registrar)
- **DNS propagation**: 1-48 hours (typically 2-4 hours)
- **Domain verification**: 5-10 minutes
- **DNS records setup**: 10-15 minutes
- **Domain mapping**: 5-10 minutes
- **SSL certificate**: 1-48 hours (automatic)
- **Total**: 2-96 hours (typically 4-8 hours)

## Important Notes

### Why Custom Domains Might Help

The GCP organization policy blocks public access to Cloud Functions and Cloud Run services. However, custom domains might bypass this because:

1. **Different IAM Path**: Custom domains use a different authentication path
2. **Firebase Hosting Integration**: Firebase Hosting has different IAM requirements
3. **Domain Verification**: Verified domains may have different policy treatment

### If Custom Domains Don't Work

If custom domains still encounter the organization policy restriction, you have these options:

1. **Contact GCP Organization Admin** (Fastest)
   - Request policy exception for project `aletheia-codex-prod`
   - Provide security justification (see ORGANIZATION_POLICY_ISSUE.md)
   - Time: 5-10 minutes once admin acts

2. **Implement API Gateway** (Workaround)
   - Deploy API Gateway in front of Cloud Functions
   - Time: 4-6 hours
   - Cost: ~$3-10/month

3. **Migrate to App Engine** (Alternative Platform)
   - Migrate APIs to App Engine
   - Time: 8-12 hours
   - Cost: Similar to Cloud Functions

## Documentation Reference

- **CUSTOM_DOMAIN_SETUP.md**: Detailed setup guide
- **DNS_RECORDS_REFERENCE.md**: DNS configuration reference
- **DOMAIN_SETUP_AUTOMATION.sh**: Automation script
- **ORGANIZATION_POLICY_ISSUE.md**: Policy blocker details

## Support

If you encounter issues:

1. Check DNS propagation: `dig aletheiacodex.app NS`
2. Verify domain ownership status in Google Search Console
3. Check Cloud Run domain mappings: `gcloud beta run domain-mappings list --region=us-central1`
4. Review Firebase Hosting status in Firebase Console

## Questions to Answer

Before proceeding, please confirm:

1. ✅ Do you have access to your domain registrar for `aletheiacodex.app`?
2. ⏳ Have you updated the nameservers at your registrar?
3. ⏳ Have you verified domain ownership?
4. ⏳ Are you ready to add DNS records?

Once you've completed Step 1 (updating nameservers), let me know and I can help with the remaining steps!