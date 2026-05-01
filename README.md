# Younds — Music & Video Downloader

A clean, fast desktop and web app for downloading music and videos from YouTube, Facebook, and more.

---

## Installation

### 1. Install Python dependencies

```bash
pip install customtkinter yt-dlp flask
```

### 2. Install FFmpeg

**Linux**
```bash
sudo apt install ffmpeg
```

**macOS**
```bash
brew install ffmpeg
```

**Windows** — download from [ffmpeg.org](https://ffmpeg.org/download.html), extract and set the path in Advanced settings.

---

## Usage

### Desktop app

```bash
python younds.py
```

### Web app

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

---

## Features

| Feature | Details |
|---|---|
| MP3 Audio | Extracts audio at 128 / 192 / 256 / 320 kbps |
| MP4 Video | Downloads video at best available quality |
| Multiple links | One link per line — YouTube, Facebook, etc. |
| Playlists | Paste a playlist URL directly — works automatically |
| Numbering | Start index for numbering files (e.g. `12 - Title.mp3`) |
| Cookies | Support for private or geo-restricted content |
| Custom output folder | Choose exactly where files are saved |
| Real-time progress | Live progress bar with speed and ETA |
| Import .txt | Load a list of URLs from a plain text file (web app) |
| Auto cleanup | Downloaded files are automatically deleted after 1 hour (web app) |

---

## Tips

- **Playlists** — paste the full playlist URL, it downloads all tracks automatically
- **Facebook** — for private videos, export a `cookies.txt` from your browser and load it in Advanced settings
- **Numbering** — if you already have 11 songs and want to continue from 12, set the start index to `12`
- **Cookies file format** — Netscape format `.txt`, exportable via browser extensions like "Get cookies.txt"

---

## Project structure

```
younds/
├── younds.py     ← Desktop app (customtkinter)
├── app.py        ← Web app (Flask)
├── templates/
│   └── index.html
└── README.md
```
