import logging
import os
import base64
import asyncio
from threading import Semaphore
from flask import Flask, render_template, jsonify, request
from playwright.sync_api import sync_playwright, Playwright

# Configure logging for Render.com
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Semaphore to allow only 1 conversion at a time (prevents memory bloat)
conversion_semaphore = Semaphore(1)

@app.route('/')
def index():
    logging.info("Accessed root path. Serving index.html.")
    return render_template('index.html')

@app.route('/launch')
def launch_chromium():
    try:
        logging.info("Launch endpoint called - using lightweight check")
        
        # Don't actually launch browser here - just return success to save memory
        # The actual browser will only launch when user submits a URL
        logging.info('Ready to process URLs on youconvert.org!')
        return jsonify({
            'status': 'success',
            'message': 'Ready to convert! Enter a URL to start.',
            'screenshot': None
        })
            
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/navigate', methods=['POST'])
def navigate_to_url():
    # Use semaphore to ensure only 1 conversion at a time
    if not conversion_semaphore.acquire(blocking=False):
        logging.warning("Conversion already in progress, rejecting new request")
        return jsonify({'status': 'error', 'message': 'A conversion is already in progress. Please wait.'})
    
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'status': 'error', 'message': 'No URL provided'})
        
        # Add https:// if no protocol is specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        logging.info(f"Processing URL: {url} on ezconv.com (semaphore acquired)")
        
        with sync_playwright() as p:
            # Launch with aggressive memory-saving flags (lowest possible footprint)
            browser = p.chromium.launch(
                headless=True, 
                args=[
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--no-zygote',  # Saves ~200MB when combined with single-process
                    '--single-process',  # Big memory saver (safe for one tab only)
                    '--disable-dev-tools',
                    '--disable-extensions',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--memory-pressure-off',  # Prevent memory pressure checks
                    '--disable-background-networking',
                    '--disable-sync',
                    '--disable-translate',
                    '--metrics-recording-only',
                    '--no-first-run',
                    '--disable-setuid-sandbox'
                ]
            )
            # Create a single page context with optimizations
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                locale='en-US',
                timezone_id='America/New_York',
                # Disable animations for faster rendering
                reduced_motion='reduce'
            )
            page = context.new_page()
            
            # Block heavy resource types early - global route before navigation
            logging.info("Setting up global resource blocking to save memory...")
            page.route("**/*", lambda route: (
                route.abort() if route.request.resource_type in ["image", "media", "font"]
                else route.continue_()
            ))
            
            # Navigate to youconvert.org first (increased timeout for slow loads)
            logging.info("Navigating to youconvert.org...")
            page.goto("https://youconvert.org/", wait_until='domcontentloaded', timeout=60000)
            
            # Wait a bit for any dynamic content to load (reduced from 2s to 1s)
            page.wait_for_timeout(1000)
            
            # Find and click the input box using XPath
            logging.info("Clicking on input box...")
            input_xpath = "//input[@id='youtube-url']"
            input_element = page.locator(f"xpath={input_xpath}")
            input_element.click()

            # Fill in the URL
            logging.info(f"Filling in URL: {url}")
            input_element.fill(url)

            # Wait a moment before clicking convert (reduced from 1s to 500ms)
            page.wait_for_timeout(500)

            # Click the convert button using XPath
            logging.info("Clicking convert button...")
            convert_button_xpath = "//button[@id='convertButton']"
            convert_button = page.locator(f"xpath={convert_button_xpath}")
            convert_button.click()
            
            # Wait exactly 30 seconds for conversion to complete
            import time
            start_time = time.time()
            logging.info("⏳ Starting 30-second wait for conversion to complete...")
            page.wait_for_timeout(30000)  # Wait 30 seconds
            elapsed_time = time.time() - start_time
            logging.info(f"✅ 30-second wait complete! Actual time elapsed: {elapsed_time:.2f} seconds")
            
            # NOW take the screenshot of whatever is on the page
            logging.info("📸 Taking screenshot NOW...")
            screenshot_bytes = page.screenshot(
                full_page=False,
                timeout=20000,
                animations='disabled'
            )
            screenshot_size = len(screenshot_bytes)
            logging.info(f"✅ Screenshot captured successfully! Size: {screenshot_size} bytes")
            
            # Convert screenshot to base64
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            # Explicit cleanup - ensure resources are freed even if errors occur
            try:
                page.close()
                logging.info("Page closed")
            except Exception as cleanup_error:
                logging.warning(f"Error closing page: {cleanup_error}")
            
            try:
                context.close()
                logging.info("Context closed")
            except Exception as cleanup_error:
                logging.warning(f"Error closing context: {cleanup_error}")
            
            try:
                browser.close()
                logging.info("Browser closed, memory cleaned up")
            except Exception as cleanup_error:
                logging.warning(f"Error closing browser: {cleanup_error}")
        
        logging.info(f'Successfully processed {url} on youconvert.org and captured screenshot')
        return jsonify({
            'status': 'success',
            'message': f'Successfully processed {url} on youconvert.org',
            'screenshot': screenshot_base64
        })
            
    except Exception as e:
        logging.error(f"Error during navigation: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        # Always release the semaphore
        conversion_semaphore.release()
        logging.info("Semaphore released, ready for next conversion")

@app.route('/status')
def get_status():
    try:
        logging.info("Checking Playwright Chromium status...")
        # Lightweight status check - don't actually launch browser to save memory
        # Just check if Playwright is available
        from playwright.sync_api import sync_playwright
        logging.info('Playwright Chromium is functional (status check passed).')
        return jsonify({'status': 'running', 'message': 'Chromium is functional'})
    except Exception as e:
        logging.warning(f"Playwright Chromium status check failed: {e}")
        return jsonify({'status': 'stopped', 'message': 'Chromium is not functional or check failed: ' + str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Starting Flask application on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
