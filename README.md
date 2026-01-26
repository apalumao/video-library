# Video Library & Proxy Server

A comprehensive video streaming solution featuring a Next.js frontend library and a custom Node.js proxy server for HLS streaming.

## Project Structure

This repository is organized into a monorepo structure:

- **[website/client](website/client/)**: The user-facing video library website. Built with Next.js, TypeScript, and Tailwind CSS.
- **[website/server](website/server/)**: The backend proxy server and scraping scripts. Built with Express and Python.

## Features

-  **Rich UI**: Browse videos with metadata, cast info, and thumbnails.
-  **HLS Streaming**: Stream encrypted/protected m3u8 playlists via a custom proxy.
-  **Scraping Tools**: Python scripts to fetch video links and metadata.
-  **Next.js**: Modern, server-side rendered frontend.

## Getting Started

### Client (Frontend)

Navigate to the client directory and install dependencies:

```bash
cd website/client
npm install
npm run dev
```

### Server (Backend)

Navigate to the server directory:

```bash
cd website/server
npm install
npm start
```

## Deployment

- **Frontend**: Deploy `website/client` to Vercel or GitHub Pages.
- **Backend**: Deploy `website/server` to Render, Railway, or Heroku.

## License

MIT
