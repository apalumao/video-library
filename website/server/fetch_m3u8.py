import asyncio
import nodriver as uc
import sys

async def main():
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        print("Please provide a URL as an argument.")
        # Optional: prompt for input if not provided
        target_url = input("Enter the target URL: ")

    if not target_url:
        print("No URL provided. Exiting.")
        return

    print(f"Starting browser to visit: {target_url}")
    
    # Start the browser
    browser = await uc.start()
    
    # Create a tab
    page = await browser.get(target_url)

    print("Waiting for page to load and network activity...")
    
    # We will look for m3u8 requests. 
    # Nodriver doesn't have a direct "network listener" like Selenium wire easily exposed in high level 
    # but we can listen to connection events or just wait and inspect if possible, 
    # or better, use the CDP protocol directly if needed.
    # However, a simpler approach with nodriver typically involves just loading and checking execution context or resources if available.
    # But for network interception, we might need to hook into the protocol.
    
    # Let's try a robust method: wait for a while and see if we can find it in the network logs if we enabled them.
    # Actually, nodriver (undetected-chromedriver v2 rewrite) allows easy access. 
    # But specific network interception examples often use `add_handler` for network events.
    
    found_m3u8 = False
    
    # Define a handler for network requests
    async def request_listener(event):
        nonlocal found_m3u8
        # The event object is an instance of a class, not a dict.
        # We access attributes directly.
        try:
            url = event.request.url
            if 'video.m3u8' in url:
                print(f"\n[FOUND VIDEO M3U8]: {url}\n")
                found_m3u8 = True
        except AttributeError:
            # In case the event structure is different than expected
            pass

    # Enable network tracking
    # Note: nodriver might auto-enable some, but explicit is better.
    # We need to access the tab's connection to add handlers.
    
    # To properly intercept, we should send Network.enable
    await page.send(uc.cdp.network.enable())
    
    # Add handler for request events
    page.add_handler(uc.cdp.network.RequestWillBeSent, request_listener)
    
    # Wait for a bit (simulate user browsing time or loading)
    # Cloudflare check might take a few seconds
    print("Watching network traffic for 30 seconds... (Press Ctrl+C to stop early)")
    
    try:
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 30:
            if found_m3u8:
                # We found one, but often there are multiple (playlists vs chunks). 
                # We'll keep listening for a bit or until user is satisfied. 
                # For this script, maybe we just print all we find.
                pass
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopping...")

    print("Finished listening.")
    # Keep browser open? The user asked to use their local computer, maybe they want to watch it.
    # The prompt says "fetch the m3u8 link for me", implying extraction is key.
    
    # Close browser? For debugging it's often better to keep it open if it's headful.
    # defaulting to closing for a clean script, but user can comment it out.
    # await browser.stop()

if __name__ == "__main__":
    # Fix for Windows event loop policy if needed
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    try:
        uc.loop().run_until_complete(main())
    except Exception as e:
        print(f"Error: {e}")
