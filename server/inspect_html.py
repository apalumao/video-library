import asyncio
import nodriver as uc
from bs4 import BeautifulSoup

async def inspect_page():
    try:
        browser = await uc.start()
        page = await browser.get('https://missav.ai/dm515/en/new?sort=views&page=1')
        print("Waiting for page load...")
        await asyncio.sleep(8) # increased wait time
        content = await page.get_content()
        soup = BeautifulSoup(content, 'html.parser')
        
        print(f"Page Title: {soup.title.string if soup.title else 'No title'}")
        
        links = soup.find_all('a', href=True)
        found = False
        for link in links:
            href = link['href']
            if 'missav.ai' in href and '-' in href and '/en/' in href: 
                print("\n--- Found Video Link Element ---")
                print(link.prettify())
                print("\n--- Parent Element ---")
                print(link.parent.prettify())
                found = True
                break
        
        if not found:
            print("No video links found matching pattern.")
            
        browser.stop()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(inspect_page())
