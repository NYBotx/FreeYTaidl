from flask import Flask, send_from_directory
from api.download import app as api_app

# Create the Flask app
app = Flask(__name__, static_folder="static", static_url_path="/")

# Register the API Blueprint
app.register_blueprint(api_app, url_prefix='/api')

# Serve the index.html file
@app.route('/')
def serve_index():
    return send_from_directory("static", "index.html")

# Serve downloaded files
@app.route('/downloads/<path:filename>')
def serve_download(filename):
    return send_from_directory("downloads", filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
    
