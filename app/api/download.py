import yt_dlp
import os
import subprocess
from flask import jsonify

DOWNLOAD_DIR = "downloads"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def fetch_formats(url):
    """
    Fetch available formats for a YouTube video.
    """
    try:
        ydl_opts = {"quiet": True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

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

        return {"status": "success", "video_formats": video_formats, "audio_formats": audio_formats}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

def download_video(url, format_id):
    """
    Download the requested video or audio format.
    """
    try:
        file_path = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
        ydl_opts = {
            "format": format_id,
            "outtmpl": file_path,
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            downloaded_file = ydl.prepare_filename(info)

        filename = os.path.basename(downloaded_file)
        return {"status": "success", "download_link": f"/downloads/{filename}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

def manual_merge(video_url, audio_url):
    """
    Handle manual video and audio merging.
    """
    try:
        video_file_path = os.path.join(DOWNLOAD_DIR, 'video.mp4')
        audio_file_path = os.path.join(DOWNLOAD_DIR, 'audio.mp4')

        # Download video and audio separately
        with yt_dlp.YoutubeDL({"outtmpl": video_file_path}) as ydl:
            ydl.download([video_url])

        with yt_dlp.YoutubeDL({"outtmpl": audio_file_path}) as ydl:
            ydl.download([audio_url])

        # Merge video and audio
        merged_file = os.path.join(DOWNLOAD_DIR, 'merged_video.mp4')
        command = [
            "ffmpeg", "-i", video_file_path, "-i", audio_file_path, "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", merged_file
        ]
        subprocess.run(command)

        # Remove individual video and audio files after merging
        os.remove(video_file_path)
        os.remove(audio_file_path)

        return {"status": "success", "download_link": f"/downloads/merged_video.mp4"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
        
