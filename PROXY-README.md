# Video Proxy Server

A CORS proxy server for m3u8 video streaming with referer header support.

## Features
- Proxies m3u8 manifests and video segments
- Adds proper referer headers to bypass restrictions
- CORS enabled for cross-origin requests
- URL rewriting for seamless playback

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the server:
```bash
npm start
```

For development with auto-reload:
```bash
npm run dev
```

## API Endpoints

### GET /proxy
Proxies m3u8 manifest files.

**Parameters:**
- `url` (required) - The m3u8 URL to proxy
- `referer` (optional) - Custom referer header (defaults to missav.ai)

**Example:**
```
http://localhost:3000/proxy?url=https://example.com/video.m3u8&referer=https://example.com
```

### GET /segment
Proxies video segments (.ts files).

**Parameters:**
- `url` (required) - The segment URL to proxy
- `referer` (optional) - Custom referer header

### GET /health
Health check endpoint.

## Deployment

### Railway
1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Railway will auto-detect and deploy

### Render
1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Set build command: `npm install`
4. Set start command: `npm start`

### Vercel (Serverless)
This requires converting to serverless functions. Contact for serverless version.

## Environment Variables
- `PORT` - Server port (default: 3000)

## Usage with Frontend

Update your frontend code to use the proxy:
```javascript
const proxyUrl = 'https://your-proxy-server.com/proxy?url=' + 
                 encodeURIComponent(m3u8Url) + 
                 '&referer=' + encodeURIComponent(videoUrl);
```
