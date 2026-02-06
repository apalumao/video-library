export interface Video {
  id: number;
  code: string;
  videoUrl: string;
  m3u8Url: string;
  quality: string;
  title?: string;
  releaseDate?: string;
  actresses?: string[]; // Changed from string to array
  genres?: string[]; // Changed from string to array
  makers?: string[]; // Changed from string to array
  director?: string;
  label?: string;
  description?: string;
  thumbnailUrl?: string;
}
