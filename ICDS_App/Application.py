# Applicatin.py
# ICDS AutoDesk — Modern Executive Desktop Suite (CustomTkinter)

import os
import sys
import re
import math
import shutil
import calendar
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
import customtkinter as ctk

from Main_Func import Format_Generator, Report_Generator_py
from updater import check_for_updates_async, APP_VERSION

# ----------------------------------------------------------------------
# Modern CustomTkinter Base Configuration
# ----------------------------------------------------------------------
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller exe"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ICDSAutoDeskApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure Window
        self.title("ICDS AutoDesk — Professional Report Engine")
        window_width, window_height = 960, 640
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = int((sw - window_width) / 2)
        y = int((sh - window_height) / 2) - 30
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(900, 600)

        # Application Icon
        try:
            self.iconbitmap(resource_path("icon.ico"))
        except Exception:
            try:
                self.iconbitmap(resource_path("app_icon.ico"))
            except Exception:
                pass

        # Load Logo for Sidebar
        self.logo_image = None
        self._load_logo()

        # Temporary files management
        self._clear_temp_folders()

        # State Variables
        self.current_screen = "home"
        self.generated_file_path = None
        self.report_file_path = None
        self.download_file_type = "Monthly Report"

        # Build Master UI Grid Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_content_area()

        # Start on Dashboard
        self.navigate_to("home")

        # Non-blocking Update Check after 2.5s
        self.after(2500, lambda: check_for_updates_async(self, silent=True))

    def _load_logo(self):
        try:
            logo_path = resource_path("logo.png")
            if os.path.exists(logo_path):
                pil_img = Image.open(logo_path)
                self.logo_image = ctk.CTkImage(
                    light_image=pil_img,
                    dark_image=pil_img,
                    size=(36, 36)
                )
        except Exception as e:
            print("Logo load failed:", e)

    # ------------------------------------------------------------------
    # Sidebar Navigation Component
    # ------------------------------------------------------------------
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=("gray92", "#0B1120")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        # Brand Header in Sidebar
        brand_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_box.grid(row=0, column=0, padx=20, pady=(24, 20), sticky="w")

        if self.logo_image:
            logo_lbl = ctk.CTkLabel(brand_box, image=self.logo_image, text="")
            logo_lbl.pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(brand_box, fg_color="transparent")
        title_box.pack(side="left")

        app_title = ctk.CTkLabel(
            title_box,
            text="ICDS AutoDesk",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        )
        app_title.pack(anchor="w")

        app_sub = ctk.CTkLabel(
            title_box,
            text="Executive Edition",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=("gray45", "gray60")
        )
        app_sub.pack(anchor="w")

        # Navigation Label
        nav_lbl = ctk.CTkLabel(
            self.sidebar,
            text="WORKSPACE MODULES",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=("gray50", "gray55")
        )
        nav_lbl.grid(row=1, column=0, padx=20, pady=(10, 8), sticky="w")

        # Nav Buttons
        self.nav_buttons = {}

        self.nav_buttons["home"] = ctk.CTkButton(
            self.sidebar,
            text="  ⊞   Dashboard",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            corner_radius=8,
            fg_color="transparent",
            text_color=("gray20", "gray85"),
            hover_color=("gray85", "#1E293B"),
            command=lambda: self.navigate_to("home")
        )
        self.nav_buttons["home"].grid(row=2, column=0, padx=14, pady=3, sticky="ew")

        self.nav_buttons["format"] = ctk.CTkButton(
            self.sidebar,
            text="  ◫   Template Designer",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            corner_radius=8,
            fg_color="transparent",
            text_color=("gray20", "gray85"),
            hover_color=("gray85", "#1E293B"),
            command=lambda: self.navigate_to("format")
        )
        self.nav_buttons["format"].grid(row=3, column=0, padx=14, pady=3, sticky="ew")

        self.nav_buttons["report"] = ctk.CTkButton(
            self.sidebar,
            text="  ⎘   Report Generator",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            corner_radius=8,
            fg_color="transparent",
            text_color=("gray20", "gray85"),
            hover_color=("gray85", "#1E293B"),
            command=lambda: self.navigate_to("report")
        )
        self.nav_buttons["report"].grid(row=4, column=0, padx=14, pady=3, sticky="ew")

        # Bottom System Card in Sidebar
        status_card = ctk.CTkFrame(
            self.sidebar,
            corner_radius=10,
            fg_color=("gray88", "#111827")
        )
        status_card.grid(row=6, column=0, padx=14, pady=16, sticky="ew")

        ver_lbl = ctk.CTkLabel(
            status_card,
            text=f"Version: v{APP_VERSION}",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#2563EB", "#38BDF8")
        )
        ver_lbl.pack(anchor="w", padx=12, pady=(10, 2))

        sync_lbl = ctk.CTkLabel(
            status_card,
            text="● Auto-Update Online",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=("#059669", "#10B981")
        )
        sync_lbl.pack(anchor="w", padx=12, pady=(0, 6))

        # Developer & Organization Attribution
        dev_lbl = ctk.CTkLabel(
            status_card,
            text="Dev: Muhammad Noukhez\nOrg: CodeX404 Solutions\ncodex404solutions.com",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=("gray40", "gray55"),
            justify="left"
        )
        dev_lbl.pack(anchor="w", padx=12, pady=(0, 10))

    # ------------------------------------------------------------------
    # Content Area with Top Header
    # ------------------------------------------------------------------
    def _build_content_area(self):
        self.content_wrapper = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray96", "#0F172A"))
        self.content_wrapper.grid(row=0, column=1, sticky="nsew")
        self.content_wrapper.grid_rowconfigure(1, weight=1)
        self.content_wrapper.grid_columnconfigure(0, weight=1)

        # Header Navbar
        self.header = ctk.CTkFrame(
            self.content_wrapper,
            height=54,
            corner_radius=0,
            fg_color=("white", "#1E293B")
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)

        # Breadcrumbs on Header Left
        self.breadcrumb_lbl = ctk.CTkLabel(
            self.header,
            text="Workspace / Dashboard",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("gray20", "gray85")
        )
        self.breadcrumb_lbl.pack(side="left", padx=24, pady=12)

        # Top Right Controls: Theme switch and Updates
        controls_box = ctk.CTkFrame(self.header, fg_color="transparent")
        controls_box.pack(side="right", padx=20, pady=10)

        update_btn = ctk.CTkButton(
            controls_box,
            text="↻ Check Updates",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            width=120,
            height=30,
            corner_radius=6,
            fg_color=("gray90", "gray25"),
            text_color=("gray15", "gray95"),
            hover_color=("gray80", "gray35"),
            command=lambda: check_for_updates_async(self, silent=False)
        )
        update_btn.pack(side="left", padx=(0, 10))

        # Modern Mode Switch
        self.theme_switch = ctk.CTkSwitch(
            controls_box,
            text="Dark Mode",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=self._toggle_theme,
            onvalue="Dark",
            offvalue="Light"
        )
        if ctk.get_appearance_mode() == "Dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()
        self.theme_switch.pack(side="left")

        # Dynamic Viewport Container
        self.viewport = ctk.CTkScrollableFrame(
            self.content_wrapper,
            corner_radius=0,
            fg_color="transparent"
        )
        self.viewport.grid(row=1, column=0, sticky="nsew", padx=24, pady=20)
        self.viewport.grid_columnconfigure(0, weight=1)

    def _toggle_theme(self):
        new_mode = "Dark" if self.theme_switch.get() == "Dark" else "Light"
        ctk.set_appearance_mode(new_mode)

    def navigate_to(self, screen_id: str):
        self.current_screen = screen_id

        # Update Sidebar Nav Active States
        for key, btn in self.nav_buttons.items():
            if key == screen_id:
                btn.configure(
                    fg_color=("#2563EB", "#1E3A8A"),
                    text_color="#FFFFFF"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray20", "gray85")
                )

        # Update Breadcrumb
        titles = {
            "home": "Workspace / Dashboard Overview",
            "format": "Workspace / Monthly Template Designer",
            "report": "Workspace / Report Calculation Engine",
            "download": "Workspace / Document Export Ready",
        }
        self.breadcrumb_lbl.configure(text=titles.get(screen_id, "Workspace"))

        # Clear and render screen
        for widget in self.viewport.winfo_children():
            widget.destroy()

        if screen_id == "home":
            self._render_home()
        elif screen_id == "format":
            self._render_format()
        elif screen_id == "report":
            self._render_report()
        elif screen_id == "download":
            self._render_download()

    # ------------------------------------------------------------------
    # View 1: Executive Dashboard (Home)
    # ------------------------------------------------------------------
    def _render_home(self):
        # Hero Banner
        hero = ctk.CTkFrame(
            self.viewport,
            corner_radius=12,
            fg_color=("white", "#1E293B")
        )
        hero.pack(fill="x", pady=(0, 20))

        hero_inner = ctk.CTkFrame(hero, fg_color="transparent")
        hero_inner.pack(fill="x", padx=24, pady=20)

        h_title = ctk.CTkLabel(
            hero_inner,
            text="Integrated Child Development Services (ICDS)",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            anchor="w"
        )
        h_title.pack(anchor="w")

        h_desc = ctk.CTkLabel(
            hero_inner,
            text="Automated Excel template creation, holiday syncing & stock report engine for administrative field operations.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("gray40", "gray65"),
            anchor="w"
        )
        h_desc.pack(anchor="w", pady=(4, 0))

        # Workflow Module Cards (Two High-Density Cards side-by-side)
        cards_container = ctk.CTkFrame(self.viewport, fg_color="transparent")
        cards_container.pack(fill="x", pady=(0, 16))
        cards_container.grid_columnconfigure((0, 1), weight=1)

        # Card 1: Template Designer
        c1 = ctk.CTkFrame(
            cards_container,
            corner_radius=12,
            fg_color=("white", "#1E293B")
        )
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        c1_box = ctk.CTkFrame(c1, fg_color="transparent")
        c1_box.pack(fill="both", expand=True, padx=22, pady=20)

        badge1 = ctk.CTkLabel(
            c1_box,
            text="MODULE 01",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=("#059669", "#34D399")
        )
        badge1.pack(anchor="w")

        c1_title = ctk.CTkLabel(
            c1_box,
            text="Monthly Template Designer",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        )
        c1_title.pack(anchor="w", pady=(2, 6))

        c1_desc = ctk.CTkLabel(
            c1_box,
            text="Build standard monthly blank spreadsheets with auto-filled dates, public holidays, and optional polio campaign days.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "gray65"),
            wraplength=280,
            justify="left"
        )
        c1_desc.pack(anchor="w", pady=(0, 14))

        # Bullet checkmarks
        self._add_feature_bullet(c1_box, "Automatic Day-to-Date mapping")
        self._add_feature_bullet(c1_box, "2026 Updated Regional Holiday List")
        self._add_feature_bullet(c1_box, "Pre-formatted stock consumption formulas")

        btn1 = ctk.CTkButton(
            c1_box,
            text="Launch Template Designer ➔",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=38,
            corner_radius=8,
            fg_color=("#059669", "#059669"),
            hover_color=("#047857", "#047857"),
            command=lambda: self.navigate_to("format")
        )
        btn1.pack(fill="x", pady=(16, 0))

        # Card 2: Report Generator
        c2 = ctk.CTkFrame(
            cards_container,
            corner_radius=12,
            fg_color=("white", "#1E293B")
        )
        c2.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        c2_box = ctk.CTkFrame(c2, fg_color="transparent")
        c2_box.pack(fill="both", expand=True, padx=22, pady=20)

        badge2 = ctk.CTkLabel(
            c2_box,
            text="MODULE 02",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        )
        badge2.pack(anchor="w")

        c2_title = ctk.CTkLabel(
            c2_box,
            text="Report Generator Engine",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        )
        c2_title.pack(anchor="w", pady=(2, 6))

        c2_desc = ctk.CTkLabel(
            c2_box,
            text="Upload completed monthly attendance sheets to reconcile food stocks, compute monthly rations, and export clean reports.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "gray65"),
            wraplength=280,
            justify="left"
        )
        c2_desc.pack(anchor="w", pady=(0, 14))

        self._add_feature_bullet(c2_box, "Automated Beneficiary Column Validation")
        self._add_feature_bullet(c2_box, "Rice, Dal, Oil & Egg balance tracking")
        self._add_feature_bullet(c2_box, "Single-click instant Excel generation")

        btn2 = ctk.CTkButton(
            c2_box,
            text="Launch Report Generator ➔",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=38,
            corner_radius=8,
            fg_color=("#2563EB", "#2563EB"),
            hover_color=("#1D4ED8", "#1D4ED8"),
            command=lambda: self.navigate_to("report")
        )
        btn2.pack(fill="x", pady=(16, 0))

        # Bottom operational tip bar
        tip_box = ctk.CTkFrame(
            self.viewport,
            corner_radius=10,
            fg_color=("white", "#1E293B")
        )
        tip_box.pack(fill="x", pady=(8, 0))

        tip_lbl = ctk.CTkLabel(
            tip_box,
            text="💡 Operational Flow: Design your monthly blank template in Module 01, populate Anganwadi attendance, then upload into Module 02.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "gray60")
        )
        tip_lbl.pack(padx=20, pady=12, anchor="w")

        # Developer & Organization Credit Banner
        credit_box = ctk.CTkFrame(
            self.viewport,
            corner_radius=10,
            fg_color=("white", "#1E293B")
        )
        credit_box.pack(fill="x", pady=(10, 0))

        credit_inner = ctk.CTkFrame(credit_box, fg_color="transparent")
        credit_inner.pack(fill="x", padx=20, pady=10)

        credit_title = ctk.CTkLabel(
            credit_inner,
            text="👨‍💻 Developer & Organization Credit",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#2563EB", "#38BDF8")
        )
        credit_title.pack(anchor="w")

        credit_detail = ctk.CTkLabel(
            credit_inner,
            text="Engineered & Maintained by Muhammad Noukhez  •  Organization: CodeX404 Solutions  •  Website: codex404solutions.com",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray35", "gray70")
        )
        credit_detail.pack(anchor="w", pady=(2, 0))

    def _add_feature_bullet(self, parent, text: str):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)

        icon = ctk.CTkLabel(
            row,
            text="✓",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=("#2563EB", "#38BDF8")
        )
        icon.pack(side="left", padx=(0, 6))

        txt = ctk.CTkLabel(
            row,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray30", "gray75")
        )
        txt.pack(side="left")

    # ------------------------------------------------------------------
    # View 2: Template Designer (Format)
    # ------------------------------------------------------------------
    def _render_format(self):
        panel = ctk.CTkFrame(
            self.viewport,
            corner_radius=12,
            fg_color=("white", "#1E293B")
        )
        panel.pack(fill="x", pady=(0, 20))

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=28, pady=24)

        t_lbl = ctk.CTkLabel(
            inner,
            text="Report Template Designer",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        )
        t_lbl.pack(anchor="w")

        s_lbl = ctk.CTkLabel(
            inner,
            text="Select the target month and year to generate a formatted monthly schedule template.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "gray65")
        )
        s_lbl.pack(anchor="w", pady=(2, 20))

        # Inputs Grid
        form_grid = ctk.CTkFrame(inner, fg_color="transparent")
        form_grid.pack(fill="x", pady=(0, 16))
        form_grid.grid_columnconfigure((0, 1), weight=1)

        # Month Selector
        m_box = ctk.CTkFrame(form_grid, fg_color="transparent")
        m_box.grid(row=0, column=0, sticky="ew", padx=(0, 15))

        ctk.CTkLabel(
            m_box,
            text="Target Month *",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        ).pack(anchor="w", pady=(0, 6))

        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        self.month_var = ctk.StringVar(value=months[0])
        month_menu = ctk.CTkOptionMenu(
            m_box,
            variable=self.month_var,
            values=months,
            height=36,
            corner_radius=8,
            command=lambda _: self._update_polio_sundays()
        )
        month_menu.pack(fill="x")

        # Year Selector
        y_box = ctk.CTkFrame(form_grid, fg_color="transparent")
        y_box.grid(row=0, column=1, sticky="ew", padx=(15, 0))

        ctk.CTkLabel(
            y_box,
            text="Target Year *",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        ).pack(anchor="w", pady=(0, 6))

        years = [str(y) for y in range(2024, 2101)]
        self.year_var = ctk.StringVar(value="2026")
        year_menu = ctk.CTkOptionMenu(
            y_box,
            variable=self.year_var,
            values=years,
            height=36,
            corner_radius=8,
            command=lambda _: self._update_polio_sundays()
        )
        year_menu.pack(fill="x")

        # Polio Campaign Checkbox
        self.include_polio = ctk.BooleanVar(value=False)
        self.polio_check = ctk.CTkCheckBox(
            inner,
            text="Mark Special National Immunization / Polio Campaign Sunday",
            variable=self.include_polio,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self._toggle_polio_drawer
        )
        self.polio_check.pack(anchor="w", pady=(10, 12))

        # Dynamic Polio Dropdown Drawer
        self.polio_drawer = ctk.CTkFrame(
            inner,
            corner_radius=8,
            fg_color=("gray95", "#0B1120")
        )
        self.polio_day_var = ctk.StringVar(value="")
        self.polio_day_menu = ctk.CTkOptionMenu(
            self.polio_drawer,
            variable=self.polio_day_var,
            values=["Select Sunday"],
            height=34,
            corner_radius=6
        )

        drawer_inner = ctk.CTkFrame(self.polio_drawer, fg_color="transparent")
        drawer_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            drawer_inner,
            text="Select Polio Sunday Date:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        ).pack(side="left", padx=(0, 14))

        self.polio_day_menu.pack(side="left")

        # Action Buttons
        btn_box = ctk.CTkFrame(inner, fg_color="transparent")
        btn_box.pack(fill="x", pady=(20, 0))

        gen_btn = ctk.CTkButton(
            btn_box,
            text="Generate Monthly Template",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            width=220,
            corner_radius=8,
            fg_color=("#059669", "#059669"),
            hover_color=("#047857", "#047857"),
            command=self._execute_format_generation
        )
        gen_btn.pack(side="left", padx=(0, 12))

        back_btn = ctk.CTkButton(
            btn_box,
            text="← Return to Dashboard",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=40,
            width=160,
            corner_radius=8,
            fg_color=("gray85", "gray25"),
            text_color=("gray15", "gray90"),
            hover_color=("gray75", "gray35"),
            command=lambda: self.navigate_to("home")
        )
        back_btn.pack(side="left")

    def _toggle_polio_drawer(self):
        if self.include_polio.get():
            self._update_polio_sundays()
            self.polio_drawer.pack(fill="x", pady=(0, 16))
        else:
            self.polio_drawer.pack_forget()

    def _update_polio_sundays(self):
        try:
            m_name = self.month_var.get()
            y_str = self.year_var.get()
            if not m_name or not y_str:
                return

            month_num = ["January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"].index(m_name) + 1
            year = int(y_str)

            sundays = [str(day) for day in range(1, calendar.monthrange(year, month_num)[1] + 1)
                       if calendar.weekday(year, month_num, day) == 6]

            if sundays:
                self.polio_day_menu.configure(values=sundays)
                self.polio_day_var.set(sundays[0])
        except Exception as e:
            print("Error updating Sundays:", e)

    def _execute_format_generation(self):
        try:
            month_name = self.month_var.get()
            year = int(self.year_var.get())

            month_num = ["January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"].index(month_name) + 1

            polio_day = int(self.polio_day_var.get()) if (self.include_polio.get() and self.polio_day_var.get()) else None

            temp_folder = os.path.join(os.getcwd(), "temp_generated")
            os.makedirs(temp_folder, exist_ok=True)

            Format_Generator(month_num, year, polio_day, temp_folder)

            self.generated_file_path = None
            for f in os.listdir(temp_folder):
                self.generated_file_path = os.path.join(temp_folder, f)

            self.download_file_type = "Monthly Report Template"
            self.navigate_to("download")
        except Exception as e:
            messagebox.showerror("Generation Error", str(e))

    # ------------------------------------------------------------------
    # View 3: Report Generator & Processor
    # ------------------------------------------------------------------
    def _render_report(self):
        panel = ctk.CTkFrame(
            self.viewport,
            corner_radius=12,
            fg_color=("white", "#1E293B")
        )
        panel.pack(fill="x", pady=(0, 20))

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=28, pady=24)

        t_lbl = ctk.CTkLabel(
            inner,
            text="Report Calculation & Stock Engine",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        )
        t_lbl.pack(anchor="w")

        s_lbl = ctk.CTkLabel(
            inner,
            text="Upload your completed data sheet to reconcile rations, attendance, and stock balance figures.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "gray65")
        )
        s_lbl.pack(anchor="w", pady=(2, 20))

        # Modern Upload Dropzone Card
        dropzone = ctk.CTkFrame(
            inner,
            corner_radius=10,
            fg_color=("gray95", "#0B1120"),
            border_width=1,
            border_color=("gray80", "#1E293B")
        )
        dropzone.pack(fill="x", pady=(0, 20))

        dz_inner = ctk.CTkFrame(dropzone, fg_color="transparent")
        dz_inner.pack(fill="both", expand=True, padx=30, pady=24)

        icon_lbl = ctk.CTkLabel(
            dz_inner,
            text="📁",
            font=ctk.CTkFont(family="Segoe UI", size=32)
        )
        icon_lbl.pack()

        dz_title = ctk.CTkLabel(
            dz_inner,
            text="Select Completed Field Data File (*.xlsx)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        dz_title.pack(pady=(4, 2))

        dz_desc = ctk.CTkLabel(
            dz_inner,
            text="Accepted Format: Month_Year_Report_Format.xlsx (e.g. September_2025_Report_Format.xlsx)",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=("gray40", "gray65")
        )
        dz_desc.pack(pady=(0, 14))

        browse_btn = ctk.CTkButton(
            dz_inner,
            text="Browse Files...",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=36,
            width=160,
            corner_radius=8,
            fg_color=("#2563EB", "#2563EB"),
            hover_color=("#1D4ED8", "#1D4ED8"),
            command=self._select_report_file
        )
        browse_btn.pack()

        self.file_indicator = ctk.CTkLabel(
            dz_inner,
            text="No file uploaded yet.",
            font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"),
            text_color=("gray50", "gray55")
        )
        self.file_indicator.pack(pady=(10, 0))

        # Action Buttons
        btn_box = ctk.CTkFrame(inner, fg_color="transparent")
        btn_box.pack(fill="x", pady=(10, 0))

        process_btn = ctk.CTkButton(
            btn_box,
            text="Process & Calculate Final Report",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            width=240,
            corner_radius=8,
            fg_color=("#2563EB", "#2563EB"),
            hover_color=("#1D4ED8", "#1D4ED8"),
            command=self._execute_report_processing
        )
        process_btn.pack(side="left", padx=(0, 12))

        back_btn = ctk.CTkButton(
            btn_box,
            text="← Return to Dashboard",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=40,
            width=160,
            corner_radius=8,
            fg_color=("gray85", "gray25"),
            text_color=("gray15", "gray90"),
            hover_color=("gray75", "gray35"),
            command=lambda: self.navigate_to("home")
        )
        back_btn.pack(side="left")

    def _select_report_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not path:
            return

        filename = os.path.basename(path)
        pattern = r"^(January|February|March|April|May|June|July|August|September|October|November|December)_(\d{4})_Report_Format\.xlsx$"

        if not re.match(pattern, filename):
            messagebox.showerror(
                "Naming Standard Notice",
                "Selected file name does not match required ICDS format.\n\nRequired Pattern:\nMonth_Year_Report_Format.xlsx\n(Example: September_2025_Report_Format.xlsx)",
            )
            return

        self.report_file_path = path
        self.file_indicator.configure(
            text=f"✓ Verified: {filename}",
            text_color=("#059669", "#34D399"),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        )

    def _execute_report_processing(self):
        if not getattr(self, "report_file_path", None):
            messagebox.showerror("File Required", "Please select a completed Excel file first.")
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

            self.download_file_type = "Verified Final Report"
            self.navigate_to("download")
        except Exception as e:
            messagebox.showerror("Processing Exception", str(e))

    # ------------------------------------------------------------------
    # View 4: Download / Export Summary Screen
    # ------------------------------------------------------------------
    def _render_download(self):
        panel = ctk.CTkFrame(
            self.viewport,
            corner_radius=12,
            fg_color=("white", "#1E293B")
        )
        panel.pack(fill="x", pady=(0, 20))

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=28, pady=24)

        t_lbl = ctk.CTkLabel(
            inner,
            text="Document Ready for Export",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        )
        t_lbl.pack(anchor="w")

        s_lbl = ctk.CTkLabel(
            inner,
            text=f"Your {self.download_file_type} has been computed and formatted successfully.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "gray65")
        )
        s_lbl.pack(anchor="w", pady=(2, 20))

        # Success Banner
        succ_card = ctk.CTkFrame(
            inner,
            corner_radius=10,
            fg_color=("#ECFDF5", "#064E3B"),
            border_width=1,
            border_color=("#A7F3D0", "#065F46")
        )
        succ_card.pack(fill="x", pady=(0, 20))

        sc_inner = ctk.CTkFrame(succ_card, fg_color="transparent")
        sc_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            sc_inner,
            text="✓ GENERATION COMPLETED SUCCESSFULLY",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=("#047857", "#6EE7B7")
        ).pack(anchor="w")

        fname = os.path.basename(self.generated_file_path) if self.generated_file_path else "Workbook.xlsx"
        ctk.CTkLabel(
            sc_inner,
            text=f"File: {fname}",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#065F46", "#ECFDF5")
        ).pack(anchor="w", pady=(4, 0))

        # Actions
        btn_box = ctk.CTkFrame(inner, fg_color="transparent")
        btn_box.pack(fill="x", pady=(10, 0))

        export_btn = ctk.CTkButton(
            btn_box,
            text="💾 Save to Local Drive...",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            width=220,
            corner_radius=8,
            fg_color=("#059669", "#059669"),
            hover_color=("#047857", "#047857"),
            command=self._save_output_file
        )
        export_btn.pack(side="left", padx=(0, 12))

        home_btn = ctk.CTkButton(
            btn_box,
            text="← Return to Dashboard",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=40,
            width=160,
            corner_radius=8,
            fg_color=("gray85", "gray25"),
            text_color=("gray15", "gray90"),
            hover_color=("gray75", "gray35"),
            command=lambda: self.navigate_to("home")
        )
        home_btn.pack(side="left")

    def _save_output_file(self):
        if not self.generated_file_path:
            messagebox.showerror("Error", "No generated file found to export.")
            return

        folder = filedialog.askdirectory(title="Select Destination Folder")
        if not folder:
            return

        try:
            dest = os.path.join(folder, os.path.basename(self.generated_file_path))
            shutil.copy2(self.generated_file_path, dest)
            messagebox.showinfo("Export Successful", f"File saved successfully to:\n\n{dest}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

        self._clear_temp_folders()

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
    app = ICDSAutoDeskApp()
    app.mainloop()
