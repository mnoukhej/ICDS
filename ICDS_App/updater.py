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
import tkinter as tk
from tkinter import ttk, messagebox

APP_VERSION = "4.0.0"
GITHUB_REPO = "mnoukhej/ICDS"
RAW_VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/version.json"
API_RELEASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def parse_version(version_str: str):
    """Convert version strings like 'v4.1.0' or '4.1' into tuple of integers (4, 1, 0)"""
    nums = re.findall(r"\d+", str(version_str))
    return tuple(int(n) for n in nums) if nums else (0,)


class UpdateDownloadDialog:
    """Toplevel progress dialog for downloading installer"""

    def __init__(self, parent, latest_version: str, download_url: str):
        self.parent = parent
        self.latest_version = latest_version
        self.download_url = download_url
        self.cancelled = False
        self.temp_installer_path = None

        self.win = tk.Toplevel(parent)
        self.win.title("ICDS AutoDesk Updater")
        self.win.geometry("420x200")
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()

        # Center over parent
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        cx = px + max(0, (pw - 420) // 2)
        cy = py + max(0, (ph - 200) // 2)
        self.win.geometry(f"+{cx}+{cy}")

        # UI elements
        container = ttk.Frame(self.win, padding=20)
        container.pack(fill="both", expand=True)

        self.title_label = ttk.Label(
            container,
            text=f"Downloading Update v{self.latest_version}...",
            font=("Segoe UI", 11, "bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 10))

        self.progress = ttk.Progressbar(container, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 8))

        self.status_label = ttk.Label(
            container,
            text="Connecting to download server...",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(anchor="w", pady=(0, 15))

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x")

        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self._on_cancel)
        self.cancel_btn.pack(side="right")

        self.win.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # Start download thread
        threading.Thread(target=self._download_worker, daemon=True).start()

    def _on_cancel(self):
        self.cancelled = True
        self.status_label.config(text="Cancelling download...")
        if self.temp_installer_path and os.path.exists(self.temp_installer_path):
            try:
                os.remove(self.temp_installer_path)
            except Exception:
                pass
        self.win.destroy()

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
                chunk_size = 64 * 1024  # 64 KB

                with open(self.temp_installer_path, "wb") as f:
                    while not self.cancelled:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_bytes > 0:
                            percent = int((downloaded / total_bytes) * 100)
                            mb_down = downloaded / (1024 * 1024)
                            mb_total = total_bytes / (1024 * 1024)
                            text = f"{percent}% ({mb_down:.1f} MB of {mb_total:.1f} MB)"
                            self.win.after(0, self._update_progress, percent, text)
                        else:
                            mb_down = downloaded / (1024 * 1024)
                            text = f"Downloaded {mb_down:.1f} MB"
                            self.win.after(0, self._update_progress, 50, text)

            if self.cancelled:
                return

            self.win.after(0, self._on_download_complete)

        except Exception as e:
            if not self.cancelled:
                self.win.after(0, self._on_download_error, str(e))

    def _update_progress(self, percent: int, text: str):
        if not self.cancelled and self.win.winfo_exists():
            self.progress["value"] = percent
            self.status_label.config(text=text)

    def _on_download_error(self, err_msg: str):
        messagebox.showerror(
            "Download Error",
            f"Failed to download update:\n{err_msg}\nPlease try again later or download directly from GitHub.",
            parent=self.win
        )
        self.win.destroy()

    def _on_download_complete(self):
        self.status_label.config(text="Download complete! Launching installer...")
        self.win.update()

        # Run installer detached
        try:
            # /CLOSEAPPLICATIONS closes running app instances cleanly
            # /RESTARTAPPLICATIONS restarts app if supported
            subprocess.Popen(
                [self.temp_installer_path, "/CLOSEAPPLICATIONS"],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
            )
            # Destroy UI and exit running app to release file locks
            self.parent.destroy()
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to run installer:\n{e}", parent=self.win)
            self.win.destroy()


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

            # Search for setup or exe in assets
            download_url = None
            for asset in data.get("assets", []):
                name = asset.get("name", "").lower()
                if name.endswith(".exe"):
                    download_url = asset.get("browser_download_url")
                    if "setup" in name:
                        break  # Prefer setup installer

            if not download_url:
                # Fallback to direct download URL pattern
                download_url = f"https://github.com/{GITHUB_REPO}/releases/latest/download/ICDSAutoDesk_Setup_v{tag}.exe"

            if tag and download_url:
                return tag, download_url, notes
    except Exception:
        pass

    return None, None, None


def check_for_updates_async(parent_window, silent=True):
    """
    Check for updates in a background thread.
    If silent=True, suppresses messages when up-to-date or offline.
    If silent=False (manual click), alerts user with results.
    """
    def worker():
        latest_version, download_url, notes = fetch_latest_release_info()

        if not latest_version:
            if not silent:
                parent_window.after(
                    0,
                    lambda: messagebox.showinfo(
                        "ICDS AutoDesk",
                        "Unable to connect to update server. Please check your internet connection.",
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
                        f"You are already using the latest version (v{APP_VERSION}).",
                        parent=parent_window
                    )
                )

    threading.Thread(target=worker, daemon=True).start()


def _prompt_update(parent_window, latest_version: str, download_url: str, notes: str):
    msg = (
        f"A new version of ICDS AutoDesk is available!\n\n"
        f"• Installed Version: v{APP_VERSION}\n"
        f"• Latest Version: v{latest_version}\n\n"
        f"Changelog / Notes:\n{notes}\n\n"
        f"Would you like to download and install this update now?"
    )
    res = messagebox.askyesno("Update Available", msg, parent=parent_window)
    if res:
        UpdateDownloadDialog(parent_window, latest_version, download_url)

