import sqlite3
import csv
from pathlib import Path
from datetime import datetime


def create_database(db_path='videos.db'):
    """Create SQLite database and table schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing table to update schema
    cursor.execute('DROP TABLE IF EXISTS videos')
    
    # Create videos table with comprehensive metadata
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_url TEXT UNIQUE NOT NULL,
            m3u8_url TEXT,
            video_code TEXT,
            quality TEXT,
            title TEXT,
            release_date TEXT,
            actress TEXT,
            genre TEXT,
            maker TEXT,
            director TEXT,
            label TEXT,
            description TEXT,
            thumbnail_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_code ON videos(video_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_actress ON videos(actress)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_genre ON videos(genre)')
    
    conn.commit()
    return conn


def extract_video_info(video_url, m3u8_url):
    """Extract video code and quality from URLs as fallback."""
    # Extract video code from URL (e.g., 'sone-614')
    # Use code from CSV if available, otherwise fallback to URL parsing
    video_code = video_url.rstrip('/').split('/')[-1]
    
    # Extract quality from m3u8 URL
    quality = None
    if m3u8_url and m3u8_url != 'Not found':
        parts = m3u8_url.split('/')
        for part in parts:
            if 'x' in part or 'p' in part:
                quality = part
                break
    
    return video_code, quality


def import_csv_to_db(csv_path, db_path='videos.db'):
    """Import CSV data into SQLite database."""
    if not Path(csv_path).exists():
        print(f"Error: {csv_path} not found!")
        return
    
    conn = create_database(db_path)
    cursor = conn.cursor()
    
    # Read CSV and import data
    imported = 0
    skipped = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            video_url = row.get('video_url', '')
            m3u8_url = row.get('m3u8_url', '')
            
            # Parse fallback/legacy logic
            video_code_fallback, quality = extract_video_info(video_url, m3u8_url)
            
            # Get values from CSV or fallback
            video_code = row.get('code') or video_code_fallback
            
            if m3u8_url == 'Not found':
                m3u8_url = None
            
            try:
                cursor.execute('''
                    INSERT INTO videos (
                        video_url, m3u8_url, video_code, quality,
                        title, release_date, actress, genre, 
                        maker, director, label, description, thumbnail_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    video_url,
                    m3u8_url,
                    video_code,
                    quality,
                    row.get('title', ''),
                    row.get('release_date', ''),
                    row.get('actress', ''),
                    row.get('genre', ''),
                    row.get('maker', ''),
                    row.get('director', ''),
                    row.get('label', ''),
                    row.get('description', ''),
                    row.get('thumbnail_url', '')
                ))
                imported += 1
            except sqlite3.IntegrityError:
                print(f"Skipping duplicate: {video_url}")
                skipped += 1
    
    conn.commit()
    
    # Print summary
    try:
        total_records = cursor.execute('SELECT COUNT(*) FROM videos').fetchone()[0]
        with_m3u8 = cursor.execute('SELECT COUNT(*) FROM videos WHERE m3u8_url IS NOT NULL').fetchone()[0]
        
        print("=" * 60)
        print("Import Complete!")
        print("-" * 60)
        print(f"Imported: {imported} new records")
        print(f"Skipped: {skipped} duplicates")
        print(f"Total records in database: {total_records}")
        print(f"Records with m3u8: {with_m3u8}")
        print(f"Records without m3u8: {total_records - with_m3u8}")
        print(f"Database saved to: {db_path}")
        print("=" * 60)
    except Exception as e:
        print(f"Error printing summary: {e}")
    
    conn.close()


def query_examples(db_path='videos.db'):
    """Show some example queries."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n" + "=" * 60)
        print("Example Queries:")
        print("=" * 60)
        
        # Example 1: Find a specific video
        print("\n1. Find video by code (e.g., 'sone-614'):")
        cursor.execute('SELECT video_url, m3u8_url FROM videos WHERE video_code = ?', ('sone-614',))
        result = cursor.fetchone()
        if result:
            print(f"   Video: {result[0]}")
            print(f"   M3U8: {result[1]}")
        
        # Example 2: Count by quality
        print("\n2. Count videos by quality:")
        cursor.execute('SELECT quality, COUNT(*) FROM videos WHERE quality IS NOT NULL GROUP BY quality')
        for quality, count in cursor.fetchall():
            print(f"   {quality}: {count} videos")
        
        # Example 3: Recent additions
        print("\n3. Latest 5 videos added:")
        cursor.execute('SELECT video_code, video_url FROM videos ORDER BY created_at DESC LIMIT 5')
        for i, (code, url) in enumerate(cursor.fetchall(), 1):
            print(f"   {i}. {code} - {url}")
        
        print("=" * 60)
        conn.close()
    except Exception:
        pass


if __name__ == "__main__":
    csv_file = "video_m3u8_links.csv"
    db_file = "videos.db"
    
    print(f"Converting {csv_file} to SQLite database...")
    import_csv_to_db(csv_file, db_file)
    query_examples(db_file)
    
    print("\n" + "=" * 60)
    print("You can now query the database using Python or any SQLite tool!")
    print("Example Python code:")
    print()
    print("  import sqlite3")
    print("  conn = sqlite3.connect('videos.db')")
    print("  cursor = conn.cursor()")
    print("  cursor.execute('SELECT * FROM videos WHERE video_code = ?', ('sone-614',))")
    print("  print(cursor.fetchone())")
    print("=" * 60)
