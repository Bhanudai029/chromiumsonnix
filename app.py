import logging
import os
from flask import Flask, render_template, jsonify
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
        logging.info("Attempting to launch Chromium via Playwright...")
        
        # Use sync_playwright to launch a headless Chromium browser
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'])
            # You can perform some basic action to confirm launch, e.g., open a new page
            page = browser.new_page()
            page.goto("about:blank") # Load a blank page
            browser.close()

        logging.info('Chromium launched successfully via Playwright!')
        return jsonify({'status': 'success', 'message': 'Chromium launched successfully!'})
            
    except Exception as e:
        logging.critical(f"Unhandled exception during Chromium launch via Playwright: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/status')
def get_status():
    try:
        logging.info("Checking Playwright Chromium status...")
        # Playwright does not expose a direct way to check if a browser is *running* outside its context
        # Instead, we will try to launch a new, very quick headless browser instance.
        # If it succeeds, it implies the Playwright Chromium is functional.
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, timeout=5000, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'])
            browser.close()
        logging.info('Playwright Chromium is functional (status check passed).')
        return jsonify({'status': 'running', 'message': 'Chromium is functional'})
    except Exception as e:
        logging.warning(f"Playwright Chromium status check failed: {e}")
        return jsonify({'status': 'stopped', 'message': 'Chromium is not functional or check failed: ' + str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Starting Flask application on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
