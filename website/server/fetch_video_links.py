import asyncio
import nodriver as uc
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

# Configuration
CONCURRENT_LIMIT = 5  # Scan 5 pages at once
BASE_URL = 'https://missav.ai/dm515/en/new?sort=views&page='
START_PAGE = 201
END_PAGE = 1000
MAX_PAGES_SAFETY = 500 # Stop after scanning this many pages to prevent infinite loop

async def fetch_links_from_tab(browser, page_num, semaphore):
    """
    Fetch video links from a specific page number. 
    Continuously checks page content every 3 seconds until 12 valid links are found or timeout (50s).
    """
    url = f"{BASE_URL}{page_num}"
    timeout = 50
    check_interval = 3
    
    async with semaphore:
        page = None
        try:
            print(f"Scanning Page {page_num}...")
            
            # Open new tab
            page = await browser.get(url, new_tab=True)
            
            video_links = set()
            ignore_keywords = ['english', 'weekly', 'monthly', 'today', 'en/uncensored-leak', 'en/chinese-subtitle', 'siro', 'luxu', 'gana', 'heyzo', 'caribbean', '1pon', '10musume', 'pacopacomama']
            
            elapsed_time = 0
            
            # Keep checking every 3 seconds until we get 12 links or timeout
            while elapsed_time < timeout:
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval
                
                # Get HTML
                html_content = await page.get_content()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find links
                video_links = set()
                for link in soup.find_all('a', href=True):

                    href = link['href']
                    absolute_url = urljoin(url, href)
                    # print(absolute_url)
                    if 'missav.ai' in absolute_url and '-' in absolute_url:
                        if not any(k in absolute_url for k in ignore_keywords):
                            video_links.add(absolute_url)
                
                count = len(video_links)
                print(f"  Page {page_num} at {elapsed_time}s: Found {count} links")
                
                if count >= 10:
                    print(f"  ✓ Page {page_num}: Found {count} links (Success)")
                    await page.close()
                    return video_links
            
            # Timeout reached
            print(f"  ⚠ Page {page_num}: Timeout after {timeout}s with {len(video_links)} links")
            await page.close()
            return video_links

        except Exception as e:
            print(f"  ✗ Page {page_num} Error: {e}")
            if page:
                try:
                    await page.close()
                except:
                    pass
            return set()

async def main():
    print(f"Starting Scan: Pages {START_PAGE} to {END_PAGE}")
    print(f"Strategy: Scanning batches of {CONCURRENT_LIMIT} pages concurrently")
    print("=" * 60)
    
    try:
        browser = await uc.start()
    except TypeError:
        browser = await uc.start()

    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    all_links = set()
    current_page = START_PAGE
    
    while current_page <= min(END_PAGE, MAX_PAGES_SAFETY):
        tasks = []
        # Create a batch of tasks
        batch_end = min(current_page + CONCURRENT_LIMIT, END_PAGE + 1, MAX_PAGES_SAFETY + 1)
        pages_in_batch = range(current_page, batch_end)
        
        print(f"\nScanning Batch: Pages {current_page} - {batch_end - 1}")
        
        for p in pages_in_batch:
            tasks.append(fetch_links_from_tab(browser, p, semaphore))
        
        # Run tasks
        for future in asyncio.as_completed(tasks):
            res = await future
            all_links.update(res)
            
        print(f"Current Total Found: {len(all_links)} unique videos")
        
        if current_page >= END_PAGE:
            print(f"Reached end page: {END_PAGE}")
            break
            
        current_page += CONCURRENT_LIMIT
        
        # Small pause between batches
        await asyncio.sleep(2)
    
    browser.stop()
    
    sorted_links = sorted(list(all_links))
    
    # Save results
    output_file = f"video_links{START_PAGE}-{END_PAGE}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for link in sorted_links:
            f.write(link + '\n')
            
    print("\n" + "=" * 60)
    print(f"Scan Complete!")
    print(f"Total Unique Videos Found: {len(sorted_links)}")
    print(f"Saved to: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        uc.loop().run_until_complete(main())
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
