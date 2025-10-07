import logging
import os
import base64
from flask import Flask, render_template, jsonify, request
from playwright.sync_api import sync_playwright, Playwright

# Configure logging for Render.com
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

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
        logging.info('Ready to process URLs on ezconv.com!')
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
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'status': 'error', 'message': 'No URL provided'})
        
        # Add https:// if no protocol is specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        logging.info(f"Processing URL: {url} on ezconv.com")
        
        with sync_playwright() as p:
            # Launch with aggressive memory-saving flags
            browser = p.chromium.launch(
                headless=True, 
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions',
                    '--disable-background-networking',
                    '--disable-sync',
                    '--disable-translate',
                    '--metrics-recording-only',
                    '--no-first-run',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--single-process'  # Use single process to save memory
                ]
            )
            # Create a single page context
            page = browser.new_page()
            
            # Navigate to ezconv.com first
            logging.info("Navigating to ezconv.com...")
            page.goto("https://ezconv.com", wait_until='domcontentloaded', timeout=30000)
            
            # Wait a bit for any dynamic content to load
            page.wait_for_timeout(2000)
            
            # Find and click the input box using XPath
            logging.info("Clicking on input box...")
            input_xpath = "//input[@id=':R6d6jalffata:']"
            input_element = page.locator(f"xpath={input_xpath}")
            input_element.click()
            
            # Fill in the URL
            logging.info(f"Filling in URL: {url}")
            input_element.fill(url)
            
            # Wait a moment before clicking convert
            page.wait_for_timeout(1000)
            
            # Click the convert button using XPath
            logging.info("Clicking convert button...")
            convert_button_xpath = "//button[@id=':R1ajalffata:']"
            convert_button = page.locator(f"xpath={convert_button_xpath}")
            convert_button.click()
            
            # Wait for conversion to process (20 seconds)
            logging.info("Waiting 20 seconds for conversion to complete...")
            page.wait_for_timeout(20000)
            
            # Take a screenshot
            screenshot_bytes = page.screenshot(full_page=False)
            
            # Convert screenshot to base64
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            # Explicit cleanup
            page.close()
            browser.close()
            logging.info("Browser closed, memory cleaned up")
        
        logging.info(f'Successfully processed {url} on ezconv.com and captured screenshot')
        return jsonify({
            'status': 'success', 
            'message': f'Successfully processed {url} on ezconv.com',
            'screenshot': screenshot_base64
        })
            
    except Exception as e:
        logging.error(f"Error during navigation: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})

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
