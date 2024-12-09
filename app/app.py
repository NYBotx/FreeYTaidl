from flask import Flask, render_template, request, jsonify, send_from_directory
from app.api.download import fetch_formats, download_video, manual_merge

app = Flask(__name__)

# Route to render the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to fetch available video and audio formats
@app.route('/get_formats', methods=['POST'])
def get_formats():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"status": "error", "message": "No URL provided"})

    # Fetch formats using the download.py methods
    formats_data = fetch_formats(url)

    return jsonify(formats_data)

# API endpoint to download video/audio or manually merge
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    quality = data.get('quality')

    if not url or not quality:
        return jsonify({"status": "error", "message": "Invalid parameters"})

    # Try to download the selected format
    download_data = download_video(url, quality)

    if download_data['status'] == "success":
        return jsonify(download_data)
    
    # If video and audio need to be merged, attempt that
    return jsonify(manual_merge(url, quality))

# Serve the downloaded files
@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory('downloads', filename)

if __name__ == '__main__':
    app.run(debug=True)
