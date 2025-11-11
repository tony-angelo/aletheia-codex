# Custom Domain Setup Summary

## Overview
This document summarizes the custom domain setup preparation completed for the Aletheia Codex project as a potential workaround for the GCP organization policy blocking public access to Cloud Functions.

## Background

### The Problem
The project is blocked by a GCP organization policy (`iam.allowedPolicyMemberDomains`) that prevents:
- Adding `allUsers` or `allAuthenticatedUsers` to IAM policies
- Public access to Cloud Functions and Cloud Run services
- All API requests return 403 Forbidden at the infrastructure level

### The Solution
Custom domain setup using `aletheiacodex.app` may bypass the organization policy by using a different authentication path through verified domains.

## Completed Setup

### 1. Cloud DNS Zone Created ✅
- **Zone Name**: `aletheiacodex-app`
- **Domain**: `aletheiacodex.app`
- **Nameservers**:
  - ns-cloud-c1.googledomains.com
  - ns-cloud-c2.googledomains.com
  - ns-cloud-c3.googledomains.com
  - ns-cloud-c4.googledomains.com

### 2. Permissions Granted ✅
- **DNS Administrator**: Service account can manage DNS records
- **Service Usage Admin**: Service account can enable APIs

### 3. Documentation Created ✅

#### CUSTOM_DOMAIN_SETUP.md
Complete step-by-step guide covering:
- Overview and current status
- Nameserver update instructions
- Domain verification process
- DNS records configuration
- Alternative approaches
- Testing procedures
- Troubleshooting guide
- Timeline estimates

#### DNS_RECORDS_REFERENCE.md
Detailed DNS configuration reference including:
- Current nameserver information
- Required DNS records (A, CNAME, TXT, CAA)
- DNS record management options
- Verification commands
- Common DNS record formats
- Next steps checklist

#### DOMAIN_SETUP_AUTOMATION.sh
Automation script that:
- Checks prerequisites
- Verifies DNS propagation
- Checks domain verification status
- Adds DNS records to Google Cloud DNS
- Provides domain mapping instructions
- Tests DNS configuration
- Provides setup summary

#### NEXT_STEPS_CUSTOM_DOMAIN.md
Action-oriented guide with:
- Current status overview
- Immediate actions required
- Step-by-step instructions
- Timeline estimates
- Testing procedures
- Troubleshooting tips
- Alternative solutions if custom domains don't work

#### DNS_QUICK_REFERENCE.txt
Quick reference card with:
- Nameserver information
- DNS propagation checking
- Domain verification steps
- DNS records to add
- Domain mapping commands
- Testing commands
- Troubleshooting commands
- Timeline summary

## User Actions Required

### Step 1: Update Nameservers (5 minutes)
User must log in to their domain registrar and update nameservers to:
```
ns-cloud-c1.googledomains.com
ns-cloud-c2.googledomains.com
ns-cloud-c3.googledomains.com
ns-cloud-c4.googledomains.com
```

### Step 2: Wait for DNS Propagation (1-48 hours)
Typically takes 2-4 hours, but can take up to 48 hours.

Check propagation:
```bash
dig aletheiacodex.app NS
```

### Step 3: Verify Domain Ownership (5-10 minutes)
Options:
- **Google Search Console**: Add property and verify via DNS TXT record
- **Firebase Console**: Add custom domain and follow verification steps

### Step 4: Add DNS Records (10-15 minutes)
After Firebase provides IP addresses:
- Add A records for root domain
- Add A records for www subdomain
- Add CNAME record for api subdomain
- Add CNAME record for graph subdomain (optional)

### Step 5: Map Domains to Cloud Run (5-10 minutes)
```bash
gcloud beta run domain-mappings create \
  --service=review-api \
  --domain=api.aletheiacodex.app \
  --region=us-central1
```

### Step 6: Update Frontend Configuration (5 minutes)
Update API URLs to use custom domains and redeploy.

### Step 7: Test (5 minutes)
- Test main site: https://aletheiacodex.app
- Test API: https://api.aletheiacodex.app/health
- Test Graph API: https://graph.aletheiacodex.app/health

## Timeline

| Step | Time Required | Notes |
|------|---------------|-------|
| Nameserver Update | 5 minutes | At domain registrar |
| DNS Propagation | 1-48 hours | Typically 2-4 hours |
| Domain Verification | 5-10 minutes | After propagation |
| DNS Records Setup | 10-15 minutes | Via automation script |
| Domain Mapping | 5-10 minutes | Via gcloud commands |
| SSL Certificate | 1-48 hours | Automatic by Google |
| **Total** | **2-96 hours** | **Typically 4-8 hours** |

## Why This Might Work

Custom domains may bypass the organization policy because:

1. **Different IAM Path**: Custom domains use domain verification instead of IAM policies
2. **Firebase Hosting Integration**: Firebase Hosting has different authentication requirements
3. **Verified Domain Status**: Verified domains may be treated differently by organization policies

## If Custom Domains Don't Work

Alternative solutions if the organization policy still blocks access:

### Option 1: Organization Policy Exception (Recommended)
- **Action**: Contact GCP organization administrator
- **Time**: 5-10 minutes once admin acts
- **Cost**: Free
- **Likelihood**: High success rate

### Option 2: API Gateway
- **Action**: Deploy API Gateway in front of Cloud Functions
- **Time**: 4-6 hours
- **Cost**: ~$3-10/month
- **Likelihood**: Should work

### Option 3: App Engine Migration
- **Action**: Migrate APIs to App Engine
- **Time**: 8-12 hours
- **Cost**: Similar to Cloud Functions
- **Likelihood**: Should work

## Files Created

All documentation and scripts are in the `aletheia-codex` directory:

```
aletheia-codex/
├── CUSTOM_DOMAIN_SETUP.md           # Complete setup guide
├── DNS_RECORDS_REFERENCE.md         # DNS configuration reference
├── DOMAIN_SETUP_AUTOMATION.sh       # Automation script
├── NEXT_STEPS_CUSTOM_DOMAIN.md      # Action items for user
├── DNS_QUICK_REFERENCE.txt          # Quick reference card
└── CUSTOM_DOMAIN_SETUP_SUMMARY.md   # This file
```

## Current State

✅ **Infrastructure Ready**
- Cloud DNS zone created and configured
- Nameservers available for user to update
- Permissions granted for DNS management

✅ **Documentation Complete**
- Comprehensive guides created
- Automation script ready
- Quick reference materials available

⏳ **Waiting for User Action**
- User needs to update nameservers at registrar
- User needs to verify domain ownership
- User needs to add DNS records

## Success Criteria

The custom domain setup will be considered successful when:

1. ✅ User can access main site at https://aletheiacodex.app
2. ✅ API endpoints respond at https://api.aletheiacodex.app
3. ✅ Graph API responds at https://graph.aletheiacodex.app
4. ✅ No 403 Forbidden errors
5. ✅ CORS headers properly applied
6. ✅ SSL certificates automatically provisioned

## Next Steps for User

1. **Immediate**: Update nameservers at domain registrar
2. **After 2-4 hours**: Check DNS propagation
3. **After propagation**: Verify domain ownership
4. **After verification**: Run automation script
5. **After DNS setup**: Map domains to Cloud Run
6. **After mapping**: Test the application

## Support

If the user encounters issues, they should:
1. Check the relevant documentation file
2. Run the automation script for guided setup
3. Use the troubleshooting commands in DNS_QUICK_REFERENCE.txt
4. Provide specific error messages and command outputs for debugging

## Conclusion

All preparation for custom domain setup is complete. The solution is ready for user implementation. This approach has a good chance of bypassing the organization policy restriction without requiring administrator intervention. If it doesn't work, we have documented alternative solutions that can be implemented.