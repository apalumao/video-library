import Link from 'next/link';
import { Video } from '@/lib/types';
import { Play } from 'lucide-react';

interface VideoCardProps {
  video: Video;
}

export default function VideoCard({ video }: VideoCardProps) {
  return (
    <Link href={`/${video.code}`} className="group">
      <div className="bg-white rounded-xl overflow-hidden shadow-md hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1">
        <div className="h-40 bg-gray-200 relative overflow-hidden">
          {video.thumbnailUrl ? (
            <img 
              src={video.thumbnailUrl} 
              alt={video.code}
              className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-500"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <span className="text-white text-2xl">▶</span>
            </div>
          )}
          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
             <div className="w-12 h-12 bg-white/30 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 backdrop-blur-sm transition-opacity">
                <span className="text-white text-xl">▶</span>
             </div>
          </div>
        </div>
        <div className="p-4">
          <h3 className="font-bold text-gray-800 text-lg group-hover:text-indigo-600 transition-colors uppercase truncate">
            {video.code}
          </h3>
          {video.title && (
            <p className="text-xs text-gray-500 mt-1 line-clamp-2" title={video.title}>
              {video.title}
            </p>
          )}
          <span className="inline-block px-2 py-1 mt-2 text-xs font-semibold text-white bg-indigo-500 rounded-md">
            {video.quality || 'HD'}
          </span>
        </div>
      </div>
    </Link>
  );
}
