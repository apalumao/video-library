import fs from 'fs';
import path from 'path';
import { Video } from './types';

export function getVideos(): Video[] {
  try {
    const filePath = path.join(process.cwd(), 'public', 'videos.json');
    const fileContents = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(fileContents);
  } catch (error) {
    console.error('Error reading videos.json:', error);
    return [];
  }
}

export function getVideoByCode(code: string): Video | undefined {
  const videos = getVideos();
  return videos.find((v) => v.code === code);
}
