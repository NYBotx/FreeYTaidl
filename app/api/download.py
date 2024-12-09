from yt_dlp import YoutubeDL
import os
from flask import Flask, jsonify, request, send_file
import subprocess

app = Flask(__name__)

DOWNLOAD_FOLDER = "/tmp"

def combine_video_audio(video_path, audio_path, output_path):
    """Combine video and audio using FFmpeg."""
    command = [
        "ffmpeg", "-i", video_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", output_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@app.route('/api/get_formats', methods=['POST'])
def get_formats():
    """Fetch all available formats for a given video."""
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({"status": "error", "message": "No URL provided."}), 400

        with YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            is_live = info.get('is_live', False)

            video_formats = [
                {
                    "format_id": fmt['format_id'],
                    "format_note": fmt['format_note'],
                    "ext": fmt['ext'],
                    "acodec": fmt['acodec']
                }
                for fmt in formats if fmt.get('vcodec') != 'none'
            ]
            audio_formats = [
                {
                    "format_id": fmt['format_id'],
                    "format_note": fmt['format_note'],
                    "ext": fmt['ext']
                }
                for fmt in formats if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none'
            ]

            return jsonify({
                "status": "success",
                "video_formats": video_formats,
                "audio_formats": audio_formats,
                "is_live": is_live
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/download', methods=['POST'])
def download_video():
    """Download video, audio, or combined video+audio."""
    try:
        url = request.json.get('url')
        quality = request.json.get('quality')  # Specific format ID
        download_type = request.json.get('type')  # video, audio, video+audio

        if not url:
            return jsonify({"status": "error", "message": "No URL provided."}), 400

        video_path = os.path.join(DOWNLOAD_FOLDER, "video.mp4")
        audio_path = os.path.join(DOWNLOAD_FOLDER, "audio.mp4")
        output_path = os.path.join(DOWNLOAD_FOLDER, "final_output.mp4")

        # Download based on the selected type
        if download_type == 'video':
            ydl_opts = {
                'format': quality or 'bestvideo',
                'outtmpl': video_path
            }
        elif download_type == 'audio':
            ydl_opts = {
                'format': quality or 'bestaudio',
                'outtmpl': audio_path
            }
        else:  # video+audio
            ydl_opts = {
                'format': quality or 'bestvideo',
                'outtmpl': video_path
            }

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                has_audio = any(
                    fmt['acodec'] != 'none' for fmt in info_dict.get('formats', [])
                )
                ydl.download([url])

            if not has_audio:
                ydl_opts_audio = {
                    'format': 'bestaudio',
                    'outtmpl': audio_path
                }
                with YoutubeDL(ydl_opts_audio) as ydl:
                    ydl.download([url])

                combine_video_audio(video_path, audio_path, output_path)
                return jsonify({
                    "status": "success",
                    "message": "Video+Audio merged successfully!",
                    "download_link": f"/api/download_file?file_path={output_path}"
                })

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        download_file = video_path if download_type == 'video' else audio_path
        return jsonify({
            "status": "success",
            "message": "Download completed!",
            "download_link": f"/api/download_file?file_path={download_file}"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/download_file', methods=['GET'])
def download_file():
    """Serve the final output file."""
    file_path = request.args.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "File not found."}), 404

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
