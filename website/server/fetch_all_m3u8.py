import asyncio
import nodriver as uc
import sys
import csv
import re
from pathlib import Path
from bs4 import BeautifulSoup


async def fetch_m3u8_from_url(url):
    """
    Fetch m3u8 link and metadata from a video page URL.
    """
    found_m3u8 = None
    metadata = {
        'title': '',
        'code': '',
        'release_date': '',
        'actress': '',
        'genre': '',
        'maker': '',
        'director': '',
        'label': '',
        'description': '',
        'thumbnail_url': ''
    }
    
    try:
        print(f"Processing: {url}")
        
        # Start the browser
        browser = await uc.start()
        
        # Navigate to the page
        page = await browser.get(url)
        
        # Define a handler for network requests
        async def request_listener(event):
            nonlocal found_m3u8
            try:
                request_url = event.request.url
                if request_url.endswith('video.m3u8'):
                    print(f"  [FOUND M3U8]: {request_url}")
                    if found_m3u8 is None:
                        found_m3u8 = request_url
            except AttributeError:
                pass
        
        # Enable network tracking
        await page.send(uc.cdp.network.enable())
        page.add_handler(uc.cdp.network.RequestWillBeSent, request_listener)
        
        print("  Watching for m3u8 link and scrubbing metadata...")
        
        # Wait a bit for page load
        await asyncio.sleep(5)
        
        # Fetch HTML content for metadata scrubbing
        html_content = await page.get_content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # --- Metadata Extraction ---
        
        # 1. Title
        h1_tag = soup.find('h1')
        if h1_tag:
            metadata['title'] = h1_tag.get_text(strip=True)
            
        # 2. Extract details map
        # Structure often uses div.text-secondary for metadata rows
        
        # Helper to clean up values (remove extra spaces, commas)
        def clean_val(text):
            # 1. Replace all potential separators (commas, spaces) with a single pipe first to normalize
            # The website is likely using hidden text or weird unicode spaces causing the issue
            # Let's simple try to collapse all comma-space sequences into a single comma-space
            text = re.sub(r'[\s,]+', ', ', text)
            return text.strip(', ')

        # Try to find all metadata rows
        info_divs = soup.select('div.text-secondary')
        
        for div in info_divs:
            # Find the label (usually the first span)
            label_span = div.find('span')
            if not label_span:
                continue
                
            label = label_span.get_text(strip=True).rstrip(':').lower()
            
            # Extract the raw text without the label
            # We clone the div to not destroy the original soup if needed elsewhere
            # But here we don't need soup later
            label_span.decompose() # Remove label from this div
            
            # The structure might be: <span>Label</span> <a ...>Val1</a>, <a...>Val2</a>
            # Getting text with separator=', ' is creating the double commas because there are text nodes (commas) + separator
            # Best approach: Get text from the anchors if they exist, or just rigorous cleaning
            
            if div.find('a'):
                # Collect text from all links
                value = ', '.join([a.get_text(strip=True) for a in div.find_all('a')])
            else:
                # Just text, clean it aggressively
                raw_text = div.get_text(separator=' ', strip=True)
                value = re.sub(r'[\s,]+', ', ', raw_text).strip(', ')
            
            if 'code' == label:
                metadata['code'] = value
            elif 'release date' == label:
                metadata['release_date'] = value
            elif 'actress' == label:
                metadata['actress'] = value
            elif 'genre' == label:
                metadata['genre'] = value
            elif 'maker' == label:
                metadata['maker'] = value
            elif 'director' == label:
                metadata['director'] = value
            elif 'label' == label:
                metadata['label'] = value
        
        # Fallback regex if soup selection failed (e.g. class names changed)
        if not metadata['code']:
            text_content = soup.get_text()
            def extract_field(pattern):
                match = re.search(pattern, text_content, re.IGNORECASE)
                return match.group(1).strip() if match else ''
            
            metadata['code'] = extract_field(r'Code:[\s\xa0]*([A-Za-z0-9-]+)')
            metadata['release_date'] = extract_field(r'Release date:[\s\xa0]*([\d-]+)')
        
        # Description is tricky, usually a block of text before "Release date"
        # We can look for meta description potentially
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '').strip()
            
        # 3. Construct Thumbnail
        if metadata['code']:
            metadata['thumbnail_url'] = f"https://fourhoi.com/{metadata['code'].lower()}/cover-n.jpg"
            
        print(f"  [METADATA]: Found {metadata['code']} | {metadata['title'][:30]}...")

        # Wait up to 20s for m3u8 (reduced from 30)
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 20:
            if found_m3u8:
                break
            await asyncio.sleep(1)
        
        browser.stop()
        
        return found_m3u8, metadata
        
    except Exception as e:
        print(f"  Error processing {url}: {e}")
        return None, metadata


async def main():
    # Read video links from file
    input_file = "video_links.txt"
    output_file = "video_m3u8_links.csv"
    
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found!")
        return
    
    # Read all video links
    with open(input_file, 'r', encoding='utf-8') as f:
        video_links = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(video_links)} video links to process")
    print("=" * 60)
    
    # Prepare CSV file
    results = []
    
    # Process each video link
    for i, video_url in enumerate(video_links, 1):
        print(f"\n[{i}/{len(video_links)}]")
        m3u8_url, metadata = await fetch_m3u8_from_url(video_url)
        
        row = {
            'video_url': video_url,
            'm3u8_url': m3u8_url if m3u8_url else 'Not found',
            **metadata
        }
        results.append(row)
        
        print(f"  Status: {'✓ Found' if m3u8_url else '✗ Not found'}")
        print("-" * 60)
    
    # Write results to CSV
    fieldnames = ['video_url', 'm3u8_url', 'title', 'code', 'release_date', 'actress', 'genre', 'maker', 'director', 'label', 'description', 'thumbnail_url']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Summary
    found_count = sum(1 for r in results if r['m3u8_url'] != 'Not found')
    print("\n" + "=" * 60)
    print(f"Processing complete!")
    print(f"Total videos: {len(results)}")
    print(f"M3U8 found: {found_count}")
    print(f"M3U8 not found: {len(results) - found_count}")
    print(f"Results saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    # Fix for Windows event loop policy if needed
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        uc.loop().run_until_complete(main())
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
