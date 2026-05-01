import os
import re
import uuid
import threading
import queue
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response, send_file
from yt_dlp import YoutubeDL

app = Flask(__name__)

DOWNLOAD_DIR = Path("/tmp/younds_downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

sessions: dict = {}


def _make_hook(sid: str):
    q = sessions[sid]["q"]

    def hook(d):
        if d["status"] == "downloading":
            raw = re.sub(r"\x1b\[[0-9;]*m", "", d.get("_percent_str", "0%")).strip()
            try:
                pct = float(raw.replace("%", ""))
            except Exception:
                pct = 0
            title = d.get("info_dict", {}).get("title", "")
            spd = re.sub(r"\x1b\[[0-9;]*m", "", d.get("_speed_str", "")).strip()
            eta = re.sub(r"\x1b\[[0-9;]*m", "", d.get("_eta_str", "")).strip()
            q.put(json.dumps({"type": "progress", "pct": pct, "title": title, "speed": spd, "eta": eta}))
        elif d["status"] == "finished":
            q.put(json.dumps({"type": "converting"}))

    return hook


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def start_download():
    data = request.json or {}
    urls = [u.strip() for u in data.get("urls", "").splitlines() if u.strip()]
    mode = data.get("mode", "audio")
    quality = data.get("quality", "320")

    if not urls:
        return jsonify({"error": "Niciun link!"}), 400

    sid = str(uuid.uuid4())
    sid_dir = DOWNLOAD_DIR / sid
    sid_dir.mkdir()
    sessions[sid] = {"q": queue.Queue(), "dir": sid_dir, "files": []}

    def run():
        q = sessions[sid]["q"]
        outtmpl = str(sid_dir / "%(title)s.%(ext)s")

        if mode == "audio":
            opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": quality}],
                "quiet": True,
                "no_warnings": True,
                "ignoreerrors": True,
                "progress_hooks": [_make_hook(sid)],
            }
        else:
            opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
                "ignoreerrors": True,
                "progress_hooks": [_make_hook(sid)],
            }

        try:
            with YoutubeDL(opts) as ydl:
                ydl.download(urls)
            files = [f.name for f in sid_dir.iterdir() if f.is_file()]
            sessions[sid]["files"] = files
            q.put(json.dumps({"type": "done", "files": files}))
        except Exception as e:
            q.put(json.dumps({"type": "error", "msg": str(e)}))
            q.put(json.dumps({"type": "done", "files": []}))

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"session_id": sid})


@app.route("/stream/<sid>")
def stream(sid):
    def generate():
        if sid not in sessions:
            yield f"data: {json.dumps({'type': 'error', 'msg': 'Sesiune invalidă'})}\n\n"
            return
        q = sessions[sid]["q"]
        while True:
            try:
                msg = q.get(timeout=90)
                yield f"data: {msg}\n\n"
                parsed = json.loads(msg)
                if parsed.get("type") == "done":
                    break
            except queue.Empty:
                yield "data: {\"type\":\"ping\"}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/files/<sid>/<path:filename>")
def download_file(sid, filename):
    if sid not in sessions:
        return "Not found", 404
    sid_dir = sessions[sid]["dir"]
    filepath = (sid_dir / filename).resolve()
    if not str(filepath).startswith(str(sid_dir.resolve())):
        return "Forbidden", 403
    if not filepath.exists():
        return "Not found", 404
    return send_file(filepath, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)
