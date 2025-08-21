from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello from Render! Your app is running."

if __name__ == '__main__':
    # This block is for local testing only; Render uses Gunicorn
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
