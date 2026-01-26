'use client';

import { useEffect, useRef, useState } from 'react';
import Hls from 'hls.js';

interface HlsPlayerProps {
  src: string;
  referer?: string;
}

// You can move this to an environment variable later
const PROXY_URL = 'https://video-proxy-server-lddl.onrender.com';

export default function HlsPlayer({ src, referer }: HlsPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('Loading...');

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    // Construct Proxy URL
    let proxyUrl = `${PROXY_URL}/proxy?url=${encodeURIComponent(src)}`;
    if (referer) {
      proxyUrl += `&referer=${encodeURIComponent(referer)}`;
    }

    let hls: Hls | null = null;

    if (Hls.isSupported()) {
      hls = new Hls({
        debug: false,
        enableWorker: true,
        lowLatencyMode: true,
      });

      hls.loadSource(proxyUrl);
      hls.attachMedia(video);

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        setStatus('Ready');
        video.play().catch(() => {
          console.log('Auto-play prevented');
        });
      });

      hls.on(Hls.Events.ERROR, (event, data) => {
        console.error('HLS error:', data);
        if (data.fatal) {
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              setError('Network error. Please check your connection.');
              hls?.startLoad();
              break;
            case Hls.ErrorTypes.MEDIA_ERROR:
              console.log('Media error, trying to recover...');
              hls?.recoverMediaError();
              break;
            default:
              setError('Fatal error: ' + data.details);
              hls?.destroy();
              break;
          }
        }
      });
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      // Native HLS (Safari)
      video.src = proxyUrl;
      video.addEventListener('loadedmetadata', () => {
        setStatus('Ready');
        video.play().catch(() => {});
      });
      video.addEventListener('error', () => {
        setError('Error loading video natively.');
      });
    } else {
      setError('HLS is not supported in this browser.');
    }

    return () => {
      if (hls) {
        hls.destroy();
      }
    };
  }, [src, referer]);

  return (
    <div className="w-full max-w-4xl mx-auto bg-black rounded-xl overflow-hidden shadow-2xl relative aspect-video">
      {status !== 'Ready' && !error && (
        <div className="absolute inset-0 flex items-center justify-center text-white z-10 bg-black/50">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
        </div>
      )}
      
      {error && (
        <div className="absolute inset-0 flex items-center justify-center text-white z-10 bg-red-900/80 p-4 text-center">
          <p>{error}</p>
        </div>
      )}

      <video
        ref={videoRef}
        controls
        className="w-full h-full object-contain"
        playsInline
      />
    </div>
  );
}
