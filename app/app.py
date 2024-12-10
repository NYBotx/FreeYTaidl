from flask import Flask
from api.download import app as api_app  # Import the blueprint from api.download

app = Flask(__name__)

# Register the blueprint for the API routes
app.register_blueprint(api_app, url_prefix='/api')

# Root route for serving the main page
@app.route('/')
def index():
    return "Welcome to the YouTube Downloader API! Use /api for API calls."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # Runs on port 8080
