const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS for all routes
app.use(cors());

// Proxy the main m3u8 manifest and rewrite URLs
app.get('/proxy', async (req, res) => {
    // Support custom URL and referer via query parameters
    const customUrl = req.query.url;
    const customReferer = req.query.referer;
    const targetUrl = customUrl;
    const referer = customReferer || 'https://missav.ai/';

    if (!targetUrl) {
        return res.status(400).send('Missing url parameter');
    }

    console.log('Proxy request:', targetUrl);
    console.log('Using referer:', referer);

    try {
        const response = await axios.get(targetUrl, {
            headers: {
                'Referer': referer,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Origin': new URL(referer).origin,
                'Accept': '*/*'
            },
            responseType: 'text',
            timeout: 30000
        });

        // Rewrite the m3u8 content to use our proxy for all segments
        let content = response.data;
        const baseUrl = targetUrl.substring(0, targetUrl.lastIndexOf('/'));
        
        // Detect the actual protocol (handle reverse proxy)
        const protocol = req.get('x-forwarded-proto') || req.protocol;
        
        // Replace segment URLs to go through our proxy
        content = content.replace(/^((?!#).+)$/gm, (match) => {
            if (match.trim() === '') return match;
            
            // Build full segment URL
            let segmentUrl;
            if (match.startsWith('http://') || match.startsWith('https://')) {
                segmentUrl = match;
            } else {
                segmentUrl = `${baseUrl}/${match}`;
            }
            
            // Return proxy URL with encoded segment URL and referer
            return `${protocol}://${req.get('host')}/segment?url=${encodeURIComponent(segmentUrl)}&referer=${encodeURIComponent(referer)}`;
        });
        
        res.setHeader('Content-Type', 'application/vnd.apple.mpegurl');
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.send(content);
    } catch (error) {
        console.error('Proxy error:', error.message);
        res.status(500).send('Proxy failed to fetch video: ' + error.message);
    }
});

// Proxy video segments
app.get('/segment', async (req, res) => {
    const segmentUrl = req.query.url;
    const referer = req.query.referer || 'https://missav.ai/';

    if (!segmentUrl) {
        return res.status(400).send('Missing url parameter');
    }

    console.log('Segment request:', segmentUrl);

    try {
        const response = await axios.get(segmentUrl, {
            headers: {
                'Referer': referer,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Origin': new URL(referer).origin,
                'Accept': '*/*'
            },
            responseType: 'arraybuffer',
            timeout: 30000
        });

        res.setHeader('Content-Type', response.headers['content-type'] || 'video/MP2T');
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.send(response.data);
    } catch (error) {
        console.error('Segment error:', error.message);
        res.status(500).send('Failed to fetch segment: ' + error.message);
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
    console.log(`Proxy server running on port ${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/health`);
});
