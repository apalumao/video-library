let allVideos = [];
let hls = null;

// Proxy server URL - change this to your deployed proxy URL
const PROXY_URL = 'http://localhost:3000';

// Load videos from JSON
async function loadVideos() {
    try {
        const response = await fetch('videos.json');
        allVideos = await response.json();
        displayVideos(allVideos);
        document.getElementById('totalCount').textContent = allVideos.length;
    } catch (error) {
        console.error('Error loading videos:', error);
        document.getElementById('videoGrid').innerHTML = '<p>Error loading videos</p>';
    }
}

// Display videos in grid
function displayVideos(videos) {
    const grid = document.getElementById('videoGrid');
    
    if (videos.length === 0) {
        grid.innerHTML = '<p class="no-results">No videos found</p>';
        return;
    }

    grid.innerHTML = videos.map(video => `
        <div class="video-card" onclick="playVideo('${video.m3u8Url}', '${video.code}', '${video.quality}', '${video.videoUrl}')">
            <div class="video-thumbnail">
                <div class="play-icon">▶</div>
            </div>
            <div class="video-info">
                <h3>${video.code}</h3>
                <span class="quality-badge">${video.quality || 'HD'}</span>
            </div>
        </div>
    `).join('');
}

// Play video using proxy
function playVideo(m3u8Url, code, quality, videoUrl) {
    const video = document.getElementById('videoPlayer');
    const playerSection = document.getElementById('playerSection');
    
    // Update player info
    document.getElementById('currentVideoTitle').textContent = code + ' - Loading...';
    document.getElementById('currentVideoQuality').textContent = `Quality: ${quality || 'HD'}`;
    document.getElementById('currentVideoLink').href = videoUrl;
    
    // Show player section
    playerSection.style.display = 'block';
    playerSection.scrollIntoView({ behavior: 'smooth' });

    // Clean up previous HLS instance
    if (hls) {
        hls.destroy();
    }

    // Use the proxy endpoint with referer
    let proxyUrl = PROXY_URL + '/proxy?url=' + encodeURIComponent(m3u8Url);
    if (videoUrl) {
        proxyUrl += '&referer=' + encodeURIComponent(videoUrl);
    }

    // Load m3u8 stream
    if (Hls.isSupported()) {
        hls = new Hls({
            debug: false,
            enableWorker: true,
            lowLatencyMode: true
        });
        
        hls.loadSource(proxyUrl);
        hls.attachMedia(video);
        
        hls.on(Hls.Events.MANIFEST_PARSED, function() {
            document.getElementById('currentVideoTitle').textContent = code;
            video.play().catch(e => {
                console.log('Auto-play prevented, user interaction required');
            });
        });
        
        hls.on(Hls.Events.ERROR, function(event, data) {
            console.error('HLS error:', data);
            if (data.fatal) {
                switch(data.type) {
                    case Hls.ErrorTypes.NETWORK_ERROR:
                        document.getElementById('currentVideoTitle').textContent = code + ' - Network Error';
                        alert('Network error loading video. Please try again later.');
                        break;
                    case Hls.ErrorTypes.MEDIA_ERROR:
                        document.getElementById('currentVideoTitle').textContent = code + ' - Recovering...';
                        hls.recoverMediaError();
                        break;
                    default:
                        document.getElementById('currentVideoTitle').textContent = code + ' - Error';
                        alert('Error loading video: ' + data.details);
                        break;
                }
            }
        });
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        // Native HLS support (Safari)
        video.src = proxyUrl;
        video.addEventListener('loadedmetadata', function() {
            document.getElementById('currentVideoTitle').textContent = code;
            video.play().catch(e => {
                console.log('Auto-play prevented, user interaction required');
            });
        });
        video.addEventListener('error', function() {
            document.getElementById('currentVideoTitle').textContent = code + ' - Error';
            alert('Error loading video. Please try again later.');
        });
    } else {
        alert('Your browser does not support HLS playback.');
    }
}

// Close player
function closePlayer() {
    const video = document.getElementById('videoPlayer');
    const playerSection = document.getElementById('playerSection');
    
    video.pause();
    if (hls) {
        hls.destroy();
        hls = null;
    }
    playerSection.style.display = 'none';
}

// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('searchInput').addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const filtered = allVideos.filter(video => 
            video.code.toLowerCase().includes(searchTerm)
        );
        displayVideos(filtered);
    });

    // Load videos on page load
    loadVideos();
});
