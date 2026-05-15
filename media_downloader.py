import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import subprocess
import sys
import yt_dlp
import os
import requests
import re
from PIL import Image, ImageTk
from io import BytesIO
import json
import time

# Appearance settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Constants & Colors
COLORS = {
    "bg": "#121212",
    "card": "#1E1E1E",
    "accent": "#3B82F6",
    "accent_hover": "#2563EB",
    "success": "#10B981",
    "success_hover": "#059669",
    "danger": "#EF4444",
    "danger_hover": "#DC2626",
    "text": "#F3F4F6",
    "text_muted": "#9CA3AF",
    "border": "#374151",
    "entry_bg": "#262626"
}

class MediaDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Media Downloader")
        self.geometry("700x780") # Reduced height
        self.configure(fg_color=COLORS["bg"])
        
        # Variables
        self.url_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready to download")
        self.progress_pct = tk.StringVar(value="0%")
        self.progress_meta = tk.StringVar(value="")
        self.selected_qual = tk.StringVar(value="1080p")
        self.download_path = self._get_default_download_path()
        self.history_file = "download_history.json"
        self.download_history = self.load_history()
        
        # Internal state
        self._last_fetched_url = ""
        self._thumb_img = None
        self._is_downloading = False
        
        # UI Setup
        self.setup_ui()
        
        # Trace URL changes
        self.url_var.trace_add("write", self._on_url_changed)

    def _get_default_download_path(self):
        return os.path.join(os.path.expanduser("~"), "Downloads")

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))
        
        title_label = ctk.CTkLabel(header, text="Media Downloader", 
                                  font=ctk.CTkFont(size=20, weight="bold"),
                                  text_color=COLORS["text"])
        title_label.pack(side="left")

        # Tab System
        self.tab_view = ctk.CTkTabview(self, fg_color=COLORS["card"], 
                                      segmented_button_selected_color=COLORS["accent"],
                                      segmented_button_unselected_hover_color=COLORS["accent_hover"],
                                      corner_radius=10)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        self.tab_download = self.tab_view.add("Download")
        self.tab_library = self.tab_view.add("Library")
        
        self._build_download_tab()
        self._build_library_tab()

    def _build_download_tab(self):
        # Removed ScrollableFrame to ensure all elements are visible at once
        container = ctk.CTkFrame(self.tab_download, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=5)
        
        # URL Input Section
        ctk.CTkLabel(container, text="Video or Audio URL", 
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_muted"]).pack(anchor="w", pady=(2, 2))
        
        url_frame = ctk.CTkFrame(container, fg_color="transparent")
        url_frame.pack(fill="x", pady=(0, 10))
        
        self.url_entry = ctk.CTkEntry(url_frame, textvariable=self.url_var,
                                     placeholder_text="Paste link here...",
                                     height=36, corner_radius=6,
                                     fg_color=COLORS["entry_bg"], 
                                     border_color=COLORS["border"],
                                     text_color=COLORS["text"])
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        paste_btn = ctk.CTkButton(url_frame, text="Paste", width=70, height=36,
                                 fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                                 font=ctk.CTkFont(size=11, weight="bold"),
                                 command=self.paste_url)
        paste_btn.pack(side="left")

        # Preview Area - More compact
        self.preview_card = ctk.CTkFrame(container, fg_color=COLORS["entry_bg"], 
                                        corner_radius=8, border_width=1, 
                                        border_color=COLORS["border"])
        self.preview_card.pack(fill="x", pady=(0, 12))
        
        self.thumb_label = ctk.CTkLabel(self.preview_card, text="Preview",
                                       font=ctk.CTkFont(size=11),
                                       text_color=COLORS["text_muted"], height=140)
        self.thumb_label.pack(expand=True, fill="both", padx=5, pady=5)

        # Quality Selection - Tighter padding
        ctk.CTkLabel(container, text="Quality", 
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, 5))
        
        qual_frame = ctk.CTkFrame(container, fg_color="transparent")
        qual_frame.pack(fill="x", pady=(0, 15))
        
        qualities = [("360p", "360p"), ("480p", "480p"), ("720p", "720p"), ("1080p", "1080p"), ("MP3", "audio")]
        self.qual_btns = {}
        
        for i, (label, val) in enumerate(qualities):
            btn = ctk.CTkButton(qual_frame, text=label, width=55, height=28,
                               fg_color=COLORS["card"], border_width=1,
                               border_color=COLORS["border"],
                               text_color=COLORS["text"],
                               font=ctk.CTkFont(size=11),
                               hover_color=COLORS["accent"],
                               command=lambda v=val: self.select_quality(v))
            btn.pack(side="left", padx=(0 if i==0 else 3, 0))
            self.qual_btns[val] = btn
        
        self.select_quality("1080p")

        # Progress & Status Display
        progress_info_frame = ctk.CTkFrame(container, fg_color="transparent")
        progress_info_frame.pack(fill="x", pady=(0, 2))
        
        self.status_label = ctk.CTkLabel(progress_info_frame, textvariable=self.status_var,
                                         font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"])
        self.status_label.pack(side="left")
        
        self.pct_label = ctk.CTkLabel(progress_info_frame, textvariable=self.progress_pct,
                                      font=ctk.CTkFont(size=11, weight="bold"), text_color=COLORS["accent"])
        self.pct_label.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(container, height=6, corner_radius=3,
                                               progress_color=COLORS["accent"], fg_color=COLORS["border"])
        self.progress_bar.pack(fill="x", pady=(0, 2))
        self.progress_bar.set(0)
        
        self.meta_label = ctk.CTkLabel(container, textvariable=self.progress_meta,
                                       font=ctk.CTkFont(size=10), text_color=COLORS["text_muted"])
        self.meta_label.pack(anchor="e", pady=(0, 12))

        # Action Buttons
        action_frame = ctk.CTkFrame(container, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 5))
        
        self.download_btn = ctk.CTkButton(action_frame, text="Download Now", height=40,
                                          corner_radius=8, fg_color=COLORS["success"],
                                          hover_color=COLORS["success_hover"],
                                          font=ctk.CTkFont(size=13, weight="bold"),
                                          command=self.start_download)
        self.download_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        self.folder_btn = ctk.CTkButton(action_frame, text="Folder", width=80, height=40,
                                       corner_radius=8, fg_color=COLORS["card"],
                                       border_width=1, border_color=COLORS["border"],
                                       font=ctk.CTkFont(size=12),
                                       command=self.choose_folder)
        self.folder_btn.pack(side="left")

    def _build_library_tab(self):
        self.lib_container = ctk.CTkFrame(self.tab_library, fg_color="transparent")
        self.lib_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.lib_scroll = ctk.CTkScrollableFrame(self.lib_container, fg_color="transparent")
        self.lib_scroll.pack(fill="both", expand=True)
        
        self.refresh_library()

    def select_quality(self, val):
        self.selected_qual.set(val)
        for k, btn in self.qual_btns.items():
            if k == val:
                btn.configure(fg_color=COLORS["accent"], border_color=COLORS["accent"])
            else:
                btn.configure(fg_color=COLORS["card"], border_color=COLORS["border"])

    def _on_url_changed(self, *_):
        url = self.url_var.get().strip()
        if not url:
            self.thumb_label.configure(image="", text="Preview", height=140)
            self._thumb_img = None
            return
            
        if url != self._last_fetched_url:
            if hasattr(self, "_fetch_timer"):
                self.after_cancel(self._fetch_timer)
            self._fetch_timer = self.after(500, self.fetch_info)

    def paste_url(self):
        try:
            clipboard = self.clipboard_get()
            self.url_var.set(clipboard)
        except:
            pass

    def fetch_info(self):
        url = self.url_var.get().strip()
        if not url or url == self._last_fetched_url:
            return
            
        self.status_var.set("Fetching info...")
        threading.Thread(target=self._fetch_thread, args=(url,), daemon=True).start()

    def _is_pinterest_url(self, url):
        return bool(re.search(r'(pinterest\.[a-z]+|pin\.it)', url, re.IGNORECASE))

    def _pinterest_opts(self):
        """Extra yt-dlp options required for Pinterest."""
        return {
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/124.0.0.0 Safari/537.36'
                ),
                'Referer': 'https://www.pinterest.com/',
            },
        }

    def _fetch_thread(self, url):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'skip_download': True,
            }
            if self._is_pinterest_url(url):
                ydl_opts.update(self._pinterest_opts())
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                thumb_url = info.get('thumbnail')
                self._last_fetched_url = url
                self.after(0, lambda: self._update_ui_with_info(title, thumb_url))
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self.status_var.set(f"Error: {error_msg[:30]}..."))

    def _update_ui_with_info(self, title, thumb_url):
        self.status_var.set("Ready")
        if thumb_url:
            threading.Thread(target=self._load_thumbnail, args=(thumb_url, title), daemon=True).start()
        else:
            self.thumb_label.configure(text=title, image="", height=140)

    def _load_thumbnail(self, url, title):
        try:
            response = requests.get(url, timeout=10)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            
            # Aspect ratio resize
            target_width = 500
            w, h = img.size
            target_height = int(h * (target_width / w))
            
            # Constrain height strictly
            if target_height > 200:
                target_height = 200
                target_width = int(w * (target_height / h))

            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(target_width, target_height))
            self._thumb_img = ctk_img 
            self.after(0, lambda: self.thumb_label.configure(image=self._thumb_img, text="", height=target_height + 5))
        except:
            self.after(0, lambda: self.thumb_label.configure(text=title, image="", height=140))

    def choose_folder(self):
        path = filedialog.askdirectory(initialdir=self.download_path)
        if path:
            self.download_path = path
            self.status_var.set(f"Folder: {os.path.basename(path)}")

    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a valid URL first.")
            return
        
        if self._is_downloading:
            return

        self._is_downloading = True
        self.download_btn.configure(state="disabled", text="Processing...")
        self.progress_bar.set(0)
        self.progress_pct.set("0%")
        self.progress_meta.set("")
        threading.Thread(target=self._download_thread, args=(url,), daemon=True).start()

    def _download_thread(self, url):
        qual = self.selected_qual.get()
        is_audio = qual == "audio"
        
        if is_audio:
            ydl_format = 'bestaudio/best'
        else:
            height = qual.replace('p', '')
            # Reliable format selection:
            # 1. Try specified resolution (bestvideo[height<=X]+bestaudio)
            # 2. Fallback to any best quality (best) if specific height is unavailable
            ydl_format = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best[height<={height}]/best"

        opts = {
            'format': ydl_format,
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4' if not is_audio else None,
            'ignoreerrors': False,
        }

        # Pinterest: inject browser headers & fall back to best available quality
        if self._is_pinterest_url(url):
            opts.update(self._pinterest_opts())
            if not is_audio:
                # Pinterest pins usually only have one video stream; 'best' is safest
                opts['format'] = f"bestvideo[height<={height}]+bestaudio/best"
        
        if is_audio:
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Downloaded Media')
                self.save_to_history(title, url)
                self.after(0, lambda: self._on_download_finished(True, title))
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self._on_download_finished(False, error_msg))

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                def strip_ansi(text):
                    if not text: return "N/A"
                    return re.sub(r'\x1b\[[0-9;]*m', '', str(text)).strip()

                p_str = strip_ansi(d.get('_percent_str', '0%')).replace('%', '')
                val = float(p_str) / 100
                
                speed = strip_ansi(d.get('_speed_str', 'N/A'))
                eta = strip_ansi(d.get('_eta_str', 'N/A'))
                size = strip_ansi(d.get('_total_bytes_str', d.get('_total_bytes_estimate_str', 'N/A')))
                
                meta = f"Speed: {speed}  |  ETA: {eta}  |  Size: {size}"
                self.after(0, lambda: self._update_progress_ui(val, p_str, meta))
            except:
                pass
        elif d['status'] == 'finished':
            self.after(0, lambda: self.status_var.set("Finalizing..."))
            self.after(0, lambda: self.progress_pct.set("100%"))

    def _update_progress_ui(self, val, pct, meta):
        self.progress_bar.set(val)
        self.progress_pct.set(f"{pct}%")
        self.progress_meta.set(meta)
        self.status_var.set("Downloading...")

    def _on_download_finished(self, success, message):
        self._is_downloading = False
        self.download_btn.configure(state="normal", text="Download Now")
        
        if success:
            self.status_var.set("Complete!")
            self.progress_pct.set("100%")
            self.progress_meta.set("File saved")
            messagebox.showinfo("Success", f"Finished: {message}")
            self.refresh_library()
        else:
            self.status_var.set("Failed")
            self.progress_meta.set("Error occurred")
            messagebox.showerror("Error", f"Download failed:\n{message}")

    def save_to_history(self, title, url):
        entry = {
            "title": title, 
            "url": url, 
            "time": time.strftime("%Y-%m-%d %H:%M"),
            "path": self.download_path
        }
        self.download_history.insert(0, entry)
        self.download_history = self.download_history[:50]
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.download_history, f)
        except:
            pass

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return []

    def refresh_library(self):
        for widget in self.lib_scroll.winfo_children():
            widget.destroy()
            
        if not self.download_history:
            ctk.CTkLabel(self.lib_scroll, text="No history.",
                         font=ctk.CTkFont(size=12, slant="italic"),
                         text_color=COLORS["text_muted"]).pack(pady=30)
            return

        for idx, item in enumerate(self.download_history):
            item_frame = ctk.CTkFrame(self.lib_scroll, fg_color=COLORS["entry_bg"], corner_radius=6)
            item_frame.pack(fill="x", pady=3, padx=5)
            
            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=6)
            
            title = item.get('title', 'Unknown')
            if len(title) > 50: title = title[:47] + "..."
            
            ctk.CTkLabel(info_frame, text=title, font=ctk.CTkFont(size=11, weight="bold"), 
                         text_color=COLORS["text"], anchor="w").pack(fill="x")
            
            meta_text = f"{item.get('time')}  •  {item.get('url', '')[:30]}..."
            ctk.CTkLabel(info_frame, text=meta_text, font=ctk.CTkFont(size=9), 
                         text_color=COLORS["text_muted"], anchor="w").pack(fill="x")
            
            btn_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=5)
            
            ctk.CTkButton(btn_frame, text="Open", width=40, height=22, 
                          fg_color=COLORS["card"], border_width=1, border_color=COLORS["border"],
                          font=ctk.CTkFont(size=10),
                          command=lambda p=item.get('path'): self._open_folder(p)).pack(side="left", padx=2)
                          
            ctk.CTkButton(btn_frame, text="🗑", width=25, height=22, 
                          fg_color="transparent", text_color=COLORS["danger"],
                          hover_color=COLORS["danger_hover"],
                          command=lambda i=idx: self.delete_history_item(i)).pack(side="left")

    def _open_folder(self, path):
        if not path or not os.path.exists(path):
            path = self._get_default_download_path()
            
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except:
            messagebox.showinfo("Folder", f"Files in:\n{path}")

    def delete_history_item(self, idx):
        if idx < len(self.download_history):
            self.download_history.pop(idx)
            try:
                with open(self.history_file, "w") as f:
                    json.dump(self.download_history, f)
            except:
                pass
            self.refresh_library()

if __name__ == "__main__":
    app = MediaDownloader()
    app.mainloop()