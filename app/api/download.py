from flask import Blueprint, request, jsonify, send_from_directory
import yt_dlp
import os

# Define the Blueprint
app = Blueprint('api', __name__)

# Ensure the downloads directory exists
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/get_formats', methods=['POST'])
def get_formats():
    """
    Fetch video and audio formats for the provided YouTube URL.
    """
    try:
        data = request.json
        url = data.get('url')

        if not url:
            return jsonify({"status": "error", "message": "No URL provided"}), 400

        ydl_opts = {"quiet": True}
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
    """
    Download the requested video or audio format.
    """
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
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            file_path = ydl.prepare_filename(info)

        # Return the download link
        filename = os.path.basename(file_path)
        return jsonify({"status": "success", "download_link": f"/downloads/{filename}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/check_high_quality', methods=['POST'])
def check_high_quality():
    """
    Check if a high-quality video without audio is available and suggest a manual combination.
    """
    try:
        data = request.json
        url = data.get('url')

        if not url:
            return jsonify({"status": "error", "message": "No URL provided"}), 400

        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

        high_quality_video = next(
            (fmt for fmt in formats if fmt.get("vcodec") != "none" and fmt.get("acodec") == "none"), None
        )
        audio_format = next(
            (fmt for fmt in formats if fmt.get("acodec") != "none"), None
        )

        if high_quality_video and audio_format:
            return jsonify({
                "status": "success",
                "high_quality_video": {
                    "format_id": high_quality_video["format_id"],
                    "resolution": high_quality_video.get("resolution", "Unknown"),
                    "ext": high_quality_video["ext"]
                },
                "audio_format": {
                    "format_id": audio_format["format_id"],
                    "ext": audio_format["ext"]
                }
            })
        else:
            return jsonify({"status": "error", "message": "No high-quality video or audio found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/download_live', methods=['POST'])
def download_live():
    """
    Download a live stream video.
    """
    try:
        data = request.json
        url = data.get('url')

        if not url:
            return jsonify({"status": "error", "message": "No URL provided"}), 400

        # Check if the URL points to a live stream
        ydl_opts = {
            "quiet": True,
            "live_from_start": True,  # Start downloading as soon as possible
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Check if it's a live stream
            if info.get("is_live"):
                ydl_opts["format"] = "best"  # Download the best quality
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_live:
                    info_live = ydl_live.extract_info(url)
                    file_path = ydl_live.prepare_filename(info_live)
                    filename = os.path.basename(file_path)
                    return jsonify({
                        "status": "success",
                        "message": "Live stream is being downloaded",
                        "download_link": f"/downloads/{filename}"
                    })
            else:
                return jsonify({"status": "error", "message": "This is not a live stream"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
