from flask import Blueprint, jsonify, request
import yt_dlp
import os

app = Blueprint('api', __name__)  # Create a blueprint

DOWNLOAD_DIR = "downloads"

# Ensure the downloads directory exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/get_formats', methods=['POST'])
def get_formats():
    """
    Fetch available formats for a given YouTube URL.
    """
    url = request.json.get('url')
    if not url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    try:
        ydl_opts = {
            'format': 'bestaudio/bestvideo',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            return jsonify({"status": "success", "formats": formats})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    """
    Download a video or audio from YouTube.
    """
    url = request.json.get('url')
    quality = request.json.get('quality')
    if not url or not quality:
        return jsonify({"status": "error", "message": "Invalid parameters"}), 400

    try:
        ydl_opts = {
            'format': quality,
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return jsonify({"status": "success", "filename": filename})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
