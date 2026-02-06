import sqlite3
import csv
from pathlib import Path
from datetime import datetime


def create_database(db_path='videos.db'):
    """Create SQLite database with normalized schema for categories."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing tables to recreate schema
    cursor.execute('DROP TABLE IF EXISTS video_makers')
    cursor.execute('DROP TABLE IF EXISTS video_genres')
    cursor.execute('DROP TABLE IF EXISTS video_actresses')
    cursor.execute('DROP TABLE IF EXISTS makers')
    cursor.execute('DROP TABLE IF EXISTS genres')
    cursor.execute('DROP TABLE IF EXISTS actresses')
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
            director TEXT,
            label TEXT,
            description TEXT,
            thumbnail_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create normalized category tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS makers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create junction tables for many-to-many relationships
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_actresses (
            video_id INTEGER NOT NULL,
            actress_id INTEGER NOT NULL,
            PRIMARY KEY (video_id, actress_id),
            FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
            FOREIGN KEY (actress_id) REFERENCES actresses(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_genres (
            video_id INTEGER NOT NULL,
            genre_id INTEGER NOT NULL,
            PRIMARY KEY (video_id, genre_id),
            FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
            FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_makers (
            video_id INTEGER NOT NULL,
            maker_id INTEGER NOT NULL,
            PRIMARY KEY (video_id, maker_id),
            FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
            FOREIGN KEY (maker_id) REFERENCES makers(id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_code ON videos(video_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_actresses_video ON video_actresses(video_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_actresses_actress ON video_actresses(actress_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_genres_video ON video_genres(video_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_genres_genre ON video_genres(genre_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_makers_video ON video_makers(video_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_makers_maker ON video_makers(maker_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_actresses_name ON actresses(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_genres_name ON genres(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_makers_name ON makers(name)')
    
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
    """Import CSV data into SQLite database with normalized categories."""
    if not Path(csv_path).exists():
        print(f"Error: {csv_path} not found!")
        return
    
    conn = create_database(db_path)
    cursor = conn.cursor()
    
    # Read CSV and import data
    imported = 0
    skipped = 0
    actress_count = 0
    genre_count = 0
    maker_count = 0
    
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
                # Insert video (without actress, genre, maker as text)
                cursor.execute('''
                    INSERT INTO videos (
                        video_url, m3u8_url, video_code, quality,
                        title, release_date, director, label, description, thumbnail_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    video_url,
                    m3u8_url,
                    video_code,
                    quality,
                    row.get('title', ''),
                    row.get('release_date', ''),
                    row.get('director', ''),
                    row.get('label', ''),
                    row.get('description', ''),
                    row.get('thumbnail_url', '')
                ))
                
                video_id = cursor.lastrowid
                imported += 1
                
                # Process actresses (comma-separated)
                actress_str = row.get('actress', '')
                if actress_str:
                    actresses = [a.strip() for a in actress_str.split(',') if a.strip()]
                    for actress_name in actresses:
                        # Insert or get actress ID
                        cursor.execute('INSERT OR IGNORE INTO actresses (name) VALUES (?)', (actress_name,))
                        cursor.execute('SELECT id FROM actresses WHERE name = ?', (actress_name,))
                        actress_id = cursor.fetchone()[0]
                        
                        # Link video to actress
                        cursor.execute('''
                            INSERT OR IGNORE INTO video_actresses (video_id, actress_id) 
                            VALUES (?, ?)
                        ''', (video_id, actress_id))
                        actress_count += 1
                
                # Process genres (comma-separated)
                genre_str = row.get('genre', '')
                if genre_str:
                    genres = [g.strip() for g in genre_str.split(',') if g.strip()]
                    for genre_name in genres:
                        # Insert or get genre ID
                        cursor.execute('INSERT OR IGNORE INTO genres (name) VALUES (?)', (genre_name,))
                        cursor.execute('SELECT id FROM genres WHERE name = ?', (genre_name,))
                        genre_id = cursor.fetchone()[0]
                        
                        # Link video to genre
                        cursor.execute('''
                            INSERT OR IGNORE INTO video_genres (video_id, genre_id) 
                            VALUES (?, ?)
                        ''', (video_id, genre_id))
                        genre_count += 1
                
                # Process makers
                maker_str = row.get('maker', '')
                if maker_str:
                    maker_name = maker_str.strip()
                    if maker_name:
                        # Insert or get maker ID
                        cursor.execute('INSERT OR IGNORE INTO makers (name) VALUES (?)', (maker_name,))
                        cursor.execute('SELECT id FROM makers WHERE name = ?', (maker_name,))
                        maker_id = cursor.fetchone()[0]
                        
                        # Link video to maker
                        cursor.execute('''
                            INSERT OR IGNORE INTO video_makers (video_id, maker_id) 
                            VALUES (?, ?)
                        ''', (video_id, maker_id))
                        maker_count += 1
                        
            except sqlite3.IntegrityError:
                print(f"Skipping duplicate: {video_url}")
                skipped += 1
    
    conn.commit()
    
    # Print summary
    try:
        total_records = cursor.execute('SELECT COUNT(*) FROM videos').fetchone()[0]
        with_m3u8 = cursor.execute('SELECT COUNT(*) FROM videos WHERE m3u8_url IS NOT NULL').fetchone()[0]
        actress_total = cursor.execute('SELECT COUNT(*) FROM actresses').fetchone()[0]
        genre_total = cursor.execute('SELECT COUNT(*) FROM genres').fetchone()[0]
        maker_total = cursor.execute('SELECT COUNT(*) FROM makers').fetchone()[0]
        
        print("=" * 60)
        print("Import Complete!")
        print("-" * 60)
        print(f"Imported: {imported} new videos")
        print(f"Skipped: {skipped} duplicates")
        print(f"Total videos in database: {total_records}")
        print(f"Videos with m3u8: {with_m3u8}")
        print(f"Videos without m3u8: {total_records - with_m3u8}")
        print()
        print("Normalized Categories:")
        print(f"  Total unique actresses: {actress_total}")
        print(f"  Total unique genres: {genre_total}")
        print(f"  Total unique makers: {maker_total}")
        print(f"  Actress relationships: {actress_count}")
        print(f"  Genre relationships: {genre_count}")
        print(f"  Maker relationships: {maker_count}")
        print()
        print(f"Database saved to: {db_path}")
        print("=" * 60)
    except Exception as e:
        print(f"Error printing summary: {e}")
    
    conn.close()


def query_examples(db_path='videos.db'):
    """Show some example queries with normalized schema."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n" + "=" * 60)
        print("Example Queries with Normalized Schema:")
        print("=" * 60)
        
        # Example 1: Find a specific video with all categories
        print("\n1. Sample video with all categories:")
        cursor.execute('''
            SELECT v.video_code, v.title
            FROM videos v
            LIMIT 1
        ''')
        result = cursor.fetchone()
        if result:
            code, title = result
            # Get actresses
            cursor.execute('''
                SELECT GROUP_CONCAT(a.name, ', ')
                FROM video_actresses va
                JOIN actresses a ON va.actress_id = a.id
                WHERE va.video_id = (SELECT id FROM videos WHERE video_code = ?)
            ''', (code,))
            actresses = cursor.fetchone()[0]
            
            # Get genres
            cursor.execute('''
                SELECT GROUP_CONCAT(g.name, ', ')
                FROM video_genres vg
                JOIN genres g ON vg.genre_id = g.id
                WHERE vg.video_id = (SELECT id FROM videos WHERE video_code = ?)
            ''', (code,))
            genres = cursor.fetchone()[0]
            
            # Get makers
            cursor.execute('''
                SELECT GROUP_CONCAT(m.name, ', ')
                FROM video_makers vm
                JOIN makers m ON vm.maker_id = m.id
                WHERE vm.video_id = (SELECT id FROM videos WHERE video_code = ?)
            ''', (code,))
            makers = cursor.fetchone()[0]
            
            print(f"   Code: {code}")
            print(f"   Title: {title[:50]}...")
            print(f"   Actresses: {actresses}")
            print(f"   Genres: {genres}")
            print(f"   Makers: {makers}")
        
        # Example 2: Top actresses by video count
        print("\n2. Top 5 actresses by video count:")
        cursor.execute('''
            SELECT a.name, COUNT(va.video_id) as video_count
            FROM actresses a
            JOIN video_actresses va ON a.id = va.actress_id
            GROUP BY a.id
            ORDER BY video_count DESC
            LIMIT 5
        ''')
        for name, count in cursor.fetchall():
            print(f"   {name}: {count} videos")
        
        # Example 3: Filter by actress
        print("\n3. Videos by specific actress:")
        cursor.execute('SELECT name FROM actresses LIMIT 1')
        actress = cursor.fetchone()
        if actress:
            actress_name = actress[0]
            cursor.execute('''
                SELECT v.video_code, v.title
                FROM videos v
                JOIN video_actresses va ON v.id = va.video_id
                JOIN actresses a ON va.actress_id = a.id
                WHERE a.name = ?
                LIMIT 3
            ''', (actress_name,))
            print(f"   Videos featuring '{actress_name}':")
            for code, title in cursor.fetchall():
                print(f"     - {code}: {title[:45]}...")
        
        # Example 4: Multi-filter (genre + maker)
        print("\n4. Complex query - Videos by genre and maker:")
        cursor.execute('''
            SELECT v.video_code, v.title
            FROM videos v
            JOIN video_genres vg ON v.id = vg.video_id
            JOIN genres g ON vg.genre_id = g.id
            JOIN video_makers vm ON v.id = vm.video_id
            JOIN makers m ON vm.maker_id = m.id
            WHERE g.name = 'Creampie' AND m.name = 'Prestige'
            LIMIT 3
        ''')
        results = cursor.fetchall()
        if results:
            print(f"   Videos with genre 'Creampie' and maker 'Prestige':")
            for code, title in results:
                print(f"     - {code}: {title[:45]}...")
        else:
            print("   (No matches found for this combination)")
        
        # Example 5: Top genres
        print("\n5. Top 5 genres by video count:")
        cursor.execute('''
            SELECT g.name, COUNT(vg.video_id) as video_count
            FROM genres g
            JOIN video_genres vg ON g.id = vg.genre_id
            GROUP BY g.id
            ORDER BY video_count DESC
            LIMIT 5
        ''')
        for name, count in cursor.fetchall():
            print(f"   {name}: {count} videos")
        
        print("=" * 60)
        conn.close()
    except Exception as e:
        print(f"Error in query examples: {e}")


if __name__ == "__main__":
    csv_file = "video_m3u8_links.csv"
    db_file = "videos.db"
    
    print(f"Converting {csv_file} to SQLite database with normalized schema...")
    import_csv_to_db(csv_file, db_file)
    query_examples(db_file)
    
    print("\n" + "=" * 60)
    print("API Query Examples for Next.js:")
    print("=" * 60)
    print()
    print("  // Get all videos by actress")
    print("  SELECT v.* FROM videos v")
    print("  JOIN video_actresses va ON v.id = va.video_id")
    print("  JOIN actresses a ON va.actress_id = a.id")
    print("  WHERE a.name = 'Remu Suzumori'")
    print()
    print("  // Filter by multiple categories")
    print("  SELECT v.* FROM videos v")
    print("  JOIN video_genres vg ON v.id = vg.video_id")
    print("  JOIN genres g ON vg.genre_id = g.id")
    print("  WHERE g.name = 'Creampie'")
    print()
    print("  // Get all categories for listing pages")
    print("  SELECT * FROM actresses ORDER BY name")
    print("  SELECT * FROM genres ORDER BY name")
    print("  SELECT * FROM makers ORDER BY name")
    print("=" * 60)
