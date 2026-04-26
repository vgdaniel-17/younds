"""
Younds - Music & Video Downloader
Redesigned UI - dark, modern, lime accent
"""

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from yt_dlp import YoutubeDL
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG          = "#0F0F0F"
PANEL       = "#1A1A1A"
CARD        = "#181818"
BORDER      = "#2A2A2A"
ACCENT      = "#C8FF00"
ACCENT_DIM  = "#9BBF00"
TEXT        = "#F0F0F0"
TEXT_SUB    = "#888888"
TEXT_MUTED  = "#444444"
SUCCESS     = "#C8FF00"
ERROR       = "#FF4444"
WARN        = "#FFAA00"

FONT_BODY   = ("Segoe UI", 11)
FONT_HEAD   = ("Segoe UI", 11, "bold")
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10)


class SectionCard(ctk.CTkFrame):
    def __init__(self, master, title, **kw):
        super().__init__(master, fg_color=CARD, corner_radius=12,
                         border_width=1, border_color=BORDER, **kw)
        ctk.CTkLabel(self, text=title, font=("Segoe UI", 9, "bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 0))

    def body(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=16, pady=(6, 14))
        return f


class DarkEntry(ctk.CTkEntry):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color="#111111", border_color=BORDER,
                         border_width=1, corner_radius=8, text_color=TEXT,
                         placeholder_text_color=TEXT_MUTED, font=FONT_BODY,
                         height=38, **kw)


class SmallBtn(ctk.CTkButton):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color="#252525", hover_color=BORDER,
                         text_color=TEXT_SUB, corner_radius=8,
                         font=FONT_SMALL, height=38, width=72, **kw)


class Downloader:
    def __init__(self, log_fn, progress_fn, done_fn):
        self.log = log_fn
        self.progress = progress_fn
        self.done = done_fn

    def _hook(self):
        def h(d):
            if d["status"] == "downloading":
                raw = re.sub(r"\x1b\[[0-9;]*m", "", d.get("_percent_str", "")).strip()
                try:
                    self.progress(float(raw.replace("%", "")))
                except Exception:
                    pass
                spd = d.get("_speed_str", "?").strip()
                eta = d.get("_eta_str", "?").strip()
                self.log(f"  {raw}  ·  {spd}  ·  ETA {eta}", TEXT_MUTED)
            elif d["status"] == "finished":
                self.log("  ✓  Procesat", SUCCESS)
            elif d["status"] == "error":
                self.log("  ✗  Eroare", ERROR)
        return h

    def download(self, urls, output_dir, mode, quality, start_index, ffmpeg_path, cookies_file):
        if mode == "audio":
            fmt = "bestaudio/best"
            pp  = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": quality}]
            pp_args = {}
        else:
            fmt = "bestvideo+bestaudio/best"
            pp  = [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]
            pp_args = {"FFmpegVideoConvertor": ["-c:v","copy","-c:a","aac","-b:a","192k"]}

        outtmpl = os.path.join(output_dir,
            "%(autonumber)d - %(title)s.%(ext)s" if start_index > 0 else "%(title)s.%(ext)s")

        opts = {
            "format": fmt, "outtmpl": outtmpl, "postprocessors": pp,
            "keepvideo": False, "ignoreerrors": True, "quiet": True,
            "no_warnings": True, "progress_hooks": [self._hook()],
            "merge_output_format": "mp4" if mode == "video" else None,
        }
        if start_index > 0:
            opts["autonumber_start"] = start_index
        if ffmpeg_path:
            p = ffmpeg_path.strip()
            opts["ffmpeg_location"] = os.path.dirname(p) if os.path.isfile(p) else p
        if pp_args:
            opts["postprocessor_args"] = pp_args
        if cookies_file and os.path.isfile(cookies_file):
            opts["cookiefile"] = cookies_file

        try:
            with YoutubeDL(opts) as ydl:
                ydl.download(urls)
            self.done(True)
        except Exception as e:
            self.log(f"  Eroare: {e}", ERROR)
            self.done(False)


class YoundsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Younds")
        self.geometry("760x830")
        self.minsize(620, 700)
        self.configure(fg_color=BG)
        self._downloading = False
        self._q_btns = []
        self._build()

    def _build(self):
        # Left accent stripe
        ctk.CTkFrame(self, width=3, fg_color=ACCENT, corner_radius=0).pack(side="left", fill="y")

        main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        main.pack(side="left", fill="both", expand=True)

        # Header
        hdr = ctk.CTkFrame(main, fg_color=PANEL, corner_radius=0, height=70)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        logo = ctk.CTkFrame(hdr, fg_color="transparent")
        logo.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(logo, text="YOU", font=("Segoe UI", 24, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkLabel(logo, text="NDS", font=("Segoe UI", 24, "bold"), text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(logo, text="  ·  downloader", font=("Segoe UI", 10), text_color=TEXT_MUTED).pack(side="left")

        # Body
        scroll = ctk.CTkScrollableFrame(main, fg_color=BG, corner_radius=0,
                                        scrollbar_button_color="#252525",
                                        scrollbar_button_hover_color=BORDER)
        scroll.pack(fill="both", expand=True)

        P = dict(padx=18, pady=(0, 12))

        # ── URL ──
        c = SectionCard(scroll, "LINKURI DE DESCĂRCAT")
        c.pack(fill="x", **P, pady=(18, 12))
        b = c.body()
        self._url_box = ctk.CTkTextbox(
            b, height=96, font=FONT_MONO, fg_color="#111111",
            border_color=BORDER, border_width=1, corner_radius=8,
            text_color=TEXT, wrap="word", scrollbar_button_color=BORDER)
        self._url_box.pack(fill="x")
        ctk.CTkLabel(b, text="Un link per linie  ·  YouTube  ·  Facebook  ·  Playlist-uri",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w", pady=(4,0))

        # ── Format ──
        c2 = SectionCard(scroll, "FORMAT")
        c2.pack(fill="x", **P)
        b2 = c2.body()

        fmt_row = ctk.CTkFrame(b2, fg_color="transparent")
        fmt_row.pack(fill="x", pady=(0, 10))
        self._mode_var = ctk.StringVar(value="audio")

        self._btn_audio = ctk.CTkButton(
            fmt_row, text="🎵  MP3 Audio", font=FONT_HEAD, height=42, corner_radius=8,
            fg_color=ACCENT, text_color=BG, hover_color=ACCENT_DIM,
            command=lambda: self._set_mode("audio"))
        self._btn_audio.pack(side="left", expand=True, fill="x", padx=(0,8))

        self._btn_video = ctk.CTkButton(
            fmt_row, text="🎬  MP4 Video", font=FONT_HEAD, height=42, corner_radius=8,
            fg_color="#252525", text_color=TEXT_SUB, hover_color=BORDER,
            command=lambda: self._set_mode("video"))
        self._btn_video.pack(side="left", expand=True, fill="x")

        # Quality chips
        q_row = ctk.CTkFrame(b2, fg_color="transparent")
        q_row.pack(fill="x")
        ctk.CTkLabel(q_row, text="Calitate audio:", font=FONT_SMALL,
                     text_color=TEXT_SUB).pack(side="left", padx=(0,10))
        self._quality_var = ctk.StringVar(value="320")
        for q in ["128", "192", "256", "320"]:
            active = q == "320"
            btn = ctk.CTkButton(
                q_row, text=f"{q}k", font=FONT_SMALL, height=28, width=56,
                corner_radius=6,
                fg_color=(ACCENT if active else "#252525"),
                text_color=(BG if active else TEXT_SUB),
                hover_color=(ACCENT_DIM if active else BORDER),
                command=lambda v=q: self._set_quality(v))
            btn._q_val = q
            btn.pack(side="left", padx=(0,6))
            self._q_btns.append(btn)

        # ── Output folder ──
        c3 = SectionCard(scroll, "FOLDER IEȘIRE")
        c3.pack(fill="x", **P)
        b3 = c3.body()
        row = ctk.CTkFrame(b3, fg_color="transparent")
        row.pack(fill="x")
        self._folder_var = ctk.StringVar(value=os.path.expanduser("~/Music/Younds"))
        DarkEntry(row, textvariable=self._folder_var).pack(side="left", fill="x", expand=True, padx=(0,8))
        SmallBtn(row, text="Alege", command=self._pick_folder).pack(side="left")

        # ── Advanced ──
        c4 = SectionCard(scroll, "AVANSAT")
        c4.pack(fill="x", **P)
        b4 = c4.body()

        ctk.CTkLabel(b4, text="FFmpeg", font=FONT_SMALL, text_color=TEXT_SUB).pack(anchor="w")
        r1 = ctk.CTkFrame(b4, fg_color="transparent")
        r1.pack(fill="x", pady=(2,10))
        self._ffmpeg_var = ctk.StringVar(value="/usr/bin/ffmpeg")
        DarkEntry(r1, textvariable=self._ffmpeg_var, font=FONT_MONO).pack(side="left", fill="x", expand=True, padx=(0,8))
        SmallBtn(r1, text="Alege", command=self._pick_ffmpeg).pack(side="left")

        ctk.CTkLabel(b4, text="Cookies (opțional)", font=FONT_SMALL, text_color=TEXT_SUB).pack(anchor="w")
        r2 = ctk.CTkFrame(b4, fg_color="transparent")
        r2.pack(fill="x", pady=(2,10))
        self._cookies_var = ctk.StringVar(value="")
        DarkEntry(r2, textvariable=self._cookies_var, placeholder_text="Lasă gol dacă nu ai nevoie").pack(
            side="left", fill="x", expand=True, padx=(0,8))
        SmallBtn(r2, text="Alege", command=self._pick_cookies).pack(side="left")

        ctk.CTkLabel(b4, text="Index start numerotare  (0 = fără număr)", font=FONT_SMALL, text_color=TEXT_SUB).pack(anchor="w")
        r3 = ctk.CTkFrame(b4, fg_color="transparent")
        r3.pack(fill="x", pady=(2,0))
        self._index_var = ctk.StringVar(value="0")
        DarkEntry(r3, textvariable=self._index_var, width=80).pack(side="left")
        ctk.CTkLabel(r3, text="   ex: 12  →  12 - Titlu.mp3, 13 - Titlu.mp3…",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left")

        # ── Progress ──
        c5 = SectionCard(scroll, "PROGRES")
        c5.pack(fill="x", **P)
        b5 = c5.body()
        self._progress_var = ctk.DoubleVar(value=0)
        ctk.CTkProgressBar(b5, variable=self._progress_var, height=6, corner_radius=3,
                           fg_color="#252525", progress_color=ACCENT).pack(fill="x", pady=(0,6))
        self._status_lbl = ctk.CTkLabel(b5, text="Gata de descărcare.",
                                        font=FONT_SMALL, text_color=TEXT_MUTED, anchor="w")
        self._status_lbl.pack(fill="x")

        # ── Buttons ──
        btn_f = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_f.pack(fill="x", padx=18, pady=(0,12))

        self._dl_btn = ctk.CTkButton(
            btn_f, text="↓   DESCARCĂ",
            font=("Segoe UI", 14, "bold"), height=52, corner_radius=10,
            fg_color=ACCENT, hover_color=ACCENT_DIM, text_color=BG,
            command=self._start)
        self._dl_btn.pack(fill="x", pady=(0,8))

        self._cancel_btn = ctk.CTkButton(
            btn_f, text="✕  Oprește",
            font=FONT_BODY, height=36, corner_radius=10,
            fg_color="#1E1E1E", hover_color="#252525", text_color=TEXT_SUB,
            state="disabled", command=self._cancel)
        self._cancel_btn.pack(fill="x")

        # ── Log ──
        c6 = SectionCard(scroll, "LOG")
        c6.pack(fill="x", padx=18, pady=(0,20))
        b6 = c6.body()
        self._log_box = ctk.CTkTextbox(
            b6, height=130, font=FONT_MONO, fg_color="#0D0D0D",
            border_color=BORDER, border_width=1, corner_radius=8,
            text_color=TEXT_SUB, state="disabled", wrap="word",
            scrollbar_button_color=BORDER)
        self._log_box.pack(fill="x", pady=(0,6))
        ctk.CTkButton(b6, text="Șterge", width=80, height=24, corner_radius=6,
                      font=FONT_SMALL, fg_color="#1A1A1A", hover_color="#252525",
                      text_color=TEXT_MUTED, command=self._clear_log).pack(anchor="e")

        ctk.CTkLabel(scroll, text="Younds v1.0  ·  yt-dlp",
                     font=FONT_SMALL, text_color="#2A2A2A").pack(pady=(0,16))

    def _set_mode(self, mode):
        self._mode_var.set(mode)
        if mode == "audio":
            self._btn_audio.configure(fg_color=ACCENT, text_color=BG)
            self._btn_video.configure(fg_color="#252525", text_color=TEXT_SUB)
            for b in self._q_btns:
                b.configure(state="normal")
            self._set_quality(self._quality_var.get())
        else:
            self._btn_video.configure(fg_color=ACCENT, text_color=BG)
            self._btn_audio.configure(fg_color="#252525", text_color=TEXT_SUB)
            for b in self._q_btns:
                b.configure(state="disabled", fg_color="#1A1A1A", text_color=TEXT_MUTED)

    def _set_quality(self, val):
        self._quality_var.set(val)
        for b in self._q_btns:
            if b._q_val == val:
                b.configure(fg_color=ACCENT, text_color=BG)
            else:
                b.configure(fg_color="#252525", text_color=TEXT_SUB)

    def _pick_folder(self):
        p = filedialog.askdirectory(title="Folder ieșire")
        if p: self._folder_var.set(p)

    def _pick_ffmpeg(self):
        p = filedialog.askopenfilename(title="ffmpeg",
            filetypes=[("FFmpeg", "ffmpeg ffmpeg.exe"), ("Toate", "*")])
        if p: self._ffmpeg_var.set(p)

    def _pick_cookies(self):
        p = filedialog.askopenfilename(title="Cookies",
            filetypes=[("Text", "*.txt"), ("Toate", "*")])
        if p: self._cookies_var.set(p)

    def _log(self, msg, color=TEXT_SUB):
        def _w():
            self._log_box.configure(state="normal")
            self._log_box.insert("end", msg + "\n")
            self._log_box.see("end")
            self._log_box.configure(state="disabled")
        self.after(0, _w)

    def _clear_log(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")

    def _set_progress(self, val):
        self.after(0, lambda: self._progress_var.set(val / 100))

    def _set_status(self, msg, color=TEXT_MUTED):
        self.after(0, lambda: self._status_lbl.configure(text=msg, text_color=color))

    def _start(self):
        if self._downloading: return
        urls = [u.strip() for u in self._url_box.get("1.0", "end").strip().splitlines() if u.strip()]
        if not urls:
            messagebox.showwarning("Younds", "Adaugă cel puțin un link!"); return
        output_dir = self._folder_var.get().strip()
        if not output_dir:
            messagebox.showwarning("Younds", "Alege un folder de ieșire."); return
        try:
            start_idx = int(self._index_var.get().strip())
        except ValueError:
            start_idx = 0
        os.makedirs(output_dir, exist_ok=True)
        self._downloading = True
        self._dl_btn.configure(state="disabled", text="Se descarcă…")
        self._cancel_btn.configure(state="normal")
        self._progress_var.set(0)
        self._set_status("Descărcare în curs…", WARN)
        self._log(f"▶  {len(urls)} link(uri)  →  {output_dir}", ACCENT)

        dl = Downloader(self._log, self._set_progress, self._on_done)
        threading.Thread(target=dl.download, kwargs=dict(
            urls=urls, output_dir=output_dir, mode=self._mode_var.get(),
            quality=self._quality_var.get(), start_index=start_idx,
            ffmpeg_path=self._ffmpeg_var.get().strip(),
            cookies_file=self._cookies_var.get().strip() or None,
        ), daemon=True).start()

    def _cancel(self):
        self._log("⚠  Oprire solicitată…", WARN)
        self._on_done(False)

    def _on_done(self, success):
        def _f():
            self._downloading = False
            self._dl_btn.configure(state="normal", text="↓   DESCARCĂ")
            self._cancel_btn.configure(state="disabled")
            if success:
                self._progress_var.set(1)
                self._set_status("✓  Descărcare finalizată!", SUCCESS)
                self._log("✓  Gata!", SUCCESS)
            else:
                self._set_status("⚠  Oprită / eroare.", ERROR)
        self.after(0, _f)


if __name__ == "__main__":
    app = YoundsApp()
    app.mainloop()