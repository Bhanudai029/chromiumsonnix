import logging
import subprocess
import os
from flask import Flask, render_template, jsonify

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
        logging.info("Attempting to launch Chromium...")
        # Try different Chromium binary names and ensure --no-sandbox for Render.com
        chromium_commands = [
            ['chromium-browser', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--remote-debugging-port=9222'],
            ['chromium', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--remote-debugging-port=9222'],
            ['google-chrome', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--remote-debugging-port=9222'],
            ['chrome', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--remote-debugging-port=9222']
        ]
        
        launched = False
        for cmd in chromium_commands:
            try:
                logging.info(f"Trying command: {' '.join(cmd)}")
                # Launch in background, detach from parent process, redirect stdout/stderr to avoid blocking
                # Using preexec_fn=os.setsid on Linux to detach process group
                process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
                logging.info(f"Chromium process started with PID: {process.pid}")
                launched = True
                break
            except FileNotFoundError:
                logging.warning(f"Chromium binary not found with command: {' '.join(cmd)}")
                continue
            except Exception as e:
                logging.error(f"Error launching Chromium with command {' '.join(cmd)}: {e}")
                continue
        
        if launched:
            logging.info('Chromium launched successfully!')
            return jsonify({'status': 'success', 'message': 'Chromium launched successfully!'})
        else:
            logging.error('Could not find or launch any Chromium binary.')
            return jsonify({'status': 'error', 'message': 'Could not find Chromium binary'})
            
    except Exception as e:
        logging.critical(f"Unhandled exception during Chromium launch: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/status')
def get_status():
    try:
        logging.info("Checking Chromium status...")
        # Check if Chromium is running using pgrep
        # Use a more specific pattern to avoid false positives
        result = subprocess.run(['pgrep', '-f', 'chromium-browser|chromium|google-chrome|chrome'], capture_output=True, text=True)
        
        if result.returncode == 0:
            logging.info('Chromium is running.')
            return jsonify({'status': 'running', 'message': 'Chromium is running'})
        else:
            logging.info('Chromium is not running.')
            return jsonify({'status': 'stopped', 'message': 'Chromium is not running'})
    except FileNotFoundError:
        logging.error("pgrep command not found. Cannot check Chromium status.")
        return jsonify({'status': 'error', 'message': 'pgrep command not found, cannot check status'})
    except Exception as e:
        logging.critical(f"Unhandled exception during status check: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Starting Flask application on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
