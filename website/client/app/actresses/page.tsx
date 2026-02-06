import { getDb } from '@/lib/db';
import Link from 'next/link';

interface Actress {
  id: number;
  name: string;
  videoCount: number;
}

export default function ActressesPage() {
  const db = getDb();
  
  const actresses = db.prepare(`
    SELECT a.id, a.name, COUNT(va.video_id) as videoCount
    FROM actresses a
    LEFT JOIN video_actresses va ON a.id = va.actress_id
    GROUP BY a.id
    ORDER BY videoCount DESC, a.name ASC
  `).all() as Actress[];

  return (
    <main className="min-h-screen bg-light p-8">
      <div className="container mx-auto">
        <header className="mb-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-primary mb-4">
            Actresses
          </h1>
          <p className="text-secondary">{actresses.length} actresses in library</p>
        </header>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {actresses.map((actress) => (
            <Link
              key={actress.id}
              href={`/actress/${encodeURIComponent(actress.name)}`}
              className="group"
            >
              <div className="bg-white rounded-lg p-6 shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-accent">
                <h2 className="text-lg font-bold text-primary group-hover:text-secondary transition-colors mb-2">
                  {actress.name}
                </h2>
                <p className="text-sm text-secondary">
                  {actress.videoCount} {actress.videoCount === 1 ? 'video' : 'videos'}
                </p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
