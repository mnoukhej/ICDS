# Applicatin.py
# ICDS AutoDesk — Professional Desktop Application Suite

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
# Professional Design System & Color Tokens
# ----------------------------------------------------------------------
class ICDSAutoDeskApp:
    THEMES = {
        "light": {
            # Sidebar Navigation (Deep Sleek Navy)
            "SIDEBAR_BG": "#0F172A",          # Slate 900
            "SIDEBAR_BORDER": "#1E293B",      # Slate 800
            "NAV_ITEM_ACTIVE_BG": "#1E293B",  # Active item fill
            "NAV_ITEM_HOVER_BG": "#1E293B",   # Hover item fill
            "NAV_ITEM_ACTIVE_FG": "#38BDF8",  # Sky 400
            "NAV_ITEM_INACTIVE_FG": "#94A3B8",# Slate 400
            "NAV_ITEM_INDICATOR": "#38BDF8",  # Accent line
            
            # Main Canvas & Panels
            "CANVAS_BG": "#F1F5F9",           # Slate 100 soft neutral workspace
            "PANEL_BG": "#FFFFFF",            # Pure White card
            "PANEL_BORDER": "#E2E8F0",        # Crisp thin border
            "HEADER_BG": "#FFFFFF",           # Top header background
            "HEADER_BORDER": "#E2E8F0",       # Header border line
            
            # Typography
            "TEXT_TITLE": "#0F172A",          # Slate 900
            "TEXT_BODY": "#334155",           # Slate 700
            "TEXT_MUTED": "#64748B",          # Slate 500
            "TEXT_FAINT": "#94A3B8",          # Slate 400
            
            # Primary Brand Accents
            "BRAND_BLUE": "#2563EB",          # Blue 600
            "BRAND_BLUE_HOVER": "#1D4ED8",    # Blue 700
            "BRAND_GREEN": "#059669",         # Emerald 600
            "BRAND_GREEN_HOVER": "#047857",   # Emerald 700
            "BRAND_PURPLE": "#7C3AED",        # Violet 600
            "BRAND_PURPLE_HOVER": "#6D28D9",
            
            # Form Inputs
            "INPUT_BG": "#F8FAFC",            # Slate 50
            "INPUT_BORDER": "#CBD5E1",        # Slate 300
            "INPUT_FOCUS": "#3B82F6",         # Blue 500
            
            # Badge & Chips
            "BADGE_BG": "#EFF6FF",            # Blue 50
            "BADGE_FG": "#1D4ED8",            # Blue 700
            "BADGE_BORDER": "#DBEAFE",
            "SUCCESS_BG": "#ECFDF5",          # Emerald 50
            "SUCCESS_FG": "#047857",          # Emerald 700
            "SUCCESS_BORDER": "#A7F3D0",
            
            # Secondary Action Buttons
            "BTN_SEC_BG": "#F1F5F9",
            "BTN_SEC_HOVER": "#E2E8F0",
            "BTN_SEC_FG": "#334155",
            "BTN_SEC_BORDER": "#CBD5E1",
        },
        "dark": {
            # Sidebar Navigation (Deep Obsidian)
            "SIDEBAR_BG": "#090D16",          # Deepest Slate
            "SIDEBAR_BORDER": "#1E293B",
            "NAV_ITEM_ACTIVE_BG": "#1E293B",
            "NAV_ITEM_HOVER_BG": "#131C2E",
            "NAV_ITEM_ACTIVE_FG": "#38BDF8",
            "NAV_ITEM_INACTIVE_FG": "#64748B",
            "NAV_ITEM_INDICATOR": "#38BDF8",
            
            # Main Canvas & Panels
            "CANVAS_BG": "#0F172A",           # Slate 900
            "PANEL_BG": "#1E293B",            # Slate 800
            "PANEL_BORDER": "#334155",        # Slate 700
            "HEADER_BG": "#1E293B",           # Header background
            "HEADER_BORDER": "#334155",
            
            # Typography
            "TEXT_TITLE": "#F8FAFC",          # Slate 50
            "TEXT_BODY": "#CBD5E1",           # Slate 300
            "TEXT_MUTED": "#94A3B8",          # Slate 400
            "TEXT_FAINT": "#64748B",          # Slate 500
            
            # Primary Brand Accents
            "BRAND_BLUE": "#3B82F6",          # Blue 500
            "BRAND_BLUE_HOVER": "#60A5FA",    # Blue 400
            "BRAND_GREEN": "#10B981",         # Emerald 500
            "BRAND_GREEN_HOVER": "#34D399",
            "BRAND_PURPLE": "#8B5CF6",
            "BRAND_PURPLE_HOVER": "#A78BFA",
            
            # Form Inputs
            "INPUT_BG": "#0F172A",            # Deep Slate 900
            "INPUT_BORDER": "#475569",        # Slate 600
            "INPUT_FOCUS": "#60A5FA",
            
            # Badge & Chips
            "BADGE_BG": "#172554",            # Blue 950
            "BADGE_FG": "#93C5FD",            # Blue 300
            "BADGE_BORDER": "#1E40AF",
            "SUCCESS_BG": "#064E3B",          # Emerald 950
            "SUCCESS_FG": "#6EE7B7",          # Emerald 300
            "SUCCESS_BORDER": "#065F46",
            
            # Secondary Action Buttons
            "BTN_SEC_BG": "#334155",
            "BTN_SEC_HOVER": "#475569",
            "BTN_SEC_FG": "#F8FAFC",
            "BTN_SEC_BORDER": "#475569",
        },
    }

    def __init__(self, root):
        self.root = root
        self.root.title("ICDS AutoDesk — Automated Report Engine")

        # Enterprise desktop aspect ratio (880x620)
        window_width, window_height = 880, 620
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = int((sw - window_width) / 2)
        y = int((sh - window_height) / 2) - 30
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(820, 560)

        self.theme_mode = "light"
        self.current_screen = "home"
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

        # Build Master Layout (Sidebar + Topbar + Content Area)
        self._build_master_scaffold()

        # Render initial screen
        self._navigate_to("home")

        # Non-blocking background check for updates after 2.5s
        self.root.after(2500, lambda: check_for_updates_async(self.root, silent=True))

    # ------------------------------------------------------------------
    # Resource & Graphic Utilities
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
                img = Image.open(logo_path).resize((40, 40), Image.LANCZOS)
                self.logo_tk = ImageTk.PhotoImage(img)
        except Exception as e:
            print("Logo load failed:", e)

    def _create_rounded_image(self, width, height, bg_color, border_color=None, border_width=1, radius=8):
        """2x supersampled anti-aliased rounded rectangle with crisp rendering."""
        key = (width, height, bg_color, border_color, border_width, radius)
        if key in self._image_cache:
            return self._image_cache[key]

        scale = 2
        w_s, h_s, r_s = width * scale, height * scale, radius * scale
        img = Image.new("RGBA", (w_s, h_s), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if border_color and border_width > 0:
            draw.rounded_rectangle((0, 0, w_s, h_s), radius=r_s, fill=border_color)
            b_s = border_width * scale
            draw.rounded_rectangle((b_s, b_s, w_s - b_s, h_s - b_s), radius=max(0, r_s - b_s), fill=bg_color)
        else:
            draw.rounded_rectangle((0, 0, w_s, h_s), radius=r_s, fill=bg_color)

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

        style.configure(
            "Executive.TCombobox",
            fieldbackground=t["INPUT_BG"],
            background=t["PANEL_BG"],
            foreground=t["TEXT_TITLE"],
            arrowcolor=t["TEXT_MUTED"],
            bordercolor=t["INPUT_BORDER"],
            lightcolor=t["INPUT_BG"],
            darkcolor=t["INPUT_BG"],
            padding=5,
        )
        style.map(
            "Executive.TCombobox",
            fieldbackground=[("readonly", t["INPUT_BG"]), ("focus", t["PANEL_BG"])],
            bordercolor=[("focus", t["INPUT_FOCUS"])],
            arrowcolor=[("focus", t["BRAND_BLUE"])]
        )

    # ------------------------------------------------------------------
    # Master Application Scaffold (Sidebar + Topbar + Content Panel)
    # ------------------------------------------------------------------
    def _build_master_scaffold(self):
        t = self.THEMES[self.theme_mode]

        # 1. Sidebar Frame (Left column: 220px fixed)
        self.sidebar_frame = tk.Frame(self.root, bg=t["SIDEBAR_BG"], width=220)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # 2. Main Content Wrapper (Right column)
        self.main_wrapper = tk.Frame(self.root, bg=t["CANVAS_BG"])
        self.main_wrapper.pack(side="right", fill="both", expand=True)

        # 3. Top Header Bar inside Main Wrapper
        self.header_frame = tk.Frame(self.main_wrapper, bg=t["HEADER_BG"], height=52)
        self.header_frame.pack(side="top", fill="x")
        self.header_frame.pack_propagate(False)

        header_divider = tk.Frame(self.main_wrapper, bg=t["HEADER_BORDER"], height=1)
        header_divider.pack(side="top", fill="x")

        # 4. Dynamic Content Area
        self.content_container = tk.Frame(self.main_wrapper, bg=t["CANVAS_BG"])
        self.content_container.pack(fill="both", expand=True, padx=28, pady=24)

        # Populate persistent components
        self._render_sidebar()
        self._render_header()

    def _render_sidebar(self):
        """Builds clean professional enterprise sidebar."""
        t = self.THEMES[self.theme_mode]
        for w in self.sidebar_frame.winfo_children():
            w.destroy()

        # Brand Logo + Name Block
        brand_box = tk.Frame(self.sidebar_frame, bg=t["SIDEBAR_BG"], padx=16, pady=20)
        brand_box.pack(fill="x")

        if self.logo_tk:
            logo_l = tk.Label(brand_box, image=self.logo_tk, bg=t["SIDEBAR_BG"])
            logo_l.pack(side="left", padx=(0, 10))

        brand_text_box = tk.Frame(brand_box, bg=t["SIDEBAR_BG"])
        brand_text_box.pack(side="left")

        brand_name = tk.Label(
            brand_text_box, text="ICDS AutoDesk",
            font=("Segoe UI", 12, "bold"), fg="#FFFFFF", bg=t["SIDEBAR_BG"]
        )
        brand_name.pack(anchor="w")

        brand_edition = tk.Label(
            brand_text_box, text="Professional Edition",
            font=("Segoe UI", 8), fg=t["NAV_ITEM_INACTIVE_FG"], bg=t["SIDEBAR_BG"]
        )
        brand_edition.pack(anchor="w")

        # Subtle Divider
        sep = tk.Frame(self.sidebar_frame, bg=t["SIDEBAR_BORDER"], height=1)
        sep.pack(fill="x", padx=14, pady=(0, 14))

        # Navigation Label
        nav_lbl = tk.Label(
            self.sidebar_frame, text="CORE MODULES",
            font=("Segoe UI", 8, "bold"), fg="#475569", bg=t["SIDEBAR_BG"]
        )
        nav_lbl.pack(anchor="w", padx=20, pady=(0, 6))

        # Navigation Items
        self.nav_widgets = {}
        nav_items = [
            ("home", "⊞", "Dashboard Overview"),
            ("format", "◫", "Template Designer"),
            ("report", "⎘", "Report Generator"),
        ]

        for screen_id, icon_char, label_text in nav_items:
            self._create_nav_item(screen_id, icon_char, label_text)

        # Sidebar Bottom Section: System Status & Version
        btm_box = tk.Frame(self.sidebar_frame, bg=t["SIDEBAR_BG"], padx=16, pady=16)
        btm_box.pack(side="bottom", fill="x")

        status_card = tk.Frame(btm_box, bg="#131C2E", padx=12, pady=10)
        status_card.pack(fill="x")

        v_lbl = tk.Label(
            status_card, text=f"Installed: v{APP_VERSION}",
            font=("Segoe UI", 8, "bold"), fg="#38BDF8", bg="#131C2E"
        )
        v_lbl.pack(anchor="w")

        sync_lbl = tk.Label(
            status_card, text="● Cloud Auto-Sync Ready",
            font=("Segoe UI", 7), fg="#10B981", bg="#131C2E"
        )
        sync_lbl.pack(anchor="w", pady=(2, 0))

    def _create_nav_item(self, screen_id, icon_char, label_text):
        t = self.THEMES[self.theme_mode]
        is_active = (self.current_screen == screen_id)

        item_bg = t["NAV_ITEM_ACTIVE_BG"] if is_active else t["SIDEBAR_BG"]
        item_fg = t["NAV_ITEM_ACTIVE_FG"] if is_active else t["NAV_ITEM_INACTIVE_FG"]

        item_frame = tk.Frame(self.sidebar_frame, bg=item_bg, cursor="hand2")
        item_frame.pack(fill="x", padx=10, pady=2)

        # Active indicator strip on left
        indicator = tk.Frame(
            item_frame,
            bg=t["NAV_ITEM_INDICATOR"] if is_active else item_bg,
            width=3, height=36
        )
        indicator.pack(side="left")

        inner_box = tk.Frame(item_frame, bg=item_bg, padx=12, pady=8, cursor="hand2")
        inner_box.pack(side="left", fill="both", expand=True)

        icon_lbl = tk.Label(
            inner_box, text=icon_char, font=("Segoe UI", 11),
            fg=item_fg, bg=item_bg, cursor="hand2"
        )
        icon_lbl.pack(side="left", padx=(0, 10))

        text_lbl = tk.Label(
            inner_box, text=label_text, font=("Segoe UI", 9, "bold" if is_active else "normal"),
            fg=item_fg, bg=item_bg, cursor="hand2"
        )
        text_lbl.pack(side="left")

        def on_click():
            self._navigate_to(screen_id)

        def on_enter(_):
            if self.current_screen != screen_id:
                item_frame.configure(bg=t["NAV_ITEM_HOVER_BG"])
                inner_box.configure(bg=t["NAV_ITEM_HOVER_BG"])
                icon_lbl.configure(bg=t["NAV_ITEM_HOVER_BG"], fg="#FFFFFF")
                text_lbl.configure(bg=t["NAV_ITEM_HOVER_BG"], fg="#FFFFFF")

        def on_leave(_):
            if self.current_screen != screen_id:
                item_frame.configure(bg=t["SIDEBAR_BG"])
                inner_box.configure(bg=t["SIDEBAR_BG"])
                icon_lbl.configure(bg=t["SIDEBAR_BG"], fg=t["NAV_ITEM_INACTIVE_FG"])
                text_lbl.configure(bg=t["SIDEBAR_BG"], fg=t["NAV_ITEM_INACTIVE_FG"])

        for w in (item_frame, inner_box, icon_lbl, text_lbl, indicator):
            w.bind("<Button-1>", lambda e: on_click())
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        self.nav_widgets[screen_id] = (item_frame, inner_box, icon_lbl, text_lbl, indicator)

    def _render_header(self):
        """Top bar with breadcrumb trail, update button, and theme switcher."""
        t = self.THEMES[self.theme_mode]
        for w in self.header_frame.winfo_children():
            w.destroy()

        h_inner = tk.Frame(self.header_frame, bg=t["HEADER_BG"], padx=20)
        h_inner.pack(fill="both", expand=True)

        # Breadcrumbs
        bread_title = "Dashboard Overview"
        if self.current_screen == "format":
            bread_title = "Template Designer"
        elif self.current_screen == "report":
            bread_title = "Report Generator"
        elif self.current_screen == "download":
            bread_title = "Export Summary"

        bread_box = tk.Frame(h_inner, bg=t["HEADER_BG"])
        bread_box.pack(side="left", fill="y")

        app_lbl = tk.Label(
            bread_box, text="Workspace",
            font=("Segoe UI", 9), fg=t["TEXT_FAINT"], bg=t["HEADER_BG"]
        )
        app_lbl.pack(side="left")

        slash_lbl = tk.Label(
            bread_box, text=" / ",
            font=("Segoe UI", 9), fg=t["TEXT_FAINT"], bg=t["HEADER_BG"]
        )
        slash_lbl.pack(side="left")

        curr_lbl = tk.Label(
            bread_box, text=bread_title,
            font=("Segoe UI", 9, "bold"), fg=t["TEXT_TITLE"], bg=t["HEADER_BG"]
        )
        curr_lbl.pack(side="left")

        # Right Controls: Check Updates & Theme Mode
        actions_box = tk.Frame(h_inner, bg=t["HEADER_BG"])
        actions_box.pack(side="right", fill="y")

        update_btn = tk.Button(
            actions_box,
            text="↻ Check Updates",
            font=("Segoe UI", 8, "bold"),
            bg=t["BTN_SEC_BG"],
            fg=t["BTN_SEC_FG"],
            activebackground=t["BTN_SEC_HOVER"],
            activeforeground=t["BTN_SEC_FG"],
            relief="flat",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=lambda: check_for_updates_async(self.root, silent=False)
        )
        update_btn.pack(side="left", padx=(0, 12))

        # Theme Switch Pill
        self._render_theme_switch(actions_box)

    def _render_theme_switch(self, parent):
        t = self.THEMES[self.theme_mode]
        sw_w, sw_h = 44, 22
        knob_d = 16
        pad = 3
        canvas = tk.Canvas(
            parent, width=sw_w, height=sw_h, bd=0,
            highlightthickness=0, bg=t["HEADER_BG"], cursor="hand2"
        )
        canvas.pack(side="right")

        knob_x = pad if self.theme_mode == "light" else sw_w - knob_d - pad
        track_color = "#E2E8F0" if self.theme_mode == "light" else "#334155"

        canvas.create_oval(0, 0, sw_h, sw_h, fill=track_color, outline=track_color)
        canvas.create_oval(sw_w - sw_h, 0, sw_w, sw_h, fill=track_color, outline=track_color)
        canvas.create_rectangle(sw_h // 2, 0, sw_w - (sw_h // 2), sw_h, fill=track_color, outline=track_color)

        knob_fill = "#FFFFFF" if self.theme_mode == "light" else "#F1F5F9"
        canvas.create_oval(knob_x, pad, knob_x + knob_d, pad + knob_d, fill=knob_fill, outline="#CBD5E1")

        def toggle(_):
            self.theme_mode = "dark" if self.theme_mode == "light" else "light"
            self._image_cache.clear()
            self._rebuild_all_views()

        canvas.bind("<Button-1>", toggle)

    def _rebuild_all_views(self):
        t = self.THEMES[self.theme_mode]
        self.root.configure(bg=t["CANVAS_BG"])
        self.sidebar_frame.configure(bg=t["SIDEBAR_BG"])
        self.main_wrapper.configure(bg=t["CANVAS_BG"])
        self.header_frame.configure(bg=t["HEADER_BG"])
        self.content_container.configure(bg=t["CANVAS_BG"])

        self._style_ttk_for_theme()
        self._render_sidebar()
        self._render_header()
        self._render_current_screen()

    def _navigate_to(self, screen_id):
        self.current_screen = screen_id
        self._render_sidebar()
        self._render_header()
        self._render_current_screen()

    def _render_current_screen(self):
        for w in self.content_container.winfo_children():
            w.destroy()

        if self.current_screen == "home":
            self._build_home_view()
        elif self.current_screen == "format":
            self._build_format_view()
        elif self.current_screen == "report":
            self._build_report_view()
        elif self.current_screen == "download":
            self._build_download_view()

    # ------------------------------------------------------------------
    # Screen 1: Executive Dashboard (Home View)
    # ------------------------------------------------------------------
    def _build_home_view(self):
        t = self.THEMES[self.theme_mode]

        # View Header
        header_box = tk.Frame(self.content_container, bg=t["CANVAS_BG"])
        header_box.pack(fill="x", pady=(0, 20))

        v_title = tk.Label(
            header_box, text="Integrated Child Development Services (ICDS)",
            font=("Segoe UI", 16, "bold"), fg=t["TEXT_TITLE"], bg=t["CANVAS_BG"]
        )
        v_title.pack(anchor="w")

        v_sub = tk.Label(
            header_box,
            text="Centralized desktop utility for automated monthly schedule generation and daily attendance-stock reconciliation.",
            font=("Segoe UI", 10), fg=t["TEXT_MUTED"], bg=t["CANVAS_BG"]
        )
        v_sub.pack(anchor="w", pady=(3, 0))

        # Workflow Cards Grid (2 Horizontal Enterprise Cards)
        cards_frame = tk.Frame(self.content_container, bg=t["CANVAS_BG"])
        cards_frame.pack(fill="x", pady=(0, 16))

        # Card 1: Template Format Module
        c1 = self._build_executive_card(
            cards_frame,
            icon_tag="01",
            icon_color=t["BRAND_GREEN"],
            title="Monthly Template Designer",
            description="Generate pristine, standardized monthly Excel workbooks pre-formatted with calendar dates, Sundays, and regional public holidays.",
            features=[
                "Automatic date-to-day mapping",
                "Optional Polio campaign Sunday scheduling",
                "Built-in attendance & daily ration formulas"
            ],
            btn_text="Launch Template Designer ➔",
            btn_color=t["BRAND_GREEN"],
            btn_hover=t["BRAND_GREEN_HOVER"],
            command=lambda: self._navigate_to("format")
        )
        c1.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Card 2: Report Generator Module
        c2 = self._build_executive_card(
            cards_frame,
            icon_tag="02",
            icon_color=t["BRAND_BLUE"],
            title="Report Generation Engine",
            description="Process completed field data from Anganwadi workers, compute total monthly meal allocations, and generate certified distribution reports.",
            features=[
                "Automatic validation of beneficiary records",
                "Accurate rice, dal, oil & egg balance calculation",
                "Instant single-click Excel export"
            ],
            btn_text="Launch Report Generator ➔",
            btn_color=t["BRAND_BLUE"],
            btn_hover=t["BRAND_BLUE_HOVER"],
            command=lambda: self._navigate_to("report")
        )
        c2.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # System Information Strip
        info_panel = tk.Frame(self.content_container, bg=t["PANEL_BG"], padx=18, pady=12, highlightthickness=1, highlightbackground=t["PANEL_BORDER"])
        info_panel.pack(fill="x", pady=(10, 0))

        ip_left = tk.Frame(info_panel, bg=t["PANEL_BG"])
        ip_left.pack(side="left")

        tip_lbl = tk.Label(
            ip_left, text="💡 Quick Tip:",
            font=("Segoe UI", 9, "bold"), fg=t["TEXT_TITLE"], bg=t["PANEL_BG"]
        )
        tip_lbl.pack(side="left", padx=(0, 6))

        tip_txt = tk.Label(
            ip_left,
            text="First design your monthly template in Module 01, fill beneficiary figures, then process in Module 02.",
            font=("Segoe UI", 9), fg=t["TEXT_MUTED"], bg=t["PANEL_BG"]
        )
        tip_txt.pack(side="left")

    def _build_executive_card(self, parent, icon_tag, icon_color, title, description, features, btn_text, btn_color, btn_hover, command):
        """Constructs a clean professional card with subtle borders and clear typography."""
        t = self.THEMES[self.theme_mode]

        card = tk.Frame(
            parent, bg=t["PANEL_BG"], padx=20, pady=20,
            highlightthickness=1, highlightbackground=t["PANEL_BORDER"]
        )

        # Header tag + Title
        h_box = tk.Frame(card, bg=t["PANEL_BG"])
        h_box.pack(fill="x", pady=(0, 8))

        tag_lbl = tk.Label(
            h_box, text=f"MODULE {icon_tag}",
            font=("Segoe UI", 8, "bold"), fg=icon_color, bg=t["PANEL_BG"]
        )
        tag_lbl.pack(anchor="w")

        title_lbl = tk.Label(
            h_box, text=title,
            font=("Segoe UI", 12, "bold"), fg=t["TEXT_TITLE"], bg=t["PANEL_BG"]
        )
        title_lbl.pack(anchor="w", pady=(2, 0))

        desc_lbl = tk.Label(
            card, text=description,
            font=("Segoe UI", 9), fg=t["TEXT_BODY"], bg=t["PANEL_BG"],
            wraplength=270, justify="left"
        )
        desc_lbl.pack(anchor="w", pady=(0, 14))

        # Bullet Feature Points
        feat_box = tk.Frame(card, bg=t["PANEL_BG"])
        feat_box.pack(fill="x", pady=(0, 16))

        for feat in features:
            f_row = tk.Frame(feat_box, bg=t["PANEL_BG"])
            f_row.pack(fill="x", pady=2)

            bullet = tk.Label(
                f_row, text="✓", font=("Segoe UI", 8, "bold"),
                fg=icon_color, bg=t["PANEL_BG"]
            )
            bullet.pack(side="left", padx=(0, 6))

            f_txt = tk.Label(
                f_row, text=feat, font=("Segoe UI", 8),
                fg=t["TEXT_MUTED"], bg=t["PANEL_BG"],
                wraplength=250, justify="left"
            )
            f_txt.pack(side="left")

        # Action Button
        btn = self._build_solid_button(
            card, text=btn_text, command=command,
            bg_color=btn_color, hover_color=btn_hover,
            width=240, height=36
        )
        btn.pack(anchor="w", fill="x")

        return card

    # ------------------------------------------------------------------
    # Screen 2: Template Designer View
    # ------------------------------------------------------------------
    def _build_format_view(self):
        t = self.THEMES[self.theme_mode]

        # View Header
        header_box = tk.Frame(self.content_container, bg=t["CANVAS_BG"])
        header_box.pack(fill="x", pady=(0, 18))

        v_title = tk.Label(
            header_box, text="Monthly Report Template Designer",
            font=("Segoe UI", 15, "bold"), fg=t["TEXT_TITLE"], bg=t["CANVAS_BG"]
        )
        v_title.pack(anchor="w")

        v_sub = tk.Label(
            header_box,
            text="Configure month and year parameters to automatically produce an official ICDS blank data entry template.",
            font=("Segoe UI", 9), fg=t["TEXT_MUTED"], bg=t["CANVAS_BG"]
        )
        v_sub.pack(anchor="w", pady=(2, 0))

        # Form Card Panel
        form_panel = tk.Frame(
            self.content_container, bg=t["PANEL_BG"], padx=24, pady=24,
            highlightthickness=1, highlightbackground=t["PANEL_BORDER"]
        )
        form_panel.pack(fill="x", pady=(0, 16))

        grid_box = tk.Frame(form_panel, bg=t["PANEL_BG"])
        grid_box.pack(fill="x", pady=(0, 16))

        # Month Selector
        m_lbl = tk.Label(
            grid_box, text="Target Month *",
            font=("Segoe UI", 9, "bold"), fg=t["TEXT_TITLE"], bg=t["PANEL_BG"]
        )
        m_lbl.grid(row=0, column=0, sticky="w", pady=(0, 4), padx=(0, 20))

        self.month_var = tk.StringVar()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        month_cb = ttk.Combobox(
            grid_box, textvariable=self.month_var, values=months,
            state="readonly", width=22, style="Executive.TCombobox"
        )
        month_cb.grid(row=1, column=0, sticky="w", pady=(0, 16), padx=(0, 20))
        month_cb.bind("<<ComboboxSelected>>", lambda e: self._update_polio_sundays())

        # Year Selector
        y_lbl = tk.Label(
            grid_box, text="Target Year *",
            font=("Segoe UI", 9, "bold"), fg=t["TEXT_TITLE"], bg=t["PANEL_BG"]
        )
        y_lbl.grid(row=0, column=1, sticky="w", pady=(0, 4))

        self.year_var = tk.StringVar()
        years = [str(y) for y in range(2024, 2101)]
        year_cb = ttk.Combobox(
            grid_box, textvariable=self.year_var, values=years,
            state="readonly", width=22, style="Executive.TCombobox"
        )
        year_cb.grid(row=1, column=1, sticky="w", pady=(0, 16))
        year_cb.bind("<<ComboboxSelected>>", lambda e: self._update_polio_sundays())

        # Polio Campaign Checkbox
        self.include_polio = tk.BooleanVar(value=False)
        self.polio_check = tk.Checkbutton(
            grid_box,
            text="Mark Special National Immunization / Polio Campaign Sunday",
            variable=self.include_polio,
            command=self._toggle_polio_day,
            fg=t["TEXT_TITLE"],
            bg=t["PANEL_BG"],
            selectcolor=t["PANEL_BG"],
            activebackground=t["PANEL_BG"],
            font=("Segoe UI", 9),
            state="disabled",
            cursor="hand2"
        )
        self.polio_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 8))

        # Dynamic Polio Sunday Dropdown Row
        self.polio_container = tk.Frame(grid_box, bg=t["PANEL_BG"])
        self.polio_day_label = tk.Label(
            self.polio_container, text="Select Scheduled Sunday:",
            font=("Segoe UI", 9, "bold"), fg=t["TEXT_TITLE"], bg=t["PANEL_BG"]
        )
        self.polio_day_label.pack(side="left", padx=(0, 10))

        self.polio_day_var = tk.StringVar()
        self.polio_day_cb = ttk.Combobox(
            self.polio_container, textvariable=self.polio_day_var,
            state="readonly", width=18, style="Executive.TCombobox"
        )
        self.polio_day_cb.pack(side="left")

        # Action Buttons Row
        actions_row = tk.Frame(form_panel, bg=t["PANEL_BG"])
        actions_row.pack(fill="x", pady=(10, 0))

        gen_btn = self._build_solid_button(
            actions_row, text="Generate Template Workbook", command=self._generate_format,
            bg_color=t["BRAND_GREEN"], hover_color=t["BRAND_GREEN_HOVER"],
            width=220, height=36
        )
        gen_btn.pack(side="left", padx=(0, 10))

        back_btn = self._build_outline_button(
            actions_row, text="← Return to Dashboard",
            command=lambda: self._navigate_to("home"),
            width=160, height=36
        )
        back_btn.pack(side="left")

    def _toggle_polio_day(self):
        if self.include_polio.get():
            self._update_polio_sundays()
            self.polio_container.grid(row=3, column=0, columnspan=2, sticky="w", pady=(4, 8))
        else:
            self.polio_container.grid_forget()

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
                messagebox.showerror("Validation Notice", "Please select a target month.")
                return
            month_num = ["January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"].index(month_name) + 1

            if not self.year_var.get():
                messagebox.showerror("Validation Notice", "Please select a target year.")
                return
            year = int(self.year_var.get())

            polio_day = int(self.polio_day_var.get()) if (self.include_polio.get() and self.polio_day_var.get()) else None

            temp_folder = os.path.join(os.getcwd(), "temp_generated")
            os.makedirs(temp_folder, exist_ok=True)

            Format_Generator(month_num, year, polio_day, temp_folder)

            self.generated_file_path = None
            for f in os.listdir(temp_folder):
                self.generated_file_path = os.path.join(temp_folder, f)

            self.download_file_type = "Monthly Report Template"
            self._navigate_to("download")
        except Exception as e:
            messagebox.showerror("Generation Error", str(e))

    # ------------------------------------------------------------------
    # Screen 3: Report Generator View
    # ------------------------------------------------------------------
    def _build_report_view(self):
        t = self.THEMES[self.theme_mode]

        # View Header
        header_box = tk.Frame(self.content_container, bg=t["CANVAS_BG"])
        header_box.pack(fill="x", pady=(0, 18))

        v_title = tk.Label(
            header_box, text="Report Generation & Calculation Engine",
            font=("Segoe UI", 15, "bold"), fg=t["TEXT_TITLE"], bg=t["CANVAS_BG"]
        )
        v_title.pack(anchor="w")

        v_sub = tk.Label(
            header_box,
            text="Upload completed monthly Excel data to reconcile food consumption, calculate stocks, and generate verified balance sheets.",
            font=("Segoe UI", 9), fg=t["TEXT_MUTED"], bg=t["CANVAS_BG"]
        )
        v_sub.pack(anchor="w", pady=(2, 0))

        # Main Panel
        panel = tk.Frame(
            self.content_container, bg=t["PANEL_BG"], padx=24, pady=24,
            highlightthickness=1, highlightbackground=t["PANEL_BORDER"]
        )
        panel.pack(fill="x", pady=(0, 16))

        # File Dropzone Box
        drop_box = tk.Frame(
            panel, bg=t["INPUT_BG"], padx=24, pady=24,
            highlightthickness=1, highlightbackground=t["INPUT_BORDER"]
        )
        drop_box.pack(fill="x", pady=(0, 16))

        icon_file = tk.Label(
            drop_box, text="⎘", font=("Segoe UI", 28),
            fg=t["BRAND_BLUE"], bg=t["INPUT_BG"]
        )
        icon_file.pack()

        inst_l = tk.Label(
            drop_box, text="Select Completed Excel Data File (*.xlsx)",
            font=("Segoe UI", 11, "bold"), fg=t["TEXT_TITLE"], bg=t["INPUT_BG"]
        )
        inst_l.pack(pady=(4, 2))

        inst_sub = tk.Label(
            drop_box, text="File naming standard: Month_Year_Report_Format.xlsx (e.g. September_2025_Report_Format.xlsx)",
            font=("Segoe UI", 8), fg=t["TEXT_MUTED"], bg=t["INPUT_BG"]
        )
        inst_sub.pack(pady=(0, 12))

        browse_btn = self._build_solid_button(
            drop_box, text="Browse Local Drive...",
            command=lambda: self._select_file(drop_box, browse_btn),
            bg_color=t["BRAND_BLUE"], hover_color=t["BRAND_BLUE_HOVER"],
            width=180, height=32
        )
        browse_btn.pack()

        # Selection Status Label placeholder
        self.file_status_label = tk.Label(
            drop_box, text="No file selected yet.",
            font=("Segoe UI", 9, "italic"), fg=t["TEXT_FAINT"], bg=t["INPUT_BG"]
        )
        self.file_status_label.pack(pady=(10, 0))

        # Action Buttons
        actions_row = tk.Frame(panel, bg=t["PANEL_BG"])
        actions_row.pack(fill="x", pady=(8, 0))

        proc_btn = self._build_solid_button(
            actions_row, text="⚡ Process & Build Final Report",
            command=self._generate_report_from_file,
            bg_color=t["BRAND_BLUE"], hover_color=t["BRAND_BLUE_HOVER"],
            width=240, height=36
        )
        proc_btn.pack(side="left", padx=(0, 10))

        back_btn = self._build_outline_button(
            actions_row, text="← Return to Dashboard",
            command=lambda: self._navigate_to("home"),
            width=160, height=36
        )
        back_btn.pack(side="left")

    def _select_file(self, parent_widget, after_widget):
        self.report_file_path = None
        self.generated_file_path = None

        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not path:
            return

        filename = os.path.basename(path)
        pattern = r"^(January|February|March|April|May|June|July|August|September|October|November|December)_(\d{4})_Report_Format\.xlsx$"

        if not re.match(pattern, filename):
            messagebox.showerror(
                "File Validation Notice",
                "Selected file does not match required ICDS format.\n\nExpected pattern:\nMonth_Year_Report_Format.xlsx\n(e.g., September_2025_Report_Format.xlsx)",
            )
            return

        self.report_file_path = path
        t = self.THEMES[self.theme_mode]
        self.file_status_label.config(
            text=f"✓ Ready: {filename}",
            fg=t["BRAND_GREEN"],
            font=("Segoe UI", 9, "bold")
        )

    def _generate_report_from_file(self):
        if not getattr(self, "report_file_path", None):
            messagebox.showerror("File Required", "Please select and verify an Excel data file first.")
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

            self.download_file_type = "Reconciled Final Report"
            self._navigate_to("download")
        except Exception as e:
            messagebox.showerror("Processing Exception", str(e))

    # ------------------------------------------------------------------
    # Screen 4: Download / Export Summary View
    # ------------------------------------------------------------------
    def _build_download_view(self):
        t = self.THEMES[self.theme_mode]
        file_desc = getattr(self, "download_file_type", "Document")

        header_box = tk.Frame(self.content_container, bg=t["CANVAS_BG"])
        header_box.pack(fill="x", pady=(0, 18))

        v_title = tk.Label(
            header_box, text="Processing Complete",
            font=("Segoe UI", 15, "bold"), fg=t["TEXT_TITLE"], bg=t["CANVAS_BG"]
        )
        v_title.pack(anchor="w")

        v_sub = tk.Label(
            header_box,
            text=f"Your {file_desc} has been generated with verified formulas and formatted schemas.",
            font=("Segoe UI", 9), fg=t["TEXT_MUTED"], bg=t["CANVAS_BG"]
        )
        v_sub.pack(anchor="w", pady=(2, 0))

        # Summary Card
        card = tk.Frame(
            self.content_container, bg=t["PANEL_BG"], padx=24, pady=24,
            highlightthickness=1, highlightbackground=t["PANEL_BORDER"]
        )
        card.pack(fill="x", pady=(0, 16))

        # Success Banner Box
        banner = tk.Frame(
            card, bg=t["SUCCESS_BG"], padx=18, pady=16,
            highlightthickness=1, highlightbackground=t["SUCCESS_BORDER"]
        )
        banner.pack(fill="x", pady=(0, 20))

        fname = os.path.basename(self.generated_file_path) if self.generated_file_path else "Generated File.xlsx"

        s_head = tk.Label(
            banner, text="✓ GENERATION COMPLETED SUCCESSFULLY",
            font=("Segoe UI", 9, "bold"), fg=t["SUCCESS_FG"], bg=t["SUCCESS_BG"]
        )
        s_head.pack(anchor="w")

        s_f = tk.Label(
            banner, text=f"Output File: {fname}",
            font=("Segoe UI", 11, "bold"), fg=t["TEXT_TITLE"], bg=t["SUCCESS_BG"]
        )
        s_f.pack(anchor="w", pady=(4, 0))

        # Actions
        actions_row = tk.Frame(card, bg=t["PANEL_BG"])
        actions_row.pack(fill="x")

        save_btn = self._build_solid_button(
            actions_row, text="💾 Save / Export to Folder...",
            command=self._download_file,
            bg_color=t["BRAND_GREEN"], hover_color=t["BRAND_GREEN_HOVER"],
            width=220, height=36
        )
        save_btn.pack(side="left", padx=(0, 10))

        home_btn = self._build_outline_button(
            actions_row, text="← Return to Dashboard",
            command=lambda: self._navigate_to("home"),
            width=180, height=36
        )
        home_btn.pack(side="left")

    def _download_file(self):
        if not self.generated_file_path:
            messagebox.showerror("Error", "No output file found to export.")
            return

        folder = filedialog.askdirectory(title="Select Destination Folder")
        if not folder:
            return

        try:
            dest = os.path.join(folder, os.path.basename(self.generated_file_path))
            shutil.copy2(self.generated_file_path, dest)
            messagebox.showinfo("Export Confirmed", f"File saved successfully to:\n\n{dest}")
        except Exception as e:
            messagebox.showerror("File Error", str(e))

        self._clear_temp_folders()

    # ------------------------------------------------------------------
    # Custom Modern Button Builders (Anti-aliased & Hover-responsive)
    # ------------------------------------------------------------------
    def _build_solid_button(self, parent, text, command, bg_color, hover_color, width=220, height=36):
        normal_img = self._create_rounded_image(width, height, bg_color=bg_color, radius=6)
        hover_img = self._create_rounded_image(width, height, bg_color=hover_color, radius=6)

        wrapper = tk.Frame(parent, bg=parent["bg"], cursor="hand2")
        lbl = tk.Label(wrapper, image=normal_img, bg=parent["bg"], bd=0, cursor="hand2")
        lbl.image_normal = normal_img
        lbl.image_hover = hover_img
        lbl.pack()

        txt = tk.Label(
            lbl, text=text, font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF", bg=bg_color, cursor="hand2"
        )
        txt.place(relx=0.5, rely=0.5, anchor="center")

        def on_enter(_):
            lbl.configure(image=hover_img)
            txt.configure(bg=hover_color)

        def on_leave(_):
            lbl.configure(image=normal_img)
            txt.configure(bg=bg_color)

        for w in (lbl, txt):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", lambda e: command())

        return wrapper

    def _build_outline_button(self, parent, text, command, width=160, height=36):
        t = self.THEMES[self.theme_mode]
        normal_img = self._create_rounded_image(
            width, height, bg_color=t["PANEL_BG"], border_color=t["BTN_SEC_BORDER"], border_width=1, radius=6
        )
        hover_img = self._create_rounded_image(
            width, height, bg_color=t["BTN_SEC_HOVER"], border_color=t["BTN_SEC_BORDER"], border_width=1, radius=6
        )

        wrapper = tk.Frame(parent, bg=parent["bg"], cursor="hand2")
        lbl = tk.Label(wrapper, image=normal_img, bg=parent["bg"], bd=0, cursor="hand2")
        lbl.image_normal = normal_img
        lbl.image_hover = hover_img
        lbl.pack()

        txt = tk.Label(
            lbl, text=text, font=("Segoe UI", 9, "bold"),
            fg=t["BTN_SEC_FG"], bg=t["PANEL_BG"], cursor="hand2"
        )
        txt.place(relx=0.5, rely=0.5, anchor="center")

        def on_enter(_):
            lbl.configure(image=hover_img)
            txt.configure(bg=t["BTN_SEC_HOVER"])

        def on_leave(_):
            lbl.configure(image=normal_img)
            txt.configure(bg=t["PANEL_BG"])

        for w in (lbl, txt):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", lambda e: command())

        return wrapper

    def _clear_temp_folders(self):
        for folder in ("temp_generated", "temp_generated_report"):
            path = os.path.join(os.getcwd(), folder)
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    print(f"Error clearing {folder}: {e}")


# ----------------------------------------------------------------------
# Application Bootstrap
# ----------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ICDSAutoDeskApp(root)
    root.mainloop()
