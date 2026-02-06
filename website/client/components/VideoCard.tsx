import Link from 'next/link';
import { Video } from '@/lib/types';
import { Play } from 'lucide-react';

interface VideoCardProps {
  video: Video;
}

export default function VideoCard({ video }: VideoCardProps) {
  return (
    <Link href={`/${video.code}`} className="group block">
      <div className="overflow-hidden rounded-lg transition-all duration-300">
        {/* Thumbnail */}
        <div className="relative aspect-video bg-light overflow-hidden rounded-lg">
          {video.thumbnailUrl ? (
            <img 
              src={video.thumbnailUrl} 
              alt={video.code}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-secondary to-accent flex items-center justify-center">
              <span className="text-white text-2xl">▶</span>
            </div>
          )}
        </div>
        
        {/* Title */}
        <div className="mt-2">
          <h3 className="text-sm text-white line-clamp-2 leading-tight">
            {video.title || video.code}
          </h3>
        </div>
      </div>
    </Link>
  );
}
