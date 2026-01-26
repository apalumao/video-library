import sqlite3
import json


def export_db_to_json(db_path='videos.db', output_path='videos.json'):
    """Export SQLite database to JSON for static website."""
    conn = sqlite3.connect(db_path)
    # Return rows as dictionaries
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all videos with m3u8 URLs
    cursor.execute('''
        SELECT *
        FROM videos
        WHERE m3u8_url IS NOT NULL
        ORDER BY video_code
    ''')
    
    videos = []
    for row in cursor.fetchall():
        videos.append({
            'code': row['video_code'],
            'videoUrl': row['video_url'],
            'm3u8Url': row['m3u8_url'],
            'quality': row['quality'],
            'title': row['title'],
            'releaseDate': row['release_date'],
            'actress': row['actress'],
            'genre': row['genre'],
            'maker': row['maker'],
            'director': row['director'],
            'label': row['label'],
            'description': row['description'],
            'thumbnailUrl': row['thumbnail_url']
        })
    
    # Write to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    
    conn.close()
    
    print(f"Exported {len(videos)} videos to {output_path}")
    return len(videos)


if __name__ == "__main__":
    export_db_to_json()
