import { getVideoByCode } from '@/lib/videos';
import HlsPlayer from '@/components/HlsPlayer';
import Link from 'next/link';

interface PageProps {
  params: Promise<{ code: string }>;
}

export default async function VideoPage({ params }: PageProps) {
  const { code } = await params;
  const video = getVideoByCode(code);

  if (!video) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">Video Not Found</h1>
          <Link href="/" className="text-indigo-400 hover:text-indigo-300 underline">
            Return Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="container mx-auto">
        <Link 
          href="/" 
          className="inline-flex items-center text-indigo-400 hover:text-indigo-300 mb-6 transition-colors"
        >
          ← Back to Library
        </Link>
        
        <div className="bg-gray-800 rounded-xl p-6 shadow-xl">
          <h1 className="text-2xl md:text-3xl font-bold mb-2 text-white">{video.title || video.code}</h1>
          <div className="flex flex-wrap items-center gap-4 mb-6 text-sm text-gray-300">
             <span className="font-mono text-indigo-400 text-lg">{video.code}</span>
             <span className="bg-gray-700 px-2 py-1 rounded">{video.quality || 'HD'}</span>
             {video.releaseDate && <span>📅 {video.releaseDate}</span>}
             {video.maker && <span>🏢 {video.maker}</span>}
             <a 
              href={video.videoUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white hover:underline ml-auto"
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
                
                {video.genre && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-500 mb-2 uppercase tracking-wider">Genres</h3>
                    <div className="flex flex-wrap gap-2">
                      {video.genre.split(',').map(g => (
                        <span key={g} className="bg-gray-700 px-3 py-1 rounded-full text-sm hover:bg-indigo-600 transition-colors cursor-pointer">
                          {g.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
             </div>

             <div className="space-y-4 bg-gray-900/50 p-6 rounded-lg">
                <h3 className="text-lg font-semibold border-b border-gray-700 pb-2">Details</h3>
                <dl className="space-y-3 text-sm">
                  {video.actress && (
                    <div className="grid grid-cols-3 gap-2">
                       <dt className="text-gray-500">Cast</dt>
                       <dd className="col-span-2 text-indigo-300 font-medium">{video.actress}</dd>
                    </div>
                  )}
                  {video.director && (
                    <div className="grid grid-cols-3 gap-2">
                       <dt className="text-gray-500">Director</dt>
                       <dd className="col-span-2">{video.director}</dd>
                    </div>
                  )}
                  {video.label && (
                    <div className="grid grid-cols-3 gap-2">
                       <dt className="text-gray-500">Label</dt>
                       <dd className="col-span-2">{video.label}</dd>
                    </div>
                  )}
                  {video.maker && (
                    <div className="grid grid-cols-3 gap-2">
                       <dt className="text-gray-500">Maker</dt>
                       <dd className="col-span-2">{video.maker}</dd>
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
