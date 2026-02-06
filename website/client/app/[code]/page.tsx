import { getVideos, getVideoByCode } from '@/lib/videos';
import HlsPlayer from '@/components/HlsPlayer';
import Link from 'next/link';

// Required for static export
export async function generateStaticParams() {
  const videos = getVideos();
  return videos.map((video) => ({
    code: video.code,
  }));
}

interface PageProps {
  params: Promise<{ code: string }>;
}

export default async function VideoPage({ params }: PageProps) {
  const { code } = await params;
  const video = getVideoByCode(code);

  if (!video) {
    return (
      <div className="min-h-screen bg-primary text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">Video Not Found</h1>
          <Link href="/" className="text-accent hover:text-white underline">
            Return Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-primary text-white p-6">
      <div className="container mx-auto">
        <Link 
          href="/" 
          className="inline-flex items-center text-accent hover:text-white mb-6 transition-colors font-medium"
        >
          ← Back to Library
        </Link>
        
        <div className="bg-secondary rounded-xl p-6 shadow-xl">
          <h1 className="text-2xl md:text-3xl font-bold mb-2 text-white">{video.title || video.code}</h1>
          <div className="flex flex-wrap items-center gap-4 mb-6 text-sm text-gray-300">
             <span className="font-mono text-white text-lg font-bold">{video.code}</span>
             <span className="bg-accent text-primary px-2 py-1 rounded font-medium">{video.quality || 'HD'}</span>
             {video.releaseDate && <span>📅 {video.releaseDate}</span>}
             {video.makers && video.makers.length > 0 && <span>🏢 {video.makers[0]}</span>}
             <a 
              href={video.videoUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-accent hover:text-white hover:underline ml-auto"
            >
              Open Source
            </a>
          </div>

          <HlsPlayer src={video.m3u8Url} referer={video.videoUrl} />
          
          <div className="mt-8 border-t border-gray-700 pt-6 grid grid-cols-1 md:grid-cols-3 gap-8">
             <div className="md:col-span-2 space-y-4">
                <h2 className="text-xl font-semibold text-white">Description</h2>
                <p className="text-gray-300 leading-relaxed whitespace-pre-line">
                  {video.description || 'No description available.'}
                </p>
                
                {video.genres && video.genres.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-400 mb-2 uppercase tracking-wider">Genres</h3>
                    <div className="flex flex-wrap gap-2">
                      {video.genres.map(g => (
                        <span key={g} className="bg-light text-primary px-3 py-1 rounded-full text-sm hover:bg-accent hover:text-primary transition-colors cursor-pointer">
                          {g}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
             </div>

             <div className="space-y-4 bg-primary/50 p-6 rounded-lg border border-gray-700">
                <h3 className="text-lg font-semibold border-b border-gray-700 pb-2 text-white">Details</h3>
                <dl className="space-y-3 text-sm">
                  {video.actresses && video.actresses.length > 0 && (
                    <div className="grid grid-cols-3 gap-2">
                       <dt className="text-gray-400">Cast</dt>
                       <dd className="col-span-2 text-white font-medium">{video.actresses.join(', ')}</dd>
                    </div>
                  )}
                  {video.director && (
                    <div className="grid grid-cols-3 gap-2">
                       <dt className="text-gray-400">Director</dt>
                       <dd className="col-span-2 text-white">{video.director}</dd>
                    </div>
                  )}
                  {video.label && (
                    <div className="grid grid-cols-3 gap-2">
                       <dt className="text-gray-400">Label</dt>
                       <dd className="col-span-2 text-white">{video.label}</dd>
                    </div>
                  )}
                  {video.makers && video.makers.length > 0 && (
                    <div className="grid grid-cols-3 gap-2">
                       <dt className="text-gray-400">Maker</dt>
                       <dd className="col-span-2 text-white">{video.makers.join(', ')}</dd>
                    </div>
                  )}
                </dl>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
