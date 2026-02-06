import { getVideos } from '@/lib/videos';
import VideoGrid from '@/components/VideoGrid';

export default function Home() {
  const videos = getVideos();

  return (
    <main className="min-h-screen bg-light p-8">
      <div className="container mx-auto">
        <header className="mb-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-heading mb-4 drop-shadow-sm">
            Recent Updates
          </h1>
          <p className="text-secondary">Discover the latest videos</p>
        </header>

        <VideoGrid initialVideos={videos} />
      </div>
    </main>
  );
}
