import yt_dlp
import subprocess
import os
import re
import imageio_ffmpeg

# --- Configuration ---
TEMP_DIR = "Temp_Workspace"
OUTPUT_DIR = "Final_Downloads"

def setup_directories():
    """Ensures our workspace and root output directories exist."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize_filename(title: str) -> str:
    """Removes illegal characters from video/playlist titles."""
    return re.sub(r'[\\/*?:"<>|]', "", title).strip()

def fetch_video_data(url: str) -> tuple:
    """Detects if the URL is a single video or playlist, returning URLs and playlist title."""
    print("\n[*] Analyzing URL...")
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'quiet': True,
        'no_warnings': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                videos = [entry['url'] for entry in info['entries'] if entry.get('url')]
                playlist_title = sanitize_filename(info.get('title', 'Unknown_Playlist'))
                print(f"[+] Playlist detected: '{playlist_title}' ({len(videos)} videos)")
                return videos, playlist_title
            else:
                print(f"[+] Single video detected: '{info.get('title', 'Unknown')}'")
                return [url], None
        except Exception as e:
            print(f"[!] Failed to fetch info from URL: {e}")
            return [], None

def get_user_quality_preference(sample_url: str) -> str:
    """Fetches available resolutions from a sample video and asks the user to choose."""
    print("\n[*] Fetching available video qualities...")
    ydl_opts = {'quiet': True, 'no_warnings': True}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(sample_url, download=False)
            formats = info.get('formats', [])
            
            # Extract unique video heights (resolutions)
            heights = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('height'):
                    heights.add(f['height'])
            
            # Sort highest to lowest
            sorted_heights = sorted(list(heights), reverse=True)
            
            if not sorted_heights:
                print("[!] Could not detect specific qualities. Defaulting to Best.")
                return 'bestvideo[ext=mp4]'
                
            print("\nAvailable Maximum Video Qualities:")
            print("0. Best Available (Default)")
            for i, h in enumerate(sorted_heights, start=1):
                print(f"{i}. {h}p")
                
            choice = input("\nEnter the number of your choice (or press Enter for Best): ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(sorted_heights):
                selected_height = sorted_heights[int(choice)-1]
                print(f"[*] You selected: Max {selected_height}p")
                # The <= ensures playlist fallback (if a video lacks 1080p, it gets 720p instead of failing)
                return f'bestvideo[height<={selected_height}][ext=mp4]'
            else:
                print("[*] Defaulting to Best Available.")
                return 'bestvideo[ext=mp4]'
                
        except Exception as e:
            print(f"[!] Error fetching qualities: {e}. Defaulting to Best.")
            return 'bestvideo[ext=mp4]'

def download_stream(url: str, output_path: str, is_video: bool, video_format: str):
    """Downloads either the video or audio stream."""
    # Use user's chosen format for video, always use best for audio
    format_selector = video_format if is_video else 'bestaudio[ext=m4a]'
    stream_type = "Video" if is_video else "Audio"
    
    print(f"    -> Downloading {stream_type}...")
    ydl_opts = {
        'format': format_selector,
        'outtmpl': output_path,
        'quiet': True,       
        'no_warnings': True,
        'fixup': 'never'     
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def merge_streams(video_path: str, audio_path: str, output_path: str):
    """Merges the raw streams using the modern imageio-ffmpeg binary."""
    print(f"    -> Merging streams into final MP4...")
    
    modern_ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    
    command = [
        modern_ffmpeg_path,
        '-y',             
        '-i', video_path, 
        '-i', audio_path, 
        '-c:v', 'copy',   
        '-c:a', 'aac',    
        output_path,
        '-loglevel', 'error' 
    ]

    subprocess.run(command, check=True)

def process_single_video(url: str, current_num: int, total_num: int, target_folder: str, video_format: str):
    """Handles the full pipeline for a single video URL."""
    print(f"\n==================================================")
    print(f"[*] Processing Video {current_num} of {total_num}")
    
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            safe_title = sanitize_filename(info.get('title', f'Unknown_Video_{current_num}'))
            print(f"[*] Title: {safe_title}")
        except Exception as e:
            print(f"[!] Skipping video (might be private or deleted): {url}")
            return

    temp_vid = os.path.join(TEMP_DIR, f"{safe_title}_vid.mp4")
    temp_aud = os.path.join(TEMP_DIR, f"{safe_title}_aud.m4a")
    final_out = os.path.join(target_folder, f"{safe_title}.mp4")

    try:
        download_stream(url, temp_vid, is_video=True, video_format=video_format)
        download_stream(url, temp_aud, is_video=False, video_format=video_format)
        merge_streams(temp_vid, temp_aud, final_out)
        
        if os.path.exists(temp_vid): os.remove(temp_vid)
        if os.path.exists(temp_aud): os.remove(temp_aud)
        print(f"[+] Success! Saved to: {final_out}")
        
    except Exception as e:
        print(f"\n[!] An error occurred while processing '{safe_title}': {e}")
        if os.path.exists(temp_vid): os.remove(temp_vid)
        if os.path.exists(temp_aud): os.remove(temp_aud)

if __name__ == "__main__":
    setup_directories()
    
    target_url = input("Enter a YouTube Video or Playlist URL: ").strip()
    
    if target_url:
        urls_to_download, playlist_title = fetch_video_data(target_url)
        total_videos = len(urls_to_download)
        
        if total_videos > 0:
            # 1. Ask the user for their preferred quality based on the first video
            sample_video_url = urls_to_download[0]
            chosen_video_format = get_user_quality_preference(sample_video_url)

            # 2. Determine target folder (Playlist subfolder vs Main folder)
            if playlist_title:
                active_output_dir = os.path.join(OUTPUT_DIR, playlist_title)
                os.makedirs(active_output_dir, exist_ok=True)
            else:
                active_output_dir = OUTPUT_DIR

            # 3. Process the queue
            for index, vid_url in enumerate(urls_to_download, start=1):
                process_single_video(vid_url, index, total_videos, active_output_dir, chosen_video_format)
            
            print(f"\n[+] All tasks complete! Your videos are located in: '{active_output_dir}'")
            
            if not os.listdir(TEMP_DIR):
                os.rmdir(TEMP_DIR)
        else:
            print("[!] Could not extract any videos from the provided URL.")
    else:
        print("[!] No URL provided. Exiting.")