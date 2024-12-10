import yt_dlp
import os
from moviepy.editor import AudioFileClip, VideoFileClip

# Directory to store downloaded files
DOWNLOAD_DIR = "downloads"

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def fetch_formats(url):
    """
    Fetch available formats (video and audio) for a given YouTube URL.
    """
    try:
        ydl_opts = {
            'format': 'bestaudio/bestvideo',  # Fetch the best audio and video
            'noplaylist': True,               # Don't download playlist items
            'quiet': True,                    # Suppress output
            'extractaudio': False,            # Don't extract audio separately
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])

            # Filter for video and audio formats
            video_formats = [f for f in formats if 'video' in f['format_id']]
            audio_formats = [f for f in formats if 'audio' in f['format_id']]

            return {
                'status': 'success',
                'video_formats': video_formats,
                'audio_formats': audio_formats
            }

    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def download_video(url, quality):
    """
    Download video or audio based on the specified quality.
    """
    try:
        ydl_opts = {
            'format': quality,  # The format chosen by the user
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),  # Save as the video title
            'quiet': False,  # Show the download process
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)

            return {
                'status': 'success',
                'filename': filename
            }

    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def manual_merge(url, quality):
    """
    Merge video and audio if video has no audio or user selects separate formats.
    """
    try:
        # Download video and audio separately if needed
        video_filename = download_video(url, quality='bestvideo')[ 'filename']
        audio_filename = download_video(url, quality='bestaudio')['filename']

        # Check if the video has no audio track
        if not video_filename or not audio_filename:
            return {'status': 'error', 'message': 'Error downloading video or audio'}

        # Merge video and audio using moviepy
        video_clip = VideoFileClip(video_filename)
        audio_clip = AudioFileClip(audio_filename)

        # Set the audio of the video clip
        video_clip = video_clip.set_audio(audio_clip)

        # Final output file name
        final_filename = os.path.join(DOWNLOAD_DIR, f"{video_filename}.merged.mp4")
        video_clip.write_videofile(final_filename, codec="libx264")

        # Cleanup temporary files
        os.remove(video_filename)
        os.remove(audio_filename)

        return {
            'status': 'success',
            'filename': final_filename
        }

    except Exception as e:
        return {'status': 'error', 'message': str(e)}
        
