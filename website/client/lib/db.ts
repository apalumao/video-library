import Database from 'better-sqlite3';
import path from 'path';

let db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!db) {
    const dbPath = path.join(process.cwd(), 'videos.db');
    db = new Database(dbPath);
    db.pragma('journal_mode = WAL'); // Better performance for concurrent reads
  }
  return db;
}

export function closeDb() {
  if (db) {
    db.close();
    db = null;
  }
}
