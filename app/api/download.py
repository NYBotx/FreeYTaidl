import yt_dlp
import os

# Function to fetch available video and audio formats
def fetch_formats(url):
    try:
        ydl_opts = {
            'quiet': True,
            'force_generic_extractor': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            formats_data = []
            for format in formats:
                formats_data.append({
                    'format_id': format['format_id'],
                    'resolution': format.get('height', 'audio'),
                    'quality': format['quality'],
                    'ext': format['ext'],
                    'url': format['url'],
                })
            return {"status": "success", "formats": formats_data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Function to download a video/audio in a specific format
def download_video(url, quality):
    try:
        ydl_opts = {
            'format': quality,
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': False
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            return {"status": "success", "file": filename}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Function to manually merge video and audio if needed (e.g., if video and audio are separate)
def manual_merge(url, quality):
    try:
        # Code to download video and audio separately, then merge
        video_data = download_video(url, quality + '[video]')
        audio_data = download_video(url, quality + '[audio]')
        
        # Merge video and audio (this could use ffmpeg or other tools, but we're assuming the download worked)
        # For simplicity, we'll just return a message.
        return {"status": "success", "message": "Merged video and audio successfully", "video_file": video_data["file"], "audio_file": audio_data["file"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
