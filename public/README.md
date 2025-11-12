# Public Directory

## Overview
This directory contains static assets and the entry point HTML file for the Aletheia Codex web application. These files are served by Firebase Hosting and provide the foundation for the React single-page application.

## Purpose
- Serve static HTML entry point
- Host favicon and app icons
- Provide manifest for Progressive Web App (PWA)
- Configure Firebase Hosting behavior

## Directory Structure
```
public/
├── README.md                          # This file
├── index.html                         # Main HTML entry point
├── favicon.ico                        # Browser favicon
├── manifest.json                      # PWA manifest
├── robots.txt                         # Search engine directives
└── assets/                            # Static assets (if any)
```

## Key Files

### index.html
The main HTML template that serves as the entry point for the React application.

**Structure**:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Aletheia Codex</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

### manifest.json
Progressive Web App configuration for installability.

## Firebase Hosting Integration

### Deployment
```bash
# Build React app
cd web
npm run build

# Deploy to Firebase Hosting
firebase deploy --only hosting
```

### Custom Domain
- **Production**: https://aletheiacodex.app
- **Firebase URL**: https://aletheia-codex-prod.web.app

## Progressive Web App (PWA) Features

### Installability
- Add to home screen on mobile
- Install as desktop app
- Offline capability (with service worker)

## SEO Optimization

### Meta Tags
```html
<meta name="description" content="Personal knowledge graph application" />
<meta property="og:title" content="Aletheia Codex" />
```

## Performance Optimization

### Caching Strategy
Firebase Hosting automatically provides:
- CDN distribution
- Automatic SSL
- HTTP/2 support
- Gzip compression

## Related Documentation
- [Web Application README](../web/README.md)
- [Firebase Hosting Docs](https://firebase.google.com/docs/hosting)
