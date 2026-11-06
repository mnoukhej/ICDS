# Applicatin.py
# ICDS AutoDesk - Modern Desktop Application

import os
import sys
import re
import math
import shutil
import calendar
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageDraw, ImageTk
import pandas as pd

from Main_Func import Format_Generator, Report_Generator_py
from updater import check_for_updates_async, APP_VERSION


# -----------------------------
# Resource Path Helper (PyInstaller & Dev friendly)
# -----------------------------
def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller exe"""
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ----------------------------------------------------------------------
# Modern Design Tokens & Theme Palettes
# ----------------------------------------------------------------------
class ICDSAutoDeskApp:
    THEMES = {
        "light": {
            # Window & Base
            "BG_ROOT": "#F8FAFC",          # Soft Slate/Off-white
            "CARD_BG": "#FFFFFF",          # Pure Card White
            "CARD_BORDER": "#E2E8F0",      # Delicate Border
            "HEADER_BG": "#FFFFFF",        # Top bar white
            "HEADER_BORDER": "#E2E8F0",    # Divider line
            
            # Typography
            "TEXT_PRIMARY": "#0F172A",     # Slate 900
            "TEXT_SECONDARY": "#475569",   # Slate 600
            "TEXT_MUTED": "#94A3B8",       # Slate 400
            
            # Brand Accents & Interactive
            "ACCENT_BLUE": "#2563EB",      # Royal Blue
            "ACCENT_HOVER": "#1D4ED8",     # Blue 700
            "BRAND_PURPLE": "#7C3AED",     # Purple 600
            "BRAND_PURPLE_HOVER": "#6D28D9",
            "ACCENT_EMERALD": "#059669",   # Green 600
            "ACCENT_EMERALD_HOVER": "#047857",
            "ACCENT_AMBER": "#D97706",     # Amber 600
            "ACCENT_AMBER_HOVER": "#B45309",
            "ACCENT_ROSE": "#E11D48",      # Rose 600
            "ACCENT_ROSE_HOVER": "#BE123C",
            
            # Input Fields
            "INPUT_BG": "#F1F5F9",         # Slate 100
            "INPUT_BORDER": "#CBD5E1",     # Slate 300
            "INPUT_FOCUS": "#3B82F6",
            
            # Secondary Buttons
            "BTN_SECONDARY_BG": "#E2E8F0",
            "BTN_SECONDARY_HOVER": "#CBD5E1",
            "BTN_SECONDARY_FG": "#1E293B",
            
            # Badges / Chips
            "CHIP_BG": "#EFF6FF",
            "CHIP_FG": "#1D4ED8",
            "CHIP_BORDER": "#BFDBFE",
        },
        "dark": {
            # Window & Base
            "BG_ROOT": "#0F172A",          # Deep Midnight Slate 900
            "CARD_BG": "#1E293B",          # Elevated Slate 800
            "CARD_BORDER": "#334155",      # Subtle Slate 700
            "HEADER_BG": "#1E293B",        # Header bar
            "HEADER_BORDER": "#334155",
            
            # Typography
            "TEXT_PRIMARY": "#F8FAFC",     # Bright Slate 50
            "TEXT_SECONDARY": "#CBD5E1",   # Muted Slate 300
            "TEXT_MUTED": "#64748B",       # Slate 500
            
            # Brand Accents & Interactive
            "ACCENT_BLUE": "#3B82F6",      # Blue 500
            "ACCENT_HOVER": "#60A5FA",     # Blue 400
            "BRAND_PURPLE": "#8B5CF6",     # Violet 500
            "BRAND_PURPLE_HOVER": "#A78BFA",
            "ACCENT_EMERALD": "#10B981",   # Emerald 500
            "ACCENT_EMERALD_HOVER": "#34D399",
            "ACCENT_AMBER": "#F59E0B",     # Amber 500
            "ACCENT_AMBER_HOVER": "#FBBF24",
            "ACCENT_ROSE": "#F43F5E",      # Rose 500
            "ACCENT_ROSE_HOVER": "#FB7185",
            
            # Input Fields
            "INPUT_BG": "#0F172A",         # Deep Slate 900
            "INPUT_BORDER": "#475569",     # Slate 600
            "INPUT_FOCUS": "#60A5FA",
            
            # Secondary Buttons
            "BTN_SECONDARY_BG": "#334155",
            "BTN_SECONDARY_HOVER": "#475569",
            "BTN_SECONDARY_FG": "#F8FAFC",
            
            # Badges / Chips
            "CHIP_BG": "#1E3A8A",
            "CHIP_FG": "#93C5FD",
            "CHIP_BORDER": "#1D4ED8",
        },
    }

    def __init__(self, root):
        self.root = root
        self.root.title("ICDS AutoDesk — Automated Report Generation")

        # Generous modern dimensions
        window_width, window_height = 680, 640
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = int((sw - window_width) / 2)
        y = int((sh - window_height) / 2) - 40
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(620, 580)

        self.theme_mode = "light"
        self._image_cache = {}

        # Set titlebar and window icons
        try:
            self.root.iconbitmap(resource_path("icon.ico"))
        except Exception:
            try:
                self.root.iconbitmap(resource_path("app_icon.ico"))
            except Exception:
                pass

        self._set_iconphoto_png(resource_path("logo.png"))

        # Cached Logo
        self.logo_tk = None
        self._load_logo()

        # Init Ttk Themes
        self._style_ttk_for_theme()

        # Temporary folders cleanup
        self._clear_temp_folders()

        # State trackers
        self.generated_file_path = None
        self.report_file_path = None
        self.selected_file_label = None

        # Build First Screen
        self._show_home()

        # Non-blocking background check for updates after 2.5 seconds
        self.root.after(2500, lambda: check_for_updates_async(self.root, silent=True))

    # ------------------------------------------------------------------
    # Resource & Graphic Utilities (Anti-aliased Pillow rendering)
    # ------------------------------------------------------------------
    def _set_iconphoto_png(self, path: str):
        try:
            if os.path.exists(path):
                icon_img = tk.PhotoImage(file=path)
                self.root.iconphoto(False, icon_img)
                self._icon_img_ref = icon_img
        except Exception:
            pass

    def _load_logo(self):
        try:
            logo_path = resource_path("logo.png")
            if os.path.exists(logo_path):
                img = Image.open(logo_path).resize((84, 84), Image.LANCZOS)
                self.logo_tk = ImageTk.PhotoImage(img)
        except Exception as e:
            print("Logo load failed:", e)

    def _adjust_hex(self, hex_color: str, factor: float):
        """Brighten or darken hex color by factor."""
        h = hex_color.lstrip("#")
        r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _create_rounded_image(self, width, height, bg_color, border_color=None, border_width=1, radius=14):
        """
        Generates ultra-smooth 2x supersampled rounded rectangle with optional border.
        Cached in dictionary to minimize CPU cycles.
        """
        key = (width, height, bg_color, border_color, border_width, radius)
        if key in self._image_cache:
            return self._image_cache[key]

        scale = 2  # 2x supersampling for crisp edges
        w_scaled = width * scale
        h_scaled = height * scale
        r_scaled = radius * scale

        img = Image.new("RGBA", (w_scaled, h_scaled), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if border_color and border_width > 0:
            draw.rounded_rectangle((0, 0, w_scaled, h_scaled), radius=r_scaled, fill=border_color)
            b_scaled = border_width * scale
            draw.rounded_rectangle(
                (b_scaled, b_scaled, w_scaled - b_scaled, h_scaled - b_scaled),
                radius=max(0, r_scaled - b_scaled),
                fill=bg_color
            )
        else:
            draw.rounded_rectangle((0, 0, w_scaled, h_scaled), radius=r_scaled, fill=bg_color)

        rendered = ImageTk.PhotoImage(img.resize((width, height), Image.LANCZOS))
        self._image_cache[key] = rendered
        return rendered

    def _style_ttk_for_theme(self):
        t = self.THEMES[self.theme_mode]
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Beautiful Combobox Style
        style.configure(
            "Modern.TCombobox",
            fieldbackground=t["INPUT_BG"],
            background=t["CARD_BG"],
            foreground=t["TEXT_PRIMARY"],
            arrowcolor=t["TEXT_SECONDARY"],
            bordercolor=t["INPUT_BORDER"],
            lightcolor=t["INPUT_BG"],
            darkcolor=t["INPUT_BG"],
            padding=6,
        )
        style.map(
            "Modern.TCombobox",
            fieldbackground=[
                ("readonly", t["INPUT_BG"]),
                ("focus", t["CARD_BG"])
            ],
            foreground=[
                ("readonly", t["TEXT_PRIMARY"]),
                ("focus", t["TEXT_PRIMARY"])
            ],
            bordercolor=[
                ("focus", t["INPUT_FOCUS"])
            ]
        )

    # ------------------------------------------------------------------
    # Reusable Component Architecture
    # ------------------------------------------------------------------
    def _clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _build_header_navbar(self):
        """Top Navigation bar with brand title, update checker chip, and animated theme switch."""
        t = self.THEMES[self.theme_mode]

        nav_frame = tk.Frame(self.root, bg=t["HEADER_BG"], height=56)
        nav_frame.pack(fill="x", side="top")

        # Inner container for margins
        inner_nav = tk.Frame(nav_frame, bg=t["HEADER_BG"])
        inner_nav.pack(fill="x", padx=20, pady=8)

        # Brand Title
        brand_frame = tk.Frame(inner_nav, bg=t["HEADER_BG"])
        brand_frame.pack(side="left")

        app_title = tk.Label(
            brand_frame,
            text="ICDS AutoDesk",
            font=("Segoe UI", 12, "bold"),
            fg=t["TEXT_PRIMARY"],
            bg=t["HEADER_BG"]
        )
        app_title.pack(side="left")

        # Pill Badge for Version
        ver_badge = tk.Label(
            brand_frame,
            text=f"v{APP_VERSION}",
            font=("Segoe UI", 8, "bold"),
            fg=t["CHIP_FG"],
            bg=t["CHIP_BG"],
            padx=8,
            pady=2
        )
        ver_badge.pack(side="left", padx=(8, 0))

        # Right side controls: Check Updates button + Theme Toggle
        ctrl_frame = tk.Frame(inner_nav, bg=t["HEADER_BG"])
        ctrl_frame.pack(side="right")

        check_btn = tk.Button(
            ctrl_frame,
            text="↻ Check Updates",
            font=("Segoe UI", 9, "bold"),
            bg=t["BTN_SECONDARY_BG"],
            fg=t["BTN_SECONDARY_FG"],
            activebackground=t["BTN_SECONDARY_HOVER"],
            activeforeground=t["BTN_SECONDARY_FG"],
            bd=0,
            padx=10,
            pady=4,
            relief="flat",
            cursor="hand2",
            command=lambda: check_for_updates_async(self.root, silent=False)
        )
        check_btn.pack(side="left", padx=(0, 12))

        # Theme toggle inside topbar
        self._theme_switch(ctrl_frame)

        # Divider border below header
        divider = tk.Frame(self.root, bg=t["HEADER_BORDER"], height=1)
        divider.pack(fill="x", side="top")

    def _theme_switch(self, parent):
        """Sleek animated pill theme switcher (Light / Dark)."""
        t = self.THEMES[self.theme_mode]
        switch_w, switch_h = 52, 28
        knob_d = 22
        pad = 3
        canvas = tk.Canvas(
            parent, width=switch_w, height=switch_h, bd=0,
            highlightthickness=0, bg=t["HEADER_BG"], cursor="hand2"
        )
        canvas.pack(side="right")

        knob_x = pad if self.theme_mode == "light" else switch_w - knob_d - pad

        def draw_switch(x):
            canvas.delete("all")
            track_color = "#E2E8F0" if self.theme_mode == "light" else "#334155"
            r = switch_h // 2
            canvas.create_oval(0, 0, switch_h, switch_h, fill=track_color, outline=track_color)
            canvas.create_oval(switch_w - switch_h, 0, switch_w, switch_h, fill=track_color, outline=track_color)
            canvas.create_rectangle(r, 0, switch_w - r, switch_h, fill=track_color, outline=track_color)

            # Sun / Moon iconography
            if self.theme_mode == "light":
                # Sun representation
                canvas.create_oval(switch_w - 20, 7, switch_w - 8, 19, fill="#F59E0B", outline="#F59E0B")
            else:
                # Moon representation
                canvas.create_oval(8, 7, 20, 19, fill="#38BDF8", outline="#38BDF8")
                canvas.create_oval(11, 6, 22, 17, fill=track_color, outline=track_color)

            # Knob
            knob_fill = "#FFFFFF" if self.theme_mode == "light" else "#F1F5F9"
            canvas.create_oval(x, pad, x + knob_d, pad + knob_d, fill=knob_fill, outline="#CBD5E1")

        def animate_toggle(start_x, end_x):
            step = 3 if end_x > start_x else -3
            for pos in range(start_x, end_x, step):
                draw_switch(pos)
                canvas.update()
                canvas.after(4)
            draw_switch(end_x)

        def toggle():
            nonlocal knob_x
            if self.theme_mode == "light":
                end_x = switch_w - knob_d - pad
                animate_toggle(knob_x, end_x)
                self.theme_mode = "dark"
            else:
                end_x = pad
                animate_toggle(knob_x, end_x)
                self.theme_mode = "light"

            self.root.configure(bg=self.THEMES[self.theme_mode]["BG_ROOT"])
            self._style_ttk_for_theme()
            self._show_home()

        canvas.bind("<Button-1>", lambda e: toggle())
        draw_switch(knob_x)

    def _page_header(self, title: str, subtitle: str):
        """Structured page title with crisp typography hierarchy."""
        t = self.THEMES[self.theme_mode]
        header_frame = tk.Frame(self.root, bg=t["BG_ROOT"])
        header_frame.pack(fill="x", padx=30, pady=(18, 12))

        lbl_title = tk.Label(
            header_frame,
            text=title,
            font=("Segoe UI", 18, "bold"),
            fg=t["TEXT_PRIMARY"],
            bg=t["BG_ROOT"]
        )
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(
            header_frame,
            text=subtitle,
            font=("Segoe UI", 10),
            fg=t["TEXT_SECONDARY"],
            bg=t["BG_ROOT"]
        )
        lbl_sub.pack(anchor="w", pady=(3, 0))

    def _modern_card(self, width=620, height=260, radius=16):
        """Card container with subtle border and crisp anti-aliased corners."""
        t = self.THEMES[self.theme_mode]
        wrapper = tk.Frame(self.root, bg=t["BG_ROOT"])
        wrapper.pack(pady=8, padx=30, fill="x")

        bg_img = self._create_rounded_image(
            width, height,
            bg_color=t["CARD_BG"],
            border_color=t["CARD_BORDER"],
            border_width=1,
            radius=radius
        )
        bg_lbl = tk.Label(wrapper, image=bg_img, bg=t["BG_ROOT"], bd=0)
        bg_lbl.image = bg_img
        bg_lbl.pack()

        inner = tk.Frame(wrapper, bg=t["CARD_BG"])
        inner.place(in_=bg_lbl, relx=0.5, rely=0.5, anchor="center")

        inner_pad = tk.Frame(inner, bg=t["CARD_BG"])
        inner_pad.pack(padx=24, pady=20, fill="both", expand=True)
        return inner_pad

    def _action_tile(self, parent, icon_str: str, title: str, desc: str, bg_color: str, hover_color: str, command):
        """
        Modern interactive action card tile with icon, title, description, and hover elevation.
        """
        t = self.THEMES[self.theme_mode]
        width, height = 540, 84
        normal_img = self._create_rounded_image(width, height, bg_color=t["CARD_BG"], border_color=t["CARD_BORDER"], border_width=1, radius=14)
        hover_img = self._create_rounded_image(width, height, bg_color=t["CARD_BG"], border_color=bg_color, border_width=2, radius=14)

        container = tk.Frame(parent, bg=t["CARD_BG"], cursor="hand2")
        container.pack(pady=7, fill="x")

        bg_lbl = tk.Label(container, image=normal_img, bg=t["CARD_BG"], bd=0, cursor="hand2")
        bg_lbl.image_normal = normal_img
        bg_lbl.image_hover = hover_img
        bg_lbl.pack()

        content = tk.Frame(container, bg=t["CARD_BG"], cursor="hand2")
        content.place(in_=bg_lbl, relx=0.03, rely=0.5, anchor="w")

        # Icon Chip
        icon_chip = tk.Label(
            content,
            text=icon_str,
            font=("Segoe UI", 16),
            fg="#FFFFFF",
            bg=bg_color,
            width=3,
            height=1,
            pady=6,
            relief="flat",
            cursor="hand2"
        )
        icon_chip.pack(side="left", padx=(4, 14))

        # Text Block
        text_block = tk.Frame(content, bg=t["CARD_BG"], cursor="hand2")
        text_block.pack(side="left", fill="y")

        t_lbl = tk.Label(
            text_block,
            text=title,
            font=("Segoe UI", 11, "bold"),
            fg=t["TEXT_PRIMARY"],
            bg=t["CARD_BG"],
            cursor="hand2"
        )
        t_lbl.pack(anchor="w")

        d_lbl = tk.Label(
            text_block,
            text=desc,
            font=("Segoe UI", 9),
            fg=t["TEXT_SECONDARY"],
            bg=t["CARD_BG"],
            cursor="hand2"
        )
        d_lbl.pack(anchor="w", pady=(2, 0))

        # Chevron Arrow
        arrow_lbl = tk.Label(
            container,
            text="➔",
            font=("Segoe UI", 12, "bold"),
            fg=bg_color,
            bg=t["CARD_BG"],
            cursor="hand2"
        )
        arrow_lbl.place(in_=bg_lbl, relx=0.96, rely=0.5, anchor="e")

        def on_enter(_):
            bg_lbl.configure(image=hover_img)
            icon_chip.configure(bg=hover_color)

        def on_leave(_):
            bg_lbl.configure(image=normal_img)
            icon_chip.configure(bg=bg_color)

        for widget in (container, bg_lbl, content, icon_chip, text_block, t_lbl, d_lbl, arrow_lbl):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e: command())

        return container

    def _button_primary(self, parent, text, command, width=320, height=44, bg_color=None, hover_color=None):
        """Modern primary rounded action button with hover glow."""
        t = self.THEMES[self.theme_mode]
        bg = bg_color or t["ACCENT_BLUE"]
        hover = hover_color or t["ACCENT_HOVER"]

        normal = self._create_rounded_image(width, height, bg_color=bg, radius=10)
        hover_img = self._create_rounded_image(width, height, bg_color=hover, radius=10)

        wrapper = tk.Frame(parent, bg=parent["bg"])
        btn = tk.Label(wrapper, image=normal, bg=parent["bg"], cursor="hand2", bd=0)
        btn.image_normal = normal
        btn.image_hover = hover_img
        btn.pack(pady=4)

        txt = tk.Label(btn, text=text, font=("Segoe UI", 10, "bold"), fg="#FFFFFF", bg=bg, cursor="hand2")
        txt.place(relx=0.5, rely=0.5, anchor="center")

        def on_enter(_):
            btn.configure(image=hover_img)
            txt.configure(bg=hover)

        def on_leave(_):
            btn.configure(image=normal)
            txt.configure(bg=bg)

        for w in (btn, txt):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", lambda e: command())

        return wrapper

    def _button_secondary(self, parent, text, command, width=320, height=38):
        """Subtle secondary button for Back/Cancel actions."""
        t = self.THEMES[self.theme_mode]
        bg = t["BTN_SECONDARY_BG"]
        hover = t["BTN_SECONDARY_HOVER"]
        fg = t["BTN_SECONDARY_FG"]

        normal = self._create_rounded_image(width, height, bg_color=bg, radius=10)
        hover_img = self._create_rounded_image(width, height, bg_color=hover, radius=10)

        wrapper = tk.Frame(parent, bg=parent["bg"])
        btn = tk.Label(wrapper, image=normal, bg=parent["bg"], cursor="hand2", bd=0)
        btn.image_normal = normal
        btn.image_hover = hover_img
        btn.pack(pady=4)

        txt = tk.Label(btn, text=text, font=("Segoe UI", 9, "bold"), fg=fg, bg=bg, cursor="hand2")
        txt.place(relx=0.5, rely=0.5, anchor="center")

        def on_enter(_):
            btn.configure(image=hover_img)
            txt.configure(bg=hover)

        def on_leave(_):
            btn.configure(image=normal)
            txt.configure(bg=bg)

        for w in (btn, txt):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", lambda e: command())

        return wrapper

    def _footer(self):
        """Minimal clean footer with developer credits."""
        t = self.THEMES[self.theme_mode]
        footer_frame = tk.Frame(self.root, bg=t["BG_ROOT"])
        footer_frame.pack(side="bottom", fill="x", pady=12)

        lbl = tk.Label(
            footer_frame,
            text=f"© 2026 ICDS AutoDesk • Engineered by Muhammad Noukhez • CodeX404 Solutions",
            font=("Segoe UI", 8),
            fg=t["TEXT_MUTED"],
            bg=t["BG_ROOT"]
        )
        lbl.pack()

    # ------------------------------------------------------------------
    # Temp folders
    # ------------------------------------------------------------------
    def _clear_temp_folders(self):
        for folder in ("temp_generated", "temp_generated_report"):
            path = os.path.join(os.getcwd(), folder)
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    print(f"Error clearing {folder}: {e}")

    # ------------------------------------------------------------------
    # Screen 1: Home Dashboard
    # ------------------------------------------------------------------
    def _show_home(self):
        self._clear_temp_folders()
        self._clear_root()
        t = self.THEMES[self.theme_mode]
        self.root.configure(bg=t["BG_ROOT"])

        # 1. Header Navbar
        self._build_header_navbar()

        # 2. Hero Section
        hero = tk.Frame(self.root, bg=t["BG_ROOT"])
        hero.pack(fill="x", padx=30, pady=(20, 10))

        if self.logo_tk:
            logo_lbl = tk.Label(hero, image=self.logo_tk, bg=t["BG_ROOT"])
            logo_lbl.pack(side="left", padx=(0, 16))

        hero_text = tk.Frame(hero, bg=t["BG_ROOT"])
        hero_text.pack(side="left", fill="both", expand=True)

        welcome_lbl = tk.Label(
            hero_text,
            text="Welcome to ICDS AutoDesk",
            font=("Segoe UI", 18, "bold"),
            fg=t["TEXT_PRIMARY"],
            bg=t["BG_ROOT"]
        )
        welcome_lbl.pack(anchor="w")

        tagline_lbl = tk.Label(
            hero_text,
            text="Automated Excel template creation, holiday syncing & stock report engine.",
            font=("Segoe UI", 10),
            fg=t["TEXT_SECONDARY"],
            bg=t["BG_ROOT"]
        )
        tagline_lbl.pack(anchor="w", pady=(4, 0))

        # 3. Action Cards
        action_card = self._modern_card(width=620, height=250, radius=18)

        section_lbl = tk.Label(
            action_card,
            text="QUICK WORKFLOWS",
            font=("Segoe UI", 9, "bold"),
            fg=t["TEXT_MUTED"],
            bg=t["CARD_BG"]
        )
        section_lbl.pack(anchor="w", pady=(0, 6), padx=4)

        # Action Tile 1: Template Designer
        self._action_tile(
            action_card,
            icon_str="📅",
            title="Design Monthly Template Format",
            desc="Configure month, year, and polio campaigns with pre-calculated days & holidays.",
            bg_color=t["ACCENT_EMERALD"],
            hover_color=t["ACCENT_EMERALD_HOVER"],
            command=self._show_generate_format
        )

        # Action Tile 2: Report Generator
        self._action_tile(
            action_card,
            icon_str="📊",
            title="Process Completed Data & Build Report",
            desc="Upload your filled monthly data Excel to calculate balances & export final reports.",
            bg_color=t["ACCENT_BLUE"],
            hover_color=t["ACCENT_HOVER"],
            command=self._show_generate_report
        )

        self._footer()

    # ------------------------------------------------------------------
    # Screen 2: Template Designer Screen
    # ------------------------------------------------------------------
    def _show_generate_format(self):
        self._clear_temp_folders()
        self._clear_root()
        t = self.THEMES[self.theme_mode]
        self.root.configure(bg=t["BG_ROOT"])

        self._build_header_navbar()
        self._page_header("Report Template Designer", "Select a target month and year to generate a formatted monthly schedule.")

        card = self._modern_card(width=620, height=330, radius=18)

        inputs = tk.Frame(card, bg=t["CARD_BG"])
        inputs.pack(pady=(6, 14), fill="x", padx=10)

        # Month Selector
        m_lbl = tk.Label(
            inputs, text="Select Month:", font=("Segoe UI", 10, "bold"),
            fg=t["TEXT_PRIMARY"], bg=t["CARD_BG"]
        )
        m_lbl.grid(row=0, column=0, sticky="w", pady=8, padx=(0, 14))

        self.month_var = tk.StringVar()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        month_cb = ttk.Combobox(
            inputs, textvariable=self.month_var, values=months,
            state="readonly", width=24, style="Modern.TCombobox"
        )
        month_cb.grid(row=0, column=1, sticky="w", pady=8)
        month_cb.bind("<<ComboboxSelected>>", lambda e: self._update_polio_sundays())

        # Year Selector
        y_lbl = tk.Label(
            inputs, text="Select Year:", font=("Segoe UI", 10, "bold"),
            fg=t["TEXT_PRIMARY"], bg=t["CARD_BG"]
        )
        y_lbl.grid(row=1, column=0, sticky="w", pady=8, padx=(0, 14))

        self.year_var = tk.StringVar()
        years = [str(y) for y in range(2024, 2101)]
        year_cb = ttk.Combobox(
            inputs, textvariable=self.year_var, values=years,
            state="readonly", width=24, style="Modern.TCombobox"
        )
        year_cb.grid(row=1, column=1, sticky="w", pady=8)
        year_cb.bind("<<ComboboxSelected>>", lambda e: self._update_polio_sundays())

        # Polio Campaign Options
        self.include_polio = tk.BooleanVar(value=False)
        self.polio_check = tk.Checkbutton(
            inputs,
            text="Include Polio Campaign Day",
            variable=self.include_polio,
            command=self._toggle_polio_day,
            fg=t["TEXT_PRIMARY"],
            bg=t["CARD_BG"],
            selectcolor=t["CARD_BG"],
            activebackground=t["CARD_BG"],
            font=("Segoe UI", 10),
            state="disabled",
            cursor="hand2"
        )
        self.polio_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 4))

        self.polio_day_label = tk.Label(
            inputs, text="Select Polio Sunday:",
            font=("Segoe UI", 10, "bold"), fg=t["TEXT_PRIMARY"], bg=t["CARD_BG"]
        )
        self.polio_day_var = tk.StringVar()
        self.polio_day_cb = ttk.Combobox(
            inputs, textvariable=self.polio_day_var,
            state="readonly", width=24, style="Modern.TCombobox"
        )

        # Actions
        btn_box = tk.Frame(card, bg=t["CARD_BG"])
        btn_box.pack(pady=(10, 4))

        self._button_primary(
            btn_box, "⚡ Generate Template Format", self._generate_format,
            width=360, height=44, bg_color=t["ACCENT_EMERALD"], hover_color=t["ACCENT_EMERALD_HOVER"]
        )
        self._button_secondary(
            btn_box, "← Back to Home", self._show_home, width=360, height=36
        )

        self._footer()

    def _toggle_polio_day(self):
        if self.include_polio.get():
            self._update_polio_sundays()
            self.polio_day_label.grid(row=3, column=0, sticky="w", pady=8, padx=(0, 14))
            self.polio_day_cb.grid(row=3, column=1, sticky="w", pady=8)
        else:
            self.polio_day_label.grid_forget()
            self.polio_day_cb.grid_forget()

    def _update_polio_sundays(self):
        try:
            month_ok = bool(getattr(self, "month_var", tk.StringVar()).get())
            year_ok = bool(getattr(self, "year_var", tk.StringVar()).get())

            if month_ok and year_ok:
                self.polio_check.config(state="normal")
            else:
                self.polio_check.config(state="disabled")
                self.include_polio.set(False)
                self._toggle_polio_day()

            if not (month_ok and year_ok):
                return

            month_num = ["January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"].index(self.month_var.get()) + 1
            year = int(self.year_var.get())

            sundays = [str(day) for day in range(1, calendar.monthrange(year, month_num)[1] + 1)
                       if calendar.weekday(year, month_num, day) == 6]

            self.polio_day_cb["values"] = sundays
            if sundays:
                self.polio_day_cb.current(0)
        except Exception as e:
            print("Error updating Sundays:", e)

    def _generate_format(self):
        try:
            month_name = self.month_var.get()
            if not month_name:
                messagebox.showerror("Selection Required", "Please select a month to continue.")
                return
            month_num = ["January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"].index(month_name) + 1

            if not self.year_var.get():
                messagebox.showerror("Selection Required", "Please select a year to continue.")
                return
            year = int(self.year_var.get())

            polio_day = int(self.polio_day_var.get()) if (self.include_polio.get() and self.polio_day_var.get()) else None

            temp_folder = os.path.join(os.getcwd(), "temp_generated")
            os.makedirs(temp_folder, exist_ok=True)

            Format_Generator(month_num, year, polio_day, temp_folder)

            self.generated_file_path = None
            for f in os.listdir(temp_folder):
                self.generated_file_path = os.path.join(temp_folder, f)

            self._show_download("Report Template")
        except Exception as e:
            messagebox.showerror("Generation Error", str(e))

    # ------------------------------------------------------------------
    # Screen 3: Generate Report Screen
    # ------------------------------------------------------------------
    def _show_generate_report(self):
        self._clear_temp_folders()
        self._clear_root()
        t = self.THEMES[self.theme_mode]
        self.root.configure(bg=t["BG_ROOT"])

        self._build_header_navbar()
        self._page_header("Report Builder & Processor", "Upload completed monthly format data to calculate rations and stock balances.")

        card = self._modern_card(width=620, height=330, radius=18)

        self.report_file_path = None
        self.selected_file_label = None

        # Upload Dropzone Card
        drop_frame = tk.Frame(card, bg=t["INPUT_BG"], padx=20, pady=20)
        drop_frame.pack(fill="x", pady=(8, 14))

        icon_up = tk.Label(
            drop_frame, text="📁", font=("Segoe UI", 24),
            bg=t["INPUT_BG"], fg=t["TEXT_PRIMARY"]
        )
        icon_up.pack()

        inst_lbl = tk.Label(
            drop_frame,
            text="Click below to select your completed monthly Excel file (*.xlsx)",
            font=("Segoe UI", 10),
            bg=t["INPUT_BG"],
            fg=t["TEXT_SECONDARY"]
        )
        inst_lbl.pack(pady=(4, 10))

        upload_btn = self._button_primary(
            drop_frame, "Browse & Select Excel File", lambda: self._select_file(drop_frame, upload_btn),
            width=280, height=38, bg_color=t["BRAND_PURPLE"], hover_color=t["BRAND_PURPLE_HOVER"]
        )
        upload_btn.pack()

        # Action Buttons
        btn_box = tk.Frame(card, bg=t["CARD_BG"])
        btn_box.pack(pady=(10, 4))

        self._button_primary(
            btn_box, "⚡ Process & Build Final Report", self._generate_report_from_file,
            width=360, height=44, bg_color=t["ACCENT_BLUE"], hover_color=t["ACCENT_HOVER"]
        )
        self._button_secondary(
            btn_box, "← Back to Home", self._show_home, width=360, height=36
        )

        self._footer()

    def _select_file(self, parent_widget, after_widget):
        if self.selected_file_label:
            self.selected_file_label.destroy()
            self.selected_file_label = None

        self.report_file_path = None
        self.generated_file_path = None

        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not path:
            return

        filename = os.path.basename(path)
        pattern = r"^(January|February|March|April|May|June|July|August|September|October|November|December)_(\d{4})_Report_Format\.xlsx$"

        if not re.match(pattern, filename):
            messagebox.showerror(
                "Invalid File Name",
                "Please select an official template in the format:\nMonth_Year_Report_Format.xlsx\n\nExample: September_2025_Report_Format.xlsx",
            )
            return

        self.report_file_path = path
        t = self.THEMES[self.theme_mode]

        self.selected_file_label = tk.Label(
            parent_widget,
            text=f"✓ Selected: {filename}",
            fg=t["ACCENT_EMERALD"],
            bg=t["INPUT_BG"],
            font=("Segoe UI", 10, "bold"),
        )
        self.selected_file_label.pack(pady=(8, 0), after=after_widget)

    def _generate_report_from_file(self):
        if not getattr(self, "report_file_path", None):
            messagebox.showerror("File Missing", "Please select and upload an Excel file first.")
            return

        try:
            temp_folder = os.path.join(os.getcwd(), "temp_generated_report")
            os.makedirs(temp_folder, exist_ok=True)

            df = pd.read_excel(self.report_file_path)

            required_columns = [
                "Date",
                "Days",
                "Pregnant (Mothers)",
                "Lactating (Mothers)",
                "Boys (6m - 3y)",
                "Girls (6m - 3y)",
                "Boys (3y - 6y)",
                "Girls (3y - 6y)",
            ]

            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                raise ValueError(f"The selected file is missing required columns:\n{', '.join(missing)}")

            empty_cols = [col for col in required_columns if df[col].isna().all()]
            if empty_cols:
                raise ValueError(f"The following columns contain no data:\n{', '.join(empty_cols)}")

            Report_Generator_py(self.report_file_path, temp_folder)

            self.generated_file_path = None
            for f in os.listdir(temp_folder):
                self.generated_file_path = os.path.join(temp_folder, f)

            self._show_download("Final Report")
        except Exception as e:
            messagebox.showerror("Processing Error", str(e))

    # ------------------------------------------------------------------
    # Screen 4: Download / Export Screen
    # ------------------------------------------------------------------
    def _show_download(self, file_type: str):
        self._clear_root()
        t = self.THEMES[self.theme_mode]
        self.root.configure(bg=t["BG_ROOT"])

        self._build_header_navbar()
        self._page_header("Processing Complete!", f"Your {file_type} has been successfully generated and is ready to save.")

        card = self._modern_card(width=620, height=260, radius=18)

        # Success Banner
        succ_frame = tk.Frame(card, bg=t["CHIP_BG"], padx=18, pady=14)
        succ_frame.pack(fill="x", pady=(4, 16))

        fname = os.path.basename(self.generated_file_path) if self.generated_file_path else "Generated File"
        succ_lbl = tk.Label(
            succ_frame,
            text=f"✓ File: {fname}",
            font=("Segoe UI", 11, "bold"),
            fg=t["CHIP_FG"],
            bg=t["CHIP_BG"]
        )
        succ_lbl.pack()

        # Save actions
        btn_box = tk.Frame(card, bg=t["CARD_BG"])
        btn_box.pack(pady=4)

        self._button_primary(
            btn_box, "💾 Save & Download File to PC", self._download_file,
            width=360, height=44, bg_color=t["ACCENT_EMERALD"], hover_color=t["ACCENT_EMERALD_HOVER"]
        )
        self._button_secondary(
            btn_box, "← Return to Main Menu", self._show_home, width=360, height=36
        )

        self._footer()
        messagebox.showinfo("Success", f"{file_type} generated successfully!")

    def _download_file(self):
        if not self.generated_file_path:
            messagebox.showerror("Error", "No file available to download.")
            return

        folder = filedialog.askdirectory(title="Select Destination Folder")
        if not folder:
            return

        try:
            dest = os.path.join(folder, os.path.basename(self.generated_file_path))
            shutil.copy2(self.generated_file_path, dest)
            messagebox.showinfo("File Saved", f"Your file has been saved successfully to:\n\n{dest}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

        self._clear_temp_folders()


# ----------------------------------------------------------------------
# Application Bootstrap
# ----------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ICDSAutoDeskApp(root)
    root.mainloop()
