import asyncio
import nodriver as uc
import sys
import csv
import re
from pathlib import Path
from bs4 import BeautifulSoup

# Configuration
CONCURRENT_LIMIT = 5
DEFAULT_TIMEOUT = 30

async def fetch_m3u8_from_tab(browser, url, semaphore):
    """
    Fetch m3u8 link and metadata from a video page URL using a new tab in an existing browser.
    """
    async with semaphore:
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
        
        page = None
        try:
            print(f"Starting: {url}")
            
            # Open new tab
            page = await browser.get(url, new_tab=True)
            
            # Request Listener
            async def request_listener(event):
                nonlocal found_m3u8
                try:
                    request_url = event.request.url
                    if request_url.endswith('video.m3u8'):
                        if found_m3u8 is None:
                            print(f"  [FOUND M3U8]: {url} -> {request_url}")
                            found_m3u8 = request_url
                except AttributeError:
                    pass
            
            # Enable network tracking for this tab
            await page.send(uc.cdp.network.enable())
            page.add_handler(uc.cdp.network.RequestWillBeSent, request_listener)
            
            # Wait for m3u8 detection
            # We wait a max of X seconds while checking periodically
            for _ in range(DEFAULT_TIMEOUT):
                if found_m3u8:
                    break
                await asyncio.sleep(1)
            
            if not found_m3u8:
                print(f"  [TIMEOUT] No M3U8 found for {url}")

            # Fetch HTML content for metadata scrubbing
            html_content = await page.get_content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # --- Metadata Extraction ---
            
            # 1. Title
            h1_tag = soup.find('h1')
            if h1_tag:
                metadata['title'] = h1_tag.get_text(strip=True)
                
            # 2. Extract details map
            info_divs = soup.select('div.text-secondary')
            
            # Helper: collapse multiple commas/spaces
            def clean_val(text):
                text = re.sub(r'[\s,]+', ', ', text)
                return text.strip(', ')

            for div in info_divs:
                label_span = div.find('span')
                if not label_span:
                    continue
                    
                label = label_span.get_text(strip=True).rstrip(':').lower()
                label_text = label # Keep for checking purpose
                
                # Clone div to modify it safely
                # Actually, simple way: remove span from soup object of this div
                label_span.decompose() 
                
                # Extract text
                if div.find('a'):
                    # Get text from anchors to avoid comma issues
                    links = [a.get_text(strip=True) for a in div.find_all('a')]
                    text_content = ", ".join(links)
                else:
                    text_content = div.get_text(strip=True)
                
                text_content = clean_val(text_content)
                
                if 'code' in label:
                    metadata['code'] = text_content
                elif 'date' in label:
                    metadata['release_date'] = text_content
                elif 'actress' in label:
                    metadata['actress'] = text_content
                elif 'genre' in label:
                    metadata['genre'] = text_content
                elif 'maker' in label:
                    metadata['maker'] = text_content
                elif 'director' in label:
                    metadata['director'] = text_content
                elif 'label' in label:
                    metadata['label'] = text_content

            # 3. Description
            # Try to find description block
            # Common pattern: <div class="text-secondary mb-3">...</div> or similar
            # Since we processed metadata rows, any remaining text-secondary might be description
            # But safer is to look for a specific container if known.
            # Fallback: Look for the longest text block in main content area
            main_content = soup.select_one('div.container')
            if main_content:
                # This is heuristic but works often
                pass

            # 4. Thumbnail
            poster = soup.find('video', attrs={'poster': True})
            if poster:
                metadata['thumbnail_url'] = poster['poster']
            elif metadata['code']:
                metadata['thumbnail_url'] = f"https://fourhoi.com/{metadata['code']}/cover-n.jpg"

            return {
                'video_url': url,
                'm3u8_url': found_m3u8 if found_m3u8 else 'Not found',
                **metadata
            }
            
        except Exception as e:
            print(f"  Error processing {url}: {e}")
            return {
                'video_url': url,
                'm3u8_url': 'Error',
                **metadata
            }
        finally:
            if page:
                try:
                    await page.close()
                except:
                    pass


async def main():
    # Read video links from file
    input_file = "video_links201-1000.txt"
    output_file = "video_m3u8_links201-1000.csv"
    
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found!")
        return
    
    # Read all video links
    with open(input_file, 'r', encoding='utf-8') as f:
        video_links = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(video_links)} video links to process")
    print(f"Running with {CONCURRENT_LIMIT} concurrent tabs")
    print("=" * 60)
    
    # Start the browser ONCE
    try:
        browser = await uc.start()
    except TypeError:
        # Fallback for older nodriver versions
        browser = await uc.start()

    # Create Semaphore
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    
    # Create Tasks
    tasks = []
    for link in video_links:
        tasks.append(fetch_m3u8_from_tab(browser, link, semaphore))
    
    # Run tasks and wait for results
    results = []
    
    # Use asyncio.as_completed to show progress
    for future in asyncio.as_completed(tasks):
        res = await future
        results.append(res)
        print(f"Completed: {res.get('code', 'Unknown')} ({len(results)}/{len(video_links)})")
    
    try:
        browser.stop()
    except:
        pass
    
    # Write results to CSV
    fieldnames = ['video_url', 'm3u8_url', 'title', 'code', 'release_date', 'actress', 'genre', 'maker', 'director', 'label', 'description', 'thumbnail_url']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Summary
    found_count = sum(1 for r in results if r['m3u8_url'] != 'Not found' and r['m3u8_url'] != 'Error')
    print("\n" + "=" * 60)
    print(f"Processing complete!")
    print(f"Total videos: {len(results)}")
    print(f"M3U8 found: {found_count}")
    print(f"Results saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    # Fix for Windows event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        uc.loop().run_until_complete(main())
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
