# Self-Hosted Fonts Directory

This directory contains locally hosted font files to eliminate external dependencies during Playwright rendering.

## Fonts Used

### Poppins (Primary UI Font)
- Weights: 300, 400, 500, 600, 700, 800
- Format: WOFF2 (primary), WOFF (fallback)
- Usage: Main UI elements, headers, body text

### Inter (Numeric Font)
- Weights: 300, 400, 500, 600, 700, 800
- Format: WOFF2 (primary), WOFF (fallback)
- Usage: Numbers, data display, metrics

### Orbitron (Brand Font)
- Weights: 400, 500, 700
- Format: WOFF2 (primary), WOFF (fallback)
- Usage: Brand elements, special headers

## Implementation

### Before (External Dependency)
```html
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Orbitron:wght@400;500;700&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
```

### After (Self-Hosted)
```html
<link rel="stylesheet" href="fonts/fonts.css">
```

## Benefits

✅ **Offline Rendering**: Playwright works without internet connection
✅ **Performance**: No external DNS lookups or network requests
✅ **Reliability**: No dependency on Google Fonts CDN availability
✅ **Privacy**: No external requests to Google servers
✅ **Production Ready**: Eliminates single point of failure

## Font Files Required

To complete implementation, download these font files:

### Poppins
- poppins-300.woff2, poppins-300.woff
- poppins-400.woff2, poppins-400.woff
- poppins-500.woff2, poppins-500.woff
- poppins-600.woff2, poppins-600.woff
- poppins-700.woff2, poppins-700.woff
- poppins-800.woff2, poppins-800.woff

### Inter
- inter-300.woff2, inter-300.woff
- inter-400.woff2, inter-400.woff
- inter-500.woff2, inter-500.woff
- inter-600.woff2, inter-600.woff
- inter-700.woff2, inter-700.woff
- inter-800.woff2, inter-800.woff

### Orbitron
- orbitron-400.woff2, orbitron-400.woff
- orbitron-500.woff2, orbitron-500.woff
- orbitron-700.woff2, orbitron-700.woff

## Download Sources

Use Google Fonts Helper or similar tools to download WOFF2/WOFF files:
- https://gwfh.mranftl.com/fonts
- Extract Latin character sets only for optimal file size