from flask import Flask, send_from_directory
from api.download import app as api_app

# Create the Flask application instance
app = Flask(__name__, static_folder="static", static_url_path="/")

# Register the API blueprint from download.py
app.register_blueprint(api_app, url_prefix='/api')

# Serve the index.html file when the root URL is accessed
@app.route('/')
def serve_index():
    return send_from_directory("static", "index.html")

# Ensure the app runs only if this is the main module
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
    
