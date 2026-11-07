# updater.py
# Auto-update manager for ICDS AutoDesk

import os
import sys
import re
import json
import threading
import tempfile
import subprocess
import urllib.request
import urllib.error
import customtkinter as ctk
from tkinter import messagebox

APP_VERSION = "4.2.0"
GITHUB_REPO = "mnoukhej/ICDS"
RAW_VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/version.json"
API_RELEASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def parse_version(version_str: str):
    """Convert version strings like 'v4.1.0' or '4.1' into tuple of integers (4, 1, 0)"""
    nums = re.findall(r"\d+", str(version_str))
    return tuple(int(n) for n in nums) if nums else (0,)


class ModernUpdateDialog(ctk.CTkToplevel):
    """Modern progress window for downloading installer"""

    def __init__(self, parent, latest_version: str, download_url: str, notes: str):
        super().__init__(parent)
        self.parent = parent
        self.latest_version = latest_version
        self.download_url = download_url
        self.cancelled = False
        self.temp_installer_path = None

        self.title("ICDS AutoDesk Update Manager")
        self.geometry("480x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center over parent
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        cx = px + max(0, (pw - 480) // 2)
        cy = py + max(0, (ph - 280) // 2)
        self.geometry(f"+{cx}+{cy}")

        container = ctk.CTkFrame(self, corner_radius=12, fg_color=("gray95", "gray14"))
        container.pack(fill="both", expand=True, padx=16, pady=16)

        title_lbl = ctk.CTkLabel(
            container,
            text=f"Downloading Update (v{self.latest_version})",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        title_lbl.pack(anchor="w", padx=16, pady=(16, 4))

        sub_lbl = ctk.CTkLabel(
            container,
            text="Downloading package from GitHub CDN servers...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("gray45", "gray65")
        )
        sub_lbl.pack(anchor="w", padx=16, pady=(0, 16))

        self.progress = ctk.CTkProgressBar(container, height=12, corner_radius=6)
        self.progress.pack(fill="x", padx=16, pady=(0, 8))
        self.progress.set(0)

        self.status_lbl = ctk.CTkLabel(
            container,
            text="Connecting to repository...",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.status_lbl.pack(anchor="w", padx=16, pady=(0, 16))

        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(fill="x", padx=16, pady=(0, 12))

        self.cancel_btn = ctk.CTkButton(
            btn_box,
            text="Cancel",
            width=100,
            fg_color=("gray75", "gray25"),
            hover_color=("gray65", "gray35"),
            text_color=("gray10", "gray90"),
            command=self._on_cancel
        )
        self.cancel_btn.pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        threading.Thread(target=self._download_worker, daemon=True).start()

    def _on_cancel(self):
        self.cancelled = True
        self.status_lbl.configure(text="Cancelling download...")
        if self.temp_installer_path and os.path.exists(self.temp_installer_path):
            try:
                os.remove(self.temp_installer_path)
            except Exception:
                pass
        self.destroy()

    def _download_worker(self):
        try:
            temp_dir = tempfile.gettempdir()
            filename = f"ICDSAutoDesk_Setup_v{self.latest_version}.exe"
            self.temp_installer_path = os.path.join(temp_dir, filename)

            headers = {"User-Agent": "ICDSAutoDesk-Updater"}
            req = urllib.request.Request(self.download_url, headers=headers)

            with urllib.request.urlopen(req, timeout=30) as resp:
                total_bytes = int(resp.headers.get("content-length", 0))
                downloaded = 0
                chunk_size = 64 * 1024

                with open(self.temp_installer_path, "wb") as f:
                    while not self.cancelled:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_bytes > 0:
                            ratio = downloaded / total_bytes
                            percent = int(ratio * 100)
                            mb_down = downloaded / (1024 * 1024)
                            mb_total = total_bytes / (1024 * 1024)
                            text = f"Downloaded {mb_down:.1f} MB of {mb_total:.1f} MB ({percent}%)"
                            self.after(0, self._update_ui, ratio, text)
                        else:
                            mb_down = downloaded / (1024 * 1024)
                            text = f"Downloaded {mb_down:.1f} MB"
                            self.after(0, self._update_ui, 0.5, text)

            if self.cancelled:
                return

            self.after(0, self._on_download_complete)

        except Exception as e:
            if not self.cancelled:
                self.after(0, self._on_download_error, str(e))

    def _update_ui(self, ratio: float, text: str):
        if not self.cancelled and self.winfo_exists():
            self.progress.set(ratio)
            self.status_lbl.configure(text=text)

    def _on_download_error(self, err_msg: str):
        messagebox.showerror(
            "Download Error",
            f"Failed to download update:\n{err_msg}\nPlease try again later or visit GitHub.",
            parent=self
        )
        self.destroy()

    def _on_download_complete(self):
        self.status_lbl.configure(text="Download complete! Launching installer...")
        self.update()

        try:
            subprocess.Popen(
                [self.temp_installer_path, "/CLOSEAPPLICATIONS"],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
            )
            self.parent.destroy()
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to run installer:\n{e}", parent=self)
            self.destroy()


def fetch_latest_release_info():
    """
    Fetch latest release info.
    Primary: raw version.json (no rate limits).
    Fallback: GitHub Releases API.
    """
    headers = {"User-Agent": "ICDSAutoDesk-App"}

    # 1. Try raw version.json
    try:
        req = urllib.request.Request(RAW_VERSION_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            ver = data.get("version", "").lstrip("v")
            url = data.get("download_url", "")
            notes = data.get("changelog", "Performance improvements and bug fixes.")
            if ver and url:
                return ver, url, notes
    except Exception:
        pass

    # 2. Fallback to GitHub Releases API
    try:
        req = urllib.request.Request(API_RELEASE_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            tag = data.get("tag_name", "").lstrip("v")
            notes = data.get("body", "Performance improvements and bug fixes.")

            download_url = None
            for asset in data.get("assets", []):
                name = asset.get("name", "").lower()
                if name.endswith(".exe"):
                    download_url = asset.get("browser_download_url")
                    if "setup" in name:
                        break

            if not download_url:
                download_url = f"https://github.com/{GITHUB_REPO}/releases/latest/download/ICDSAutoDesk_Setup_v{tag}.exe"

            if tag and download_url:
                return tag, download_url, notes
    except Exception:
        pass

    return None, None, None


def check_for_updates_async(parent_window, silent=True):
    """
    Check for updates in a background thread.
    """
    def worker():
        latest_version, download_url, notes = fetch_latest_release_info()

        if not latest_version:
            if not silent:
                parent_window.after(
                    0,
                    lambda: messagebox.showinfo(
                        "ICDS AutoDesk",
                        "Unable to connect to update server. Please verify your internet connection.",
                        parent=parent_window
                    )
                )
            return

        current_v = parse_version(APP_VERSION)
        latest_v = parse_version(latest_version)

        if latest_v > current_v:
            parent_window.after(
                0,
                lambda: _prompt_update(parent_window, latest_version, download_url, notes)
            )
        else:
            if not silent:
                parent_window.after(
                    0,
                    lambda: messagebox.showinfo(
                        "ICDS AutoDesk",
                        f"You are already on the latest version (v{APP_VERSION}).",
                        parent=parent_window
                    )
                )

    threading.Thread(target=worker, daemon=True).start()


def _prompt_update(parent_window, latest_version: str, download_url: str, notes: str):
    msg = (
        f"A new version of ICDS AutoDesk is available!\n\n"
        f"• Installed Version: v{APP_VERSION}\n"
        f"• Latest Available: v{latest_version}\n\n"
        f"Summary of Changes:\n{notes}\n\n"
        f"Would you like to download and install this update now?"
    )
    res = messagebox.askyesno("Update Available", msg, parent=parent_window)
    if res:
        ModernUpdateDialog(parent_window, latest_version, download_url, notes)
