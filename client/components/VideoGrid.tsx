'use client';

import { useState } from 'react';
import { Video } from '@/lib/types';
import VideoCard from './VideoCard';

interface VideoGridProps {
  initialVideos: Video[];
}

export default function VideoGrid({ initialVideos }: VideoGridProps) {
  const [searchTerm, setSearchTerm] = useState('');
  
  const filteredVideos = initialVideos.filter((video) =>
    video.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <div className="flex justify-between items-center mb-8 flex-wrap gap-4">
        <div className="bg-white/10 px-4 py-2 rounded-lg backdrop-blur-md">
            <span className="text-white font-medium">Total: {initialVideos.length} videos</span>
        </div>
        <input
          type="text"
          placeholder="Search videos..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="px-4 py-2 rounded-full bg-white/90 focus:bg-white text-gray-800 placeholder-gray-500 outline-none w-full max-w-md shadow-lg transition-all"
        />
      </div>

      {filteredVideos.length === 0 ? (
        <div className="text-center text-white py-20 text-xl">
          No videos found matching "{searchTerm}"
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          {filteredVideos.map((video) => (
            <VideoCard key={video.code} video={video} />
          ))}
        </div>
      )}
    </div>
  );
}
