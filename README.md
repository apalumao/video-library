# Video Proxy Server

A CORS proxy server for streaming m3u8 video content with referer header support.

## Features

- Proxies m3u8 manifest files and video segments
- Adds referer headers to bypass source restrictions
- CORS enabled for cross-origin requests
- Rewrites manifest URLs to route through proxy

## Deployment

This server is designed to be deployed on platforms like Render, Railway, or Vercel.

### Environment Variables

- `PORT` - Server port (default: 3000)

### Endpoints

- `GET /proxy?url=<m3u8_url>&referer=<referer_url>` - Proxy m3u8 manifest
- `GET /segment?url=<segment_url>&referer=<referer_url>` - Proxy video segments
- `GET /` - Health check

## Usage

```bash
npm install
npm start
```

## License

MIT
