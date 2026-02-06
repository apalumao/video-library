import { getDb } from './db';
import { Video } from './types';

interface VideoRow {
  id: number;
  video_code: string;
  video_url: string;
  m3u8_url: string;
  quality: string;
  title: string;
  release_date: string;
  director: string;
  label: string;
  description: string;
  thumbnail_url: string;
}

interface CategoryRow {
  name: string;
}

function buildVideoWithCategories(videoRow: VideoRow): Video {
  const db = getDb();
  
  // Get actresses for this video
  const actresses = db.prepare(`
    SELECT a.name 
    FROM video_actresses va
    JOIN actresses a ON va.actress_id = a.id
    WHERE va.video_id = ?
  `).all(videoRow.id) as CategoryRow[];
  
  // Get genres for this video
  const genres = db.prepare(`
    SELECT g.name 
    FROM video_genres vg
    JOIN genres g ON vg.genre_id = g.id
    WHERE vg.video_id = ?
  `).all(videoRow.id) as CategoryRow[];
  
  // Get makers for this video
  const makers = db.prepare(`
    SELECT m.name 
    FROM video_makers vm
    JOIN makers m ON vm.maker_id = m.id
    WHERE vm.video_id = ?
  `).all(videoRow.id) as CategoryRow[];
  
  return {
    id: videoRow.id,
    code: videoRow.video_code,
    videoUrl: videoRow.video_url,
    m3u8Url: videoRow.m3u8_url,
    quality: videoRow.quality,
    title: videoRow.title,
    releaseDate: videoRow.release_date,
    actresses: actresses.map(a => a.name),
    genres: genres.map(g => g.name),
    makers: makers.map(m => m.name),
    director: videoRow.director,
    label: videoRow.label,
    description: videoRow.description,
    thumbnailUrl: videoRow.thumbnail_url,
  };
}

export function getVideos(): Video[] {
  try {
    const db = getDb();
    const videoRows = db.prepare('SELECT * FROM videos ORDER BY release_date DESC').all() as VideoRow[];
    
    return videoRows.map(buildVideoWithCategories);
  } catch (error) {
    console.error('Error reading from database:', error);
    return [];
  }
}

export function getVideoByCode(code: string): Video | undefined {
  try {
    const db = getDb();
    const videoRow = db.prepare('SELECT * FROM videos WHERE video_code = ?').get(code) as VideoRow | undefined;
    
    if (!videoRow) return undefined;
    
    return buildVideoWithCategories(videoRow);
  } catch (error) {
    console.error('Error reading video from database:', error);
    return undefined;
  }
}
