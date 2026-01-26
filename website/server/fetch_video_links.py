import asyncio
import nodriver as uc
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys


async def fetch_video_links(page_url):
    """
    Fetch all video links from a given page URL using nodriver to bypass antibot.
    
    Args:
        page_url: The homepage URL to fetch video links from
        
    Returns:
        List of video URLs found on the page
    """
    try:
        print(f"Starting browser to visit: {page_url}")
        
        # Start the browser with nodriver (undetected chrome)
        browser = await uc.start()
        
        # Navigate to the page
        page = await browser.get(page_url)
        
        print("Waiting for page to load and bypass antibot checks...")
        
        # Wait for the page to fully load and bypass any Cloudflare/antibot checks
        # Usually 5-10 seconds is enough
        await asyncio.sleep(3)
        
        # Get the page HTML content
        html_content = await page.get_content()
        
        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all links on the page
        video_links = set()
        
        # Look for common patterns for video links
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(page_url, href)
            print(f"Found link: {absolute_url}")
            # Filter for video links (pattern like /dm2/en/sone-614)
            ignore_url = ['english','weekly','monthly','today']
            if 'missav.ai' in absolute_url and '-' in absolute_url and not any(ign in absolute_url for ign in ignore_url):
                    video_links.add(absolute_url)
        
        # Close the browser (optional - browser will close automatically when script ends)
        # browser.stop() is not async in nodriver, or we can just let it close naturally
        
        return sorted(list(video_links))
        
    except Exception as e:
        print(f"Error: {e}")
        return []


async def main():
    # Get URL from command line argument or use default
    base_url = 'https://missav.ai/dm515/en/new?sort=views&page='
    
    # Number of pages to fetch (can be modified)
    num_pages = 5
    
    print(f"Fetching video links from {num_pages} pages simultaneously...")
    print("-" * 60)
    
    # Create tasks for fetching multiple pages simultaneously
    tasks = [fetch_video_links(base_url + str(i)) for i in range(1, num_pages + 1)]
    
    # Fetch all pages concurrently
    results = await asyncio.gather(*tasks)
    
    # Combine all video links and remove duplicates
    all_video_links = set()
    for links in results:
        all_video_links.update(links)
    
    video_links = sorted(list(all_video_links))
    
    # Save to file
    output_file = "video_links.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for link in video_links:
            f.write(link + '\n')
    
    # Display results
    if video_links:
        print(f"\nFound {len(video_links)} unique video links:\n")
        for i, link in enumerate(video_links, 1):
            print(f"{i}. {link}")
    else:
        print("No video links found.")
    
    print("-" * 60)
    print(f"Total: {len(video_links)} unique links from {num_pages} pages")
    print(f"Links saved to: {output_file}")


if __name__ == "__main__":
    # Fix for Windows event loop policy if needed
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        uc.loop().run_until_complete(main())
    except Exception as e:
        print(f"Error: {e}")
