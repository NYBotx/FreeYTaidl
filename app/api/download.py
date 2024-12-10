from flask import Blueprint, request, jsonify
import yt_dlp
import os

# Define the Blueprint
app = Blueprint('api', __name__)

# Ensure the downloads directory exists
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

COOKIES_FILE = "cookies.txt"  # Path to cookies.txt for authenticated downloads

@app.route('/get_formats', methods=['POST'])
def get_formats():
    """Fetch video and audio formats for the provided YouTube URL."""
    try:
        data = request.json
        url = data.get('url')

        if not url:
            return jsonify({"status": "error", "message": "No URL provided"}), 400

        ydl_opts = {
            "quiet": True,
            "cookies": COOKIES_FILE,  # Use cookies for authentication
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

        # Categorize video and audio formats
        video_formats = [
            {
                "format_id": fmt["format_id"],
                "resolution": fmt.get("resolution", "Unknown"),
                "ext": fmt["ext"],
                "has_audio": fmt.get("acodec") != "none"
            }
            for fmt in formats if fmt.get("vcodec") != "none"
        ]
        audio_formats = [
            {
                "format_id": fmt["format_id"],
                "ext": fmt["ext"]
            }
            for fmt in formats if fmt.get("acodec") != "none"
        ]

        return jsonify({
            "status": "success",
            "video_formats": video_formats,
            "audio_formats": audio_formats
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/download', methods=['POST'])
def download():
    """Download the requested video or audio format."""
    try:
        data = request.json
        url = data.get('url')
        format_id = data.get('quality')

        if not url or not format_id:
            return jsonify({"status": "error", "message": "Missing required parameters"}), 400

        # Set up download options
        ydl_opts = {
            "format": format_id,
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "quiet": True,
            "cookies": COOKIES_FILE,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            file_path = ydl.prepare_filename(info)

        # Return the download link
        filename = os.path.basename(file_path)
        return jsonify({"status": "success", "download_link": f"/downloads/{filename}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
