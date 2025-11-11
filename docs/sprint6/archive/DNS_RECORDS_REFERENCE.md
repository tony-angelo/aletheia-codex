# DNS Records Reference for aletheiacodex.app

## Current Google Cloud DNS Nameservers

These nameservers are already configured in your Google Cloud DNS zone and should be set at your domain registrar:

```
ns-cloud-c1.googledomains.com
ns-cloud-c2.googledomains.com
ns-cloud-c3.googledomains.com
ns-cloud-c4.googledomains.com
```

## DNS Records to Add (After Domain Verification)

### 1. Firebase Hosting Records (Main Website)

Firebase will provide specific IP addresses when you add the custom domain. Typical records look like:

```
Type: A
Name: @
Value: 151.101.1.195
TTL: 3600

Type: A
Name: @
Value: 151.101.65.195
TTL: 3600

Type: A
Name: www
Value: 151.101.1.195
TTL: 3600

Type: A
Name: www
Value: 151.101.65.195
TTL: 3600
```

**Note**: The actual IP addresses will be provided by Firebase when you add the custom domain in the Firebase Console.

### 2. API Subdomain (Cloud Run/Cloud Functions)

For the API subdomain, we'll use a CNAME record:

```
Type: CNAME
Name: api
Value: ghs.googlehosted.com.
TTL: 3600
```

**Alternative**: If using direct Cloud Run domain mapping, the value might be different (Cloud Run will provide the specific CNAME target).

### 3. Graph API Subdomain (Optional - if using separate subdomain)

```
Type: CNAME
Name: graph
Value: ghs.googlehosted.com.
TTL: 3600
```

### 4. Domain Verification TXT Record

Google will provide a TXT record for domain verification. It will look something like:

```
Type: TXT
Name: @
Value: google-site-verification=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TTL: 3600
```

**Note**: The actual verification code will be provided during the verification process.

### 5. SSL Certificate Verification (CAA Records - Optional)

These are optional but recommended for security:

```
Type: CAA
Name: @
Value: 0 issue "letsencrypt.org"
TTL: 3600

Type: CAA
Name: @
Value: 0 issue "pki.goog"
TTL: 3600
```

## DNS Record Management Options

### Option 1: Manage via Google Cloud DNS (Recommended)

Since your nameservers are pointed to Google Cloud DNS, you can manage all records via the Google Cloud Console or gcloud CLI:

```bash
# Add an A record
gcloud dns record-sets create aletheiacodex.app. \
  --zone=aletheiacodex-app \
  --type=A \
  --ttl=3600 \
  --rrdatas=151.101.1.195,151.101.65.195

# Add a CNAME record
gcloud dns record-sets create api.aletheiacodex.app. \
  --zone=aletheiacodex-app \
  --type=CNAME \
  --ttl=3600 \
  --rrdatas=ghs.googlehosted.com.

# Add a TXT record for verification
gcloud dns record-sets create aletheiacodex.app. \
  --zone=aletheiacodex-app \
  --type=TXT \
  --ttl=3600 \
  --rrdatas="google-site-verification=YOUR_VERIFICATION_CODE"
```

### Option 2: Manage via Registrar

If you prefer to manage DNS at your registrar instead of Google Cloud DNS, you can:
1. Keep your existing nameservers at the registrar
2. Add the DNS records directly in your registrar's DNS management interface
3. Skip the Google Cloud DNS zone entirely

**Note**: If using this option, you won't need to update nameservers to Google Cloud DNS.

## Verification Commands

After adding DNS records, verify they're working:

```bash
# Check A records
dig aletheiacodex.app A

# Check CNAME records
dig api.aletheiacodex.app CNAME

# Check TXT records
dig aletheiacodex.app TXT

# Check nameservers
dig aletheiacodex.app NS
```

## DNS Propagation Checking

Use these online tools to check DNS propagation globally:
- https://www.whatsmydns.net/
- https://dnschecker.org/
- https://www.dnswatch.info/

## Common DNS Record Formats

### For Registrar DNS Management
Most registrars use a similar format:

| Type  | Name/Host | Value/Points To              | TTL  |
|-------|-----------|------------------------------|------|
| A     | @         | 151.101.1.195                | 3600 |
| A     | @         | 151.101.65.195               | 3600 |
| A     | www       | 151.101.1.195                | 3600 |
| CNAME | api       | ghs.googlehosted.com         | 3600 |
| TXT   | @         | google-site-verification=... | 3600 |

**Notes**:
- `@` represents the root domain (aletheiacodex.app)
- `www` represents www.aletheiacodex.app
- `api` represents api.aletheiacodex.app
- TTL is in seconds (3600 = 1 hour)
- Some registrars require a trailing dot (.) for CNAME values

## Next Steps

1. **First**: Update nameservers at your registrar (if using Google Cloud DNS)
2. **Wait**: 1-48 hours for DNS propagation
3. **Verify**: Use dig commands to confirm nameserver changes
4. **Add Domain**: In Firebase Console, add custom domain
5. **Get Records**: Firebase will provide specific A record IP addresses
6. **Add Records**: Add the A records and CNAME records
7. **Wait**: For SSL certificate provisioning (automatic)
8. **Test**: Access your site via the custom domain

## Support

If you need help with any of these steps, please provide:
- Your domain registrar name
- Current DNS configuration (screenshot or text)
- Any error messages you're seeing
- Output of `dig aletheiacodex.app NS` command