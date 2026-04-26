# 🎵 Younds — Music & Video Downloader

Aplicație desktop simplă și curată pentru descărcat muzică și videoclipuri.

---

## ✅ Instalare

### 1. Instalează dependențele Python

```bash
pip install -r requirements.txt
```

Sau manual:

```bash
pip install customtkinter yt-dlp
```

### 2. Instalează FFmpeg

- Descarcă de la https://ffmpeg.org/download.html  
- Extrage arhiva și pune calea completă spre `ffmpeg.exe` în câmpul din aplicație  
- Exemplu: `C:\ffmpeg\bin\ffmpeg.exe`

---

## ▶ Rulare

```bash
python younds.py
```

---

## 🔧 Funcții

| Funcție | Detalii |
|---|---|
| 🎵 MP3 Audio | Extrage audio la calitate 128 / 192 / 256 / 320 kbps |
| 🎬 MP4 Video | Descarcă video la cea mai bună calitate disponibilă |
| 📋 Link-uri multiple | Pune câte un link pe linie — YouTube, Facebook, etc. |
| 🔢 Numerotare | Index de start pentru a numerota fișierele (ex: 12 - Titlu.mp3) |
| 🍪 Cookies | Suport pentru conținut privat sau geo-restricționat |
| 📁 Folder custom | Alegi exact unde se salvează fișierele |
| 📋 Log în timp real | Vezi progresul fiecărei descărcări |

---

## 💡 Sfaturi

- **Facebook**: Dacă primești eroare la videoclipuri private, folosește un fișier `cookies.txt` exportat din browser
- **Playlist**: Pune link-ul playlist-ului direct în căsuță — funcționează automat
- **Index start**: Dacă ai deja 11 melodii și vrei să continui de la 12, pune `12` în câmpul index

---

## 📦 Structură

```
younds/
├── younds.py        ← Aplicația principală
├── requirements.txt ← Dependențe Python
└── README.md
```