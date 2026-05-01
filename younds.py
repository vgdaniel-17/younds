"""
Younds — Music & Video Downloader
"""

import os
import re
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from yt_dlp import YoutubeDL

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG      = "#0A0A0A"
SURF    = "#141414"
SURF2   = "#1E1E1E"
BORDER  = "#272727"
BORDER2 = "#333333"
ACCENT  = "#C8FF00"
ACCENT2 = "#9BBF00"
TEXT    = "#F0F0F0"
TEXT2   = "#888888"
TEXT3   = "#444444"
ERROR   = "#FF453A"
WARN    = "#FF9F0A"

F       = ("Segoe UI", 13)
F_B     = ("Segoe UI", 13, "bold")
F_SM    = ("Segoe UI", 11)
F_XS    = ("Segoe UI", 10)
F_XS_B  = ("Segoe UI", 10, "bold")
F_MONO  = ("Consolas", 11)
F_LOGO  = ("Segoe UI", 22, "bold")


# ── Reusable components ──────────────────────────────────────────────────────

class Card(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=SURF, corner_radius=12,
                         border_width=1, border_color=BORDER, **kw)

    def inner(self, padx=20, pady=16):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=padx, pady=pady)
        return f


def label(master, text, font=F_XS, color=TEXT3, **kw):
    return ctk.CTkLabel(master, text=text, font=font, text_color=color, **kw)


def small_entry(master, var, mono=False, placeholder="", **kw):
    return ctk.CTkEntry(
        master, textvariable=var,
        fg_color=BG, border_color=BORDER, border_width=1,
        corner_radius=8, text_color=TEXT,
        font=F_MONO if mono else F_SM,
        height=36,
        placeholder_text=placeholder,
        placeholder_text_color=TEXT3,
        **kw,
    )


def browse_btn(master, text="Browse", cmd=None):
    return ctk.CTkButton(
        master, text=text, font=F_XS, height=36, width=70,
        fg_color=SURF2, text_color=TEXT2, hover_color=BORDER2,
        corner_radius=8, command=cmd,
    )


# ── Download logic ───────────────────────────────────────────────────────────

class Downloader:
    def __init__(self, on_progress, on_converting, on_log, on_done):
        self._on_progress   = on_progress
        self._on_converting = on_converting
        self._on_log        = on_log
        self._on_done       = on_done

    def _hook(self):
        def h(d):
            if d["status"] == "downloading":
                raw = re.sub(r"\x1b\[[0-9;]*m", "", d.get("_percent_str", "0%")).strip()
                try:
                    pct = float(raw.replace("%", ""))
                except Exception:
                    pct = 0
                title = d.get("info_dict", {}).get("title", "")
                spd = re.sub(r"\x1b\[[0-9;]*m", "", d.get("_speed_str", "")).strip()
                eta = re.sub(r"\x1b\[[0-9;]*m", "", d.get("_eta_str", "")).strip()
                self._on_progress(pct, title, spd, eta)
                self._on_log(f"  {raw}  ·  {spd}  ·  ETA {eta}")
            elif d["status"] == "finished":
                self._on_converting()
                self._on_log("  ✓ Downloaded, processing…")
        return h

    def download(self, urls, output_dir, mode, quality, start_index,
                 ffmpeg_path, cookies_file):
        outtmpl = os.path.join(
            output_dir,
            "%(autonumber)d - %(title)s.%(ext)s" if start_index > 0
            else "%(title)s.%(ext)s",
        )
        if mode == "audio":
            opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [{"key": "FFmpegExtractAudio",
                                    "preferredcodec": "mp3",
                                    "preferredquality": quality}],
            }
        else:
            opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [{"key": "FFmpegVideoConvertor",
                                    "preferedformat": "mp4"}],
                "merge_output_format": "mp4",
            }
        opts.update({"quiet": True, "no_warnings": True,
                     "ignoreerrors": True, "progress_hooks": [self._hook()]})
        if start_index > 0:
            opts["autonumber_start"] = start_index
        if ffmpeg_path:
            p = ffmpeg_path.strip()
            opts["ffmpeg_location"] = os.path.dirname(p) if os.path.isfile(p) else p
        if cookies_file and os.path.isfile(cookies_file):
            opts["cookiefile"] = cookies_file

        try:
            with YoutubeDL(opts) as ydl:
                ydl.download(urls)
            files = sorted(f for f in os.listdir(output_dir)
                           if os.path.isfile(os.path.join(output_dir, f)))
            self._on_done(True, files)
        except Exception as e:
            self._on_log(f"  ✗ {e}")
            self._on_done(False, [])


# ── Main window ──────────────────────────────────────────────────────────────

class YoundsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Younds")
        self.geometry("600x840")
        self.minsize(520, 640)
        self.configure(fg_color=BG)

        self._mode        = "audio"
        self._quality     = "320"
        self._q_btns: dict = {}
        self._downloading = False
        self._adv_open    = False
        self._log_open    = False
        self._log_count   = 0
        self._files_shown = False
        self._url_has_placeholder = True

        self._build()

    # ── Build UI ─────────────────────────────────────────────────────────────

    def _build(self):
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=BG, corner_radius=0,
            scrollbar_button_color=SURF2,
            scrollbar_button_hover_color=BORDER2,
        )
        scroll.pack(fill="both", expand=True)
        self._scroll = scroll
        self.bind_all("<Button-4>", lambda e: scroll._parent_canvas.yview_scroll(-1, "units"))
        self.bind_all("<Button-5>", lambda e: scroll._parent_canvas.yview_scroll( 1, "units"))

        PAD = dict(padx=20, pady=(0, 10))

        # Header
        hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(32, 28))
        logo_row = ctk.CTkFrame(hdr, fg_color="transparent")
        logo_row.pack(anchor="w")
        ctk.CTkLabel(logo_row, text="YOU", font=F_LOGO, text_color=TEXT).pack(side="left")
        ctk.CTkLabel(logo_row, text="NDS", font=F_LOGO, text_color=ACCENT).pack(side="left")
        label(hdr, "downloader").pack(anchor="w", pady=(3, 0))

        # URL
        url_card = Card(scroll)
        url_card.pack(fill="x", **PAD)
        ui = url_card.inner()

        self._url_box = ctk.CTkTextbox(
            ui, height=110, font=F_MONO,
            fg_color=BG, border_color=BORDER, border_width=1,
            corner_radius=8, text_color=TEXT3, wrap="word",
            scrollbar_button_color=BORDER,
        )
        self._url_box.pack(fill="x")
        self._url_placeholder = (
            "Paste links here — one per line\n\n"
            "https://youtube.com/watch?v=...\n"
            "https://youtube.com/playlist?list=..."
        )
        self._url_box.insert("1.0", self._url_placeholder)
        self._url_box.bind("<FocusIn>",  self._url_focus_in)
        self._url_box.bind("<FocusOut>", self._url_focus_out)

        hint = ctk.CTkFrame(ui, fg_color="transparent")
        hint.pack(fill="x", pady=(8, 0))
        for t in ["YouTube", "Facebook", "Playlists", "One link per line"]:
            label(hint, f"·  {t}").pack(side="left", padx=(0, 10))

        # Format
        fmt_card = Card(scroll)
        fmt_card.pack(fill="x", **PAD)
        fi = fmt_card.inner(pady=(14, 16))

        label(fi, "FORMAT", font=F_XS_B).pack(anchor="w", pady=(0, 10))

        toggle = ctk.CTkFrame(fi, fg_color="transparent")
        toggle.pack(fill="x", pady=(0, 10))
        toggle.columnconfigure((0, 1), weight=1)

        self._btn_audio = ctk.CTkButton(
            toggle, text="♪   MP3 Audio", font=F_B, height=42,
            corner_radius=8, fg_color=ACCENT, text_color=BG, hover_color=ACCENT2,
            command=lambda: self._set_mode("audio"),
        )
        self._btn_audio.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self._btn_video = ctk.CTkButton(
            toggle, text="▶   MP4 Video", font=F_B, height=42,
            corner_radius=8, fg_color=SURF2, text_color=TEXT2, hover_color=BORDER2,
            command=lambda: self._set_mode("video"),
        )
        self._btn_video.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        q_row = ctk.CTkFrame(fi, fg_color="transparent")
        q_row.pack(fill="x")
        label(q_row, "Quality", color=TEXT2).pack(side="left", padx=(0, 10))
        for q in ["128", "192", "256", "320"]:
            active = q == "320"
            btn = ctk.CTkButton(
                q_row, text=f"{q}k", font=F_XS, height=28, width=54,
                corner_radius=14,
                fg_color=ACCENT if active else SURF2,
                text_color=BG if active else TEXT2,
                hover_color=ACCENT2 if active else BORDER2,
                command=lambda v=q: self._set_quality(v),
            )
            btn.pack(side="left", padx=(0, 6))
            self._q_btns[q] = btn

        # Advanced (collapsible)
        adv_card = Card(scroll)
        adv_card.pack(fill="x", **PAD)
        adv_top = ctk.CTkFrame(adv_card, fg_color="transparent")
        adv_top.pack(fill="x", padx=20, pady=14)

        self._adv_btn = ctk.CTkButton(
            adv_top, text="▶   Advanced settings", font=F_XS,
            fg_color=SURF, text_color=TEXT3,
            hover_color=SURF, anchor="w",
            height=20, command=self._toggle_adv,
        )
        self._adv_btn.pack(anchor="w")

        self._adv_frame = ctk.CTkFrame(adv_card, fg_color="transparent")
        ai = ctk.CTkFrame(self._adv_frame, fg_color="transparent")
        ai.pack(fill="x", padx=20, pady=(0, 16))

        label(ai, "FFmpeg", color=TEXT2).pack(anchor="w", pady=(0, 5))
        ff_row = ctk.CTkFrame(ai, fg_color="transparent")
        ff_row.pack(fill="x", pady=(0, 12))
        self._ffmpeg_var = ctk.StringVar(value="/usr/bin/ffmpeg")
        small_entry(ff_row, self._ffmpeg_var, mono=True).pack(side="left", fill="x", expand=True, padx=(0, 8))
        browse_btn(ff_row, cmd=self._pick_ffmpeg).pack(side="left")

        label(ai, "Cookies (optional)", color=TEXT2).pack(anchor="w", pady=(0, 5))
        ck_row = ctk.CTkFrame(ai, fg_color="transparent")
        ck_row.pack(fill="x", pady=(0, 12))
        self._cookies_var = ctk.StringVar(value="")
        small_entry(ck_row, self._cookies_var, placeholder="Leave empty if not needed").pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        browse_btn(ck_row, cmd=self._pick_cookies).pack(side="left")

        label(ai, "Numbering start index", color=TEXT2).pack(anchor="w", pady=(0, 5))
        idx_row = ctk.CTkFrame(ai, fg_color="transparent")
        idx_row.pack(fill="x", pady=(0, 12))
        self._index_var = ctk.StringVar(value="0")
        small_entry(idx_row, self._index_var, width=80).pack(side="left")
        label(idx_row, '  0 = no number  ·  12 → "12 - Title.mp3"…').pack(side="left")

        label(ai, "Output folder", color=TEXT2).pack(anchor="w", pady=(0, 5))
        out_row = ctk.CTkFrame(ai, fg_color="transparent")
        out_row.pack(fill="x")
        self._folder_var = ctk.StringVar(value=os.path.expanduser("~/Music/Younds"))
        small_entry(out_row, self._folder_var, mono=True).pack(side="left", fill="x", expand=True, padx=(0, 8))
        browse_btn(out_row, cmd=self._pick_folder).pack(side="left")

        # Download button
        btn_f = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_f.pack(fill="x", padx=20, pady=(0, 10))
        self._dl_btn = ctk.CTkButton(
            btn_f, text="↓   Download", font=("Segoe UI", 15, "bold"),
            height=52, corner_radius=12,
            fg_color=ACCENT, text_color=BG, hover_color=ACCENT2,
            command=self._start,
        )
        self._dl_btn.pack(fill="x")

        # Progress card
        self._prog_card = Card(scroll)
        self._prog_card.pack(fill="x", padx=20, pady=(0, 10))
        pi = self._prog_card.inner()

        self._prog_title = ctk.CTkLabel(pi, text="Ready to download.",
                                        font=F_SM, text_color=TEXT3, anchor="w")
        self._prog_title.pack(fill="x", pady=(0, 10))

        self._prog_bar = ctk.CTkProgressBar(
            pi, height=4, corner_radius=2,
            fg_color=SURF2, progress_color=ACCENT,
        )
        self._prog_bar.set(0)
        self._prog_bar.pack(fill="x", pady=(0, 8))

        meta = ctk.CTkFrame(pi, fg_color="transparent")
        meta.pack(fill="x")
        self._pct_lbl = label(meta, "")
        self._pct_lbl.pack(side="left")
        self._spd_lbl = label(meta, "")
        self._spd_lbl.pack(side="left", padx=16)
        self._eta_lbl = label(meta, "")
        self._eta_lbl.pack(side="left")

        self._status_lbl = ctk.CTkLabel(pi, text="", font=F_SM,
                                        text_color=TEXT2, anchor="w")
        self._status_lbl.pack(fill="x", pady=(8, 0))

        # Files card (shown after download)
        self._files_card = Card(scroll)
        self._files_list = ctk.CTkFrame(
            ctk.CTkFrame(self._files_card, fg_color="transparent"),
            fg_color="transparent",
        )
        self._files_list.master.pack(fill="x", padx=20, pady=(14, 16))
        label(self._files_list.master, "DOWNLOADED FILES", font=F_XS_B).pack(anchor="w", pady=(0, 10))
        self._files_list.pack(fill="x")

        # Log card (collapsible)
        self._log_card = Card(scroll)
        self._log_card.pack(fill="x", padx=20, pady=(0, 12))

        log_top = ctk.CTkFrame(self._log_card, fg_color="transparent")
        log_top.pack(fill="x", padx=20, pady=14)
        self._log_btn = ctk.CTkButton(
            log_top, text="▶   Log", font=F_XS,
            fg_color=SURF, text_color=TEXT3,
            hover_color=SURF, anchor="w",
            height=20, command=self._toggle_log,
        )
        self._log_btn.pack(side="left")
        self._log_count_lbl = label(log_top, "")
        self._log_count_lbl.pack(side="right")

        self._log_frame = ctk.CTkFrame(self._log_card, fg_color="transparent")
        li = ctk.CTkFrame(self._log_frame, fg_color="transparent")
        li.pack(fill="x", padx=20, pady=(0, 14))
        self._log_box = ctk.CTkTextbox(
            li, height=140, font=F_MONO,
            fg_color=BG, border_color=BORDER, border_width=1,
            corner_radius=8, text_color=TEXT3, state="disabled",
            wrap="word", scrollbar_button_color=BORDER,
        )
        self._log_box.pack(fill="x")
        ctk.CTkButton(
            li, text="Clear", width=68, height=22, corner_radius=6,
            font=F_XS, fg_color=SURF2, hover_color=BORDER2, text_color=TEXT3,
            command=self._clear_log,
        ).pack(anchor="e", pady=(6, 0))

        label(scroll, "Younds v2.0  ·  yt-dlp").pack(pady=(0, 24))

    # ── URL placeholder ──────────────────────────────────────────────────────

    def _url_focus_in(self, _):
        if self._url_has_placeholder:
            self._url_box.delete("1.0", "end")
            self._url_box.configure(text_color=TEXT)
            self._url_has_placeholder = False

    def _url_focus_out(self, _):
        if not self._url_box.get("1.0", "end").strip():
            self._url_box.insert("1.0", self._url_placeholder)
            self._url_box.configure(text_color=TEXT3)
            self._url_has_placeholder = True

    # ── Mode / Quality ───────────────────────────────────────────────────────

    def _set_mode(self, m):
        self._mode = m
        if m == "audio":
            self._btn_audio.configure(fg_color=ACCENT, text_color=BG)
            self._btn_video.configure(fg_color=SURF2, text_color=TEXT2)
            for btn in self._q_btns.values():
                btn.configure(state="normal")
            self._set_quality(self._quality)
        else:
            self._btn_video.configure(fg_color=ACCENT, text_color=BG)
            self._btn_audio.configure(fg_color=SURF2, text_color=TEXT2)
            for btn in self._q_btns.values():
                btn.configure(state="disabled", fg_color=SURF2, text_color=TEXT3)

    def _set_quality(self, q):
        self._quality = q
        for val, btn in self._q_btns.items():
            btn.configure(
                fg_color=ACCENT if val == q else SURF2,
                text_color=BG if val == q else TEXT2,
            )

    # ── Collapsibles ─────────────────────────────────────────────────────────

    def _toggle_adv(self):
        self._adv_open = not self._adv_open
        arrow = "▼" if self._adv_open else "▶"
        self._adv_btn.configure(text=f"{arrow}   Advanced settings")
        if self._adv_open:
            self._adv_frame.pack(fill="x")
        else:
            self._adv_frame.pack_forget()

    def _toggle_log(self):
        self._log_open = not self._log_open
        arrow = "▼" if self._log_open else "▶"
        self._log_btn.configure(text=f"{arrow}   Log")
        if self._log_open:
            self._log_frame.pack(fill="x")
        else:
            self._log_frame.pack_forget()

    # ── File pickers ─────────────────────────────────────────────────────────

    def _pick_folder(self):
        p = filedialog.askdirectory(title="Output folder")
        if p: self._folder_var.set(p)

    def _pick_ffmpeg(self):
        p = filedialog.askopenfilename(
            title="FFmpeg executable",
            filetypes=[("FFmpeg", "ffmpeg ffmpeg.exe"), ("All files", "*")],
        )
        if p: self._ffmpeg_var.set(p)

    def _pick_cookies(self):
        p = filedialog.askopenfilename(
            title="Cookies file",
            filetypes=[("Text files", "*.txt"), ("All files", "*")],
        )
        if p: self._cookies_var.set(p)

    # ── Logging ──────────────────────────────────────────────────────────────

    def _log(self, msg):
        def _w():
            self._log_box.configure(state="normal")
            self._log_box.insert("end", msg + "\n")
            self._log_box.see("end")
            self._log_box.configure(state="disabled")
            self._log_count += 1
            self._log_count_lbl.configure(text=f"{self._log_count}")
        self.after(0, _w)

    def _clear_log(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")
        self._log_count = 0
        self._log_count_lbl.configure(text="")

    # ── Progress ─────────────────────────────────────────────────────────────

    def _on_progress(self, pct, title, spd, eta):
        def _u():
            self._prog_bar.set(pct / 100)
            if title: self._prog_title.configure(text=title, text_color=TEXT2)
            self._pct_lbl.configure(text=f"{pct:.0f}%")
            if spd: self._spd_lbl.configure(text=spd)
            if eta: self._eta_lbl.configure(text=f"ETA {eta}")
        self.after(0, _u)

    def _on_converting(self):
        self.after(0, lambda: self._status_lbl.configure(
            text="Converting…", text_color=WARN))

    def _set_status(self, msg, color=TEXT2):
        self.after(0, lambda: self._status_lbl.configure(text=msg, text_color=color))

    # ── Start / Done ─────────────────────────────────────────────────────────

    def _start(self):
        if self._downloading:
            return
        raw = self._url_box.get("1.0", "end").strip()
        if not raw or self._url_has_placeholder:
            self._url_box.focus()
            return
        urls = [u for u in raw.splitlines() if u.strip()]
        if not urls:
            return

        output_dir = self._folder_var.get().strip()
        if not output_dir:
            messagebox.showwarning("Younds", "Please select an output folder.")
            return
        try:
            start_idx = int(self._index_var.get().strip())
        except ValueError:
            start_idx = 0

        os.makedirs(output_dir, exist_ok=True)
        self._downloading = True
        self._dl_btn.configure(state="disabled", text="Downloading…",
                                fg_color=SURF2, text_color=TEXT2)
        self._prog_bar.set(0)
        self._prog_title.configure(text="Preparing…", text_color=TEXT2)
        self._pct_lbl.configure(text="")
        self._spd_lbl.configure(text="")
        self._eta_lbl.configure(text="")
        self._status_lbl.configure(text="Downloading…", text_color=WARN)
        self._log(f"▶  {len(urls)} link(s)  →  {output_dir}")

        dl = Downloader(self._on_progress, self._on_converting, self._log, self._on_done)
        threading.Thread(
            target=dl.download,
            kwargs=dict(
                urls=urls, output_dir=output_dir, mode=self._mode,
                quality=self._quality, start_index=start_idx,
                ffmpeg_path=self._ffmpeg_var.get().strip(),
                cookies_file=self._cookies_var.get().strip() or None,
            ),
            daemon=True,
        ).start()

    def _on_done(self, success, files):
        def _f():
            self._downloading = False
            self._dl_btn.configure(state="normal", text="↓   Download",
                                    fg_color=ACCENT, text_color=BG)
            if success:
                self._prog_bar.set(1)
                self._set_status(f"✓  Done!  {len(files)} file(s) downloaded.", ACCENT)
                self._log(f"✓  Done! {len(files)} file(s).")
                if files:
                    self._show_files(files)
            else:
                self._set_status("⚠  Error or cancelled.", ERROR)
        self.after(0, _f)

    def _show_files(self, files):
        for w in self._files_list.winfo_children():
            w.destroy()

        output_dir = self._folder_var.get().strip()
        for fname in files:
            row = ctk.CTkFrame(self._files_list, fg_color=SURF2,
                               corner_radius=8, border_width=1, border_color=BORDER)
            row.pack(fill="x", pady=(0, 6))
            ctk.CTkLabel(row, text=fname, font=F_SM, text_color=TEXT,
                         anchor="w").pack(side="left", padx=12, pady=10,
                                          fill="x", expand=True)
            full = os.path.join(output_dir, fname)
            ctk.CTkButton(
                row, text="Open", font=F_XS, height=28, width=68,
                fg_color=SURF2, text_color=ACCENT,
                hover_color=BORDER2, corner_radius=6,
                command=lambda p=full: self._open_file(p),
            ).pack(side="right", padx=8)

        if not self._files_shown:
            self._files_card.pack(fill="x", padx=20, pady=(0, 10),
                                   before=self._log_card)
            self._files_shown = True

    @staticmethod
    def _open_file(path):
        if os.name == "nt":
            os.startfile(path)
        else:
            os.system(f'xdg-open "{path}"')


if __name__ == "__main__":
    app = YoundsApp()
    app.mainloop()
