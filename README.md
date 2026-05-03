# 🎥 YouTube High-Res Downloader

A lightweight, robust Python script to download YouTube videos and entire playlists in the highest possible quality. 

This tool intelligently separates the highest quality video and audio streams, then merges them losslessly in seconds using a localized, modern FFmpeg binary. This bypasses the common issue of outdated system-level FFmpeg installations causing file corruption or codec errors.

## ✨ Features
* **Smart URL Detection:** Automatically detects whether you provided a single video or a full playlist.
* **Quality Selection:** Scans available resolutions and lets you choose your maximum preferred video quality (e.g., 4K, 1080p, 720p).
* **Lossless Merging:** Always pulls the highest quality audio stream and merges it with the video without re-encoding, preserving 100% of the original quality.
* **Automated Organization:** Creates a clean workspace. Playlist downloads are automatically routed into their own dedicated subfolders named after the playlist.
* **Error Resilience:** Gracefully skips private or deleted videos in a playlist without crashing the entire queue.
* **Zero FFmpeg Setup:** Uses `imageio-ffmpeg` to manage dependencies, meaning you don't need to manually install or configure FFmpeg on your operating system.

## 🛠️ Prerequisites
* **Python 3.7+** installed on your system.

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hany73-max/youtube-downloader.git
   cd youtube-downloader
2. Install the required dependencies:

    ```Bash
    pip install yt-dlp imageio-ffmpeg
    ```

### 💻 Usage
1. Run the script from your terminal:

    ```Bash
    python downloader.py
    ```

2. Paste the YouTube URL when prompted.

3. If applicable, select your preferred maximum video resolution from the generated list.

4. Let the script do the work!

### Folder Structure Output  
The script automatically generates folders to keep your workspace clean:

- Temp_Workspace/ — Used temporarily during the download process and automatically deleted when finished.

- Final_Downloads/ — Your final .mp4 files will appear here. Playlists will generate their own subfolders inside this directory.

## ⚠️ Disclaimer  
This tool is intended for personal use and educational purposes. Please respect YouTube's Terms of Service and the copyright of content creators. Do not distribute downloaded content without permission.


### Next Steps:
1. Save this text into a file named `README.md` inside your folder.
2. In the installation section of the text above, don't forget to change `YourUsername` to your actual GitHub username (`hany73-max`).
3. If your script is still named `trial.py`, I highly recommend renaming it to something professional like `downloader.py` or `main.py` before you push it to GitHub again!