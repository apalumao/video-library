import { getVideos } from '@/lib/videos';
import VideoGrid from '@/components/VideoGrid';

export default function Home() {
  const videos = getVideos();

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-900 to-purple-900 p-8">
      <div className="container mx-auto">
        <header className="mb-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 drop-shadow-md">
            📹 Video Library
          </h1>
          <p className="text-indigo-200">Next.js + TypeScript HLS Player</p>
        </header>

        <VideoGrid initialVideos={videos} />
      </div>
    </main>
  );
}
