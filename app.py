from flask import Flask, render_template, jsonify
import subprocess
import sys
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/launch')
def launch_chromium():
    try:
        # Try different Chromium binary names
        chromium_commands = [
            ['chromium-browser', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--remote-debugging-port=9222'],
            ['chromium', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--remote-debugging-port=9222'],
            ['google-chrome', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--remote-debugging-port=9222'],
            ['chrome', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--remote-debugging-port=9222']
        ]
        
        launched = False
        for cmd in chromium_commands:
            try:
                # Launch in background
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                launched = True
                break
            except FileNotFoundError:
                continue
        
        if launched:
            return jsonify({'status': 'success', 'message': 'Chromium launched successfully!'})
        else:
            return jsonify({'status': 'error', 'message': 'Could not find Chromium binary'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/status')
def get_status():
    try:
        # Check if Chromium is running
        result = subprocess.run(['pgrep', '-f', 'chromium'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({'status': 'running', 'message': 'Chromium is running'})
        else:
            return jsonify({'status': 'stopped', 'message': 'Chromium is not running'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
