# Media Downloader 🎬

A sleek, user-friendly desktop application for downloading videos and audio from social media platforms and video sharing sites.

## Features

- 🎥 **Download Videos** - Download videos in various quality options (360p, 480p, 720p, 1080p)
- 🎵 **Extract Audio** - Extract audio as MP3 from videos
- 📸 **Preview Thumbnails** - See video thumbnails before downloading
- 📚 **Download History** - Keep track of all your downloaded media
- 🎨 **Modern Dark UI** - Beautiful, intuitive interface built with CustomTkinter
- 🚀 **Fast Downloads** - Powered by yt-dlp for reliable downloads

## Supported Platforms

Works with:
- YouTube
- TikTok
- Instagram
- And many other sites supported by yt-dlp

## Requirements

- Python 3.8 or higher
- ffmpeg (for audio/video conversion)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/social-media-downloader.git
cd social-media-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download ffmpeg:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use: `choco install ffmpeg`
   - **Mac**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`

## Usage

Run the application:
```bash
python media_downloader.py
```

### How to Use

1. **Paste URL**: Enter or paste the media URL in the input field
2. **Select Quality**: Choose your preferred quality (360p, 480p, 720p, 1080p, or MP3)
3. **Choose Folder** (Optional): Click "Folder" to select where files should be saved
4. **Download**: Click "Download Now" to start the download
5. **View History**: Check the "Library" tab to see your download history

## Features Explained

### Download Tab
- **URL Input**: Paste direct links to videos
- **Quality Selection**: Choose video quality or audio-only (MP3) format
- **Preview**: See video thumbnails before downloading
- **Progress Bar**: Real-time download progress tracking
- **Folder Selection**: Pick a custom download location

### Library Tab
- **Download History**: View all previously downloaded media
- **Quick Access**: See metadata about your downloads

## Configuration

Downloaded files are saved to your Downloads folder by default. You can change the download location by clicking the "Folder" button in the application.

## Known Limitations

- Some sites may restrict downloading due to their terms of service
- Quality availability depends on the source
- Requires internet connection for download

## Troubleshooting

**Issue**: "ffmpeg not found"
- **Solution**: Install ffmpeg and add it to your system PATH

**Issue**: Downloads fail or are slow
- **Solution**: Check your internet connection and ensure the URL is valid

**Issue**: Quality options not available
- **Solution**: Some sources may not have all quality options available

## Contributing

Contributions are welcome! Feel free to submit issues and enhancement requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for personal use only. Users are responsible for respecting copyright laws and terms of service of the platforms they download from. The author assumes no liability for misuse of this software.

## Author

Created with ❤️

---

⭐ If you find this helpful, please consider giving it a star!
