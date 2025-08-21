# Applicatin.py

import tkinter as tk
import pandas as pd
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageDraw, ImageTk
import calendar
import re
import math
import shutil
import os
import sys
from Main_Func import Format_Generator, Report_Generator_py


# -----------------------------
# Helper to get correct path (PyInstaller friendly)
# -----------------------------
def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller exe """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# -------------------------------
# Merged: Modern Themed App + Rounded UI + Full Functionality
# -------------------------------
class ICDSAutoDeskApp:
    # Theme palettes (light/dark)
    THEMES = {
        "light": {
            "BG_ROOT": "#F4F4F8",
            "FG_TEXT": "#222222",
            "FG_MUTED": "#666666",
            "CARD_BG": "#FFFFFF",
            "BTN_GREEN": "#00a97f",
            "BTN_RED": "#d9534f",
            "BTN_PINK": "#d600a1",
            "BTN_TEAL": "#28a78d",
            "BTN_ORANGE": "#c9402f",
            "ACCENT": "#ffb400",
            "TRACK_OFF": "#D0D0D5",
            "TRACK_ON": "#4CAF50",
        },
        "dark": {
            "BG_ROOT": "#1E1E1E",
            "FG_TEXT": "#FFFFFF",
            "FG_MUTED": "#AAAAAA",
            "CARD_BG": "#2C2C2C",
            "BTN_GREEN": "#00a97f",
            "BTN_RED": "#d9534f",
            "BTN_PINK": "#d600a1",
            "BTN_TEAL": "#28a78d",
            "BTN_ORANGE": "#c9402f",
            "ACCENT": "#ffb400",
            "TRACK_OFF": "#55585f",
            "TRACK_ON": "#4CAF50",
        },
    }

    def __init__(self, root):
        self.root = root
        self.root.title("ICDS AutoDesk")

        # Window sizing/centering
        window_width, window_height = 600, 560
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = int((sw - window_width) / 2)
        y = int((sh - window_height) / 2) - 50
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(560, 480)
        self.root.configure(bg=self.THEMES["light"]["BG_ROOT"])

        # Theme state
        self.theme_mode = "light"  # "light" or "dark"

        # Titlebar icon (ICO)
        try:
            self.root.iconbitmap(resource_path("app_icon.ico"))
        except Exception as e:
            print(f"Icon load failed: {e}")

        # Optional window iconphoto from PNG (no crash if missing)
        self._set_iconphoto_png(resource_path("logo.png"))

        # Load logo (for UI, not title bar)
        self.logo_tk = None
        self._load_logo()

        # Tk/ttk style init
        self._style_ttk_for_theme()

        # clear temps
        self._clear_temp_folders()

        # placeholders for paths/labels
        self.generated_file_path = None
        self.report_file_path = None
        self.selected_file_label = None

        # first screen
        self._show_home()

    # -------------------------
    # Utilities - Resources/Style
    # -------------------------
    def _set_iconphoto_png(self, path: str):
        try:
            if os.path.exists(path):
                icon_img = tk.PhotoImage(file=path)
                self.root.iconphoto(False, icon_img)
                self._icon_img_ref = icon_img  # prevent GC
        except Exception:
            pass

    def _load_logo(self):
        try:
            logo_path = resource_path("logo.png")
            if os.path.exists(logo_path):
                img = Image.open(logo_path).resize((120, 120), Image.LANCZOS)
                self.logo_tk = ImageTk.PhotoImage(img)
        except Exception as e:
            print("Logo load failed:", e)

    def _style_ttk_for_theme(self):
        t = self.THEMES[self.theme_mode]
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Combobox style that adapts to theme
        style.configure(
            "Themed.TCombobox",
            fieldbackground=t["CARD_BG"],   # Entry background
            background=t["CARD_BG"],        # Dropdown button background
            foreground=t["FG_TEXT"],        # Normal text color
            arrowcolor=t["FG_TEXT"],        # Arrow color
            bordercolor="#888888",          # Slight border so it looks distinct
            lightcolor=t["CARD_BG"],
            darkcolor=t["CARD_BG"],
        )

        # Add difference when focused / selecting
        style.map(
            "Themed.TCombobox",
            fieldbackground=[
                ("readonly", t["CARD_BG"]),
                ("focus", self._adjust_hex(t["CARD_BG"], 0.9))  # darker on focus
            ],
            foreground=[
                ("readonly", t["FG_TEXT"]),
                ("focus", "#ffffff")  # white text when active
            ],
            selectbackground=[("!disabled", "#0078d7")],  # highlight blue
            selectforeground=[("!disabled", "#ffffff")]   # white text on highlight
        )


    def _adjust_hex(self, hex_color: str, factor: float):
        """Lighten/Darken a hex color by multiplier factor."""
        h = hex_color.lstrip("#")
        r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _rounded_rect_image(self, size, color, radius=16):
        """Return a PhotoImage of a rounded rectangle for background cards/buttons."""
        w, h = size
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        drw = ImageDraw.Draw(img)
        drw.rounded_rectangle((0, 0, w, h), radius=radius, fill=color)
        return ImageTk.PhotoImage(img)

    # -------------------------
    # Reusable UI Parts
    # -------------------------
    def _clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _heading(self, text):
        t = self.THEMES[self.theme_mode]
        lbl = tk.Label(self.root, text=text, font=("Segoe UI", 20, "bold"),
                       fg=t["ACCENT"], bg=t["BG_ROOT"])
        lbl.pack(pady=(18, 6))
        return lbl

    def _subtext(self, text):
        t = self.THEMES[self.theme_mode]
        lbl = tk.Label(self.root, text=text, font=("Segoe UI", 10),
                       fg=t["FG_MUTED"], bg=t["BG_ROOT"])
        lbl.pack(pady=(0, 10))
        return lbl

    def _footer(self):
        t = self.THEMES[self.theme_mode]
        lbl = tk.Label(self.root,
                       text="© 2025 ICDS AutoDesk | Developed by Muhammad Noukhez",
                       font=("Segoe UI", 8, "italic"),
                       fg=t["FG_MUTED"], bg=t["BG_ROOT"])
        lbl.pack(side="bottom", pady=8)
        return lbl

    def _card(self, content_height=220, width=520, pad_y=10, radius=18):
        """Rounded card container with inner frame returned for content."""
        t = self.THEMES[self.theme_mode]
        wrapper = tk.Frame(self.root, bg=t["BG_ROOT"])
        wrapper.pack(pady=pad_y, fill="x")

        bg_img = self._rounded_rect_image((width, content_height), t["CARD_BG"], radius=radius)
        bg_lbl = tk.Label(wrapper, image=bg_img, bg=t["BG_ROOT"], bd=0)
        bg_lbl.image = bg_img
        bg_lbl.pack()

        inner = tk.Frame(wrapper, bg=t["CARD_BG"])
        inner.place(in_=bg_lbl, relx=0.5, rely=0.5, anchor="center")
        inner_pad = tk.Frame(inner, bg=t["CARD_BG"])
        inner_pad.pack(padx=18, pady=18, fill="both", expand=True)
        return inner_pad

    def _button(self, parent, text, bg, command, width=380, height=44, radius=12, pad=(8, 6)):
        """Rounded pill-like button with hover effect."""
        normal = self._rounded_rect_image((width, height), bg, radius=radius)
        hover = self._rounded_rect_image((width, height), self._adjust_hex(bg, 1.12), radius=radius)

        wrapper = tk.Frame(parent, bg=parent["bg"])
        btn = tk.Label(wrapper, image=normal, bg=parent["bg"], cursor="hand2")
        btn.image_normal = normal
        btn.image_hover = hover
        btn.pack(padx=pad[0], pady=pad[1])

        txt = tk.Label(btn, text=text, font=("Segoe UI", 11, "bold"), fg="white", bg=bg)
        txt.place(relx=0.5, rely=0.5, anchor="center")

        def on_enter(_):
            btn.configure(image=hover)
            txt.configure(bg=self._adjust_hex(bg, 1.12))

        def on_leave(_):
            btn.configure(image=normal)
            txt.configure(bg=bg)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", lambda e: command())
        txt.bind("<Enter>", on_enter)
        txt.bind("<Leave>", on_leave)
        txt.bind("<Button-1>", lambda e: command())
        return wrapper

    # -------------------------
    # Modern Theme Toggle (rounded)
    # -------------------------
    def _theme_switch(self, parent):
        t = self.THEMES[self.theme_mode]
        switch_w, switch_h = 56, 30
        knob_d = 26
        pad = 2
        canvas = tk.Canvas(parent, width=switch_w, height=switch_h, bd=0,
                        highlightthickness=0, bg=t["BG_ROOT"])
        canvas.pack(anchor="ne", pady=10, padx=10)

        knob_x = pad if self.theme_mode == "light" else switch_w - knob_d - pad

        def draw_switch(x):
            canvas.delete("all")

            # Track background (black like in image)
            track_color = "#111111"
            r = switch_h // 2
            canvas.create_oval(0, 0, switch_h, switch_h, fill=track_color, outline=track_color)
            canvas.create_oval(switch_w - switch_h, 0, switch_w, switch_h, fill=track_color, outline=track_color)
            canvas.create_rectangle(r, 0, switch_w - r, switch_h, fill=track_color, outline=track_color)

            # Sun icon (left)
            canvas.create_oval(6, 6, 18, 18, fill="#ffb400", outline="#ffb400")
            for i in range(8):
                angle = i * 45
                x1 = 12 + 7 * (math.cos(math.radians(angle)))
                y1 = 12 + 7 * (math.sin(math.radians(angle)))
                x2 = 12 + 10 * (math.cos(math.radians(angle)))
                y2 = 12 + 10 * (math.sin(math.radians(angle)))
                canvas.create_line(x1, y1, x2, y2, fill="#ffb400", width=1.5)

            # Moon icon (right)
            canvas.create_oval(switch_w - 18, 6, switch_w - 6, 18, fill="#ffb400", outline="#ffb400")
            canvas.create_oval(switch_w - 14, 6, switch_w - 2, 18, fill=track_color, outline=track_color)

            # Knob
            canvas.create_oval(x, pad, x + knob_d, pad + knob_d, fill="white", outline="white")

        def animate_toggle(start_x, end_x):
            step = 2 if end_x > start_x else -2
            for pos in range(start_x, end_x, step):
                draw_switch(pos)
                canvas.update()
                canvas.after(5)
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

            # AFTER animation is fully done, then refresh UI
            self.root.configure(bg=self.THEMES[self.theme_mode]["BG_ROOT"])
            self._style_ttk_for_theme()
            self._show_home()


        canvas.bind("<Button-1>", lambda e: toggle())
        draw_switch(knob_x)


    # -------------------------
    # Temp folders
    # -------------------------
    def _clear_temp_folders(self):
        for folder in ("temp_generated", "temp_generated_report"):
            path = os.path.join(os.getcwd(), folder)
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    print(f"Error clearing {folder}: {e}")

    # -----------------------------------------------------------
    # Screens
    # -----------------------------------------------------------
    def _build_topbar(self):
        # Top bar with theme switch (and optional logo small if you want)
        t = self.THEMES[self.theme_mode]
        top = tk.Frame(self.root, bg=t["BG_ROOT"])
        top.pack(fill="x")
        self._theme_switch(top)
        return top

    def _show_home(self):
        self._clear_temp_folders()
        self._clear_root()
        t = self.THEMES[self.theme_mode]
        self.root.configure(bg=t["BG_ROOT"])

        self._build_topbar()

        self._heading("Welcome to ICDS AutoDesk")
        self._subtext("Smart. Fast. Reliable Report Generation.")

        if self.logo_tk:
            tk.Label(self.root, image=self.logo_tk, bg=t["BG_ROOT"]).pack(pady=6)

        card = self._card(content_height=220)

        self._button(card, "Open Template Designer", t["BTN_GREEN"],
                     self._show_generate_format).pack()
        self._button(card, "Open Report Generator", t["BTN_RED"],
                     self._show_generate_report).pack()

        self._footer()

    # ------------------ Generate Format Screen ------------------
    def _show_generate_format(self):
        self._clear_temp_folders()
        self._clear_root()
        t = self.THEMES[self.theme_mode]
        self.root.configure(bg=t["BG_ROOT"])

        self._build_topbar()

        self._heading("Report Template Designer")
        self._subtext("Build the perfect format for your ICDS reports.")

        card = self._card(content_height=300)

        inputs = tk.Frame(card, bg=t["CARD_BG"])
        inputs.pack(pady=(0, 10))

        # Month
        tk.Label(inputs, text="Select Month:", fg=t["FG_TEXT"], bg=t["CARD_BG"],
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="e", padx=(0, 8), pady=6)
        self.month_var = tk.StringVar()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        month_cb = ttk.Combobox(inputs, textvariable=self.month_var, values=months,
                                state="readonly", width=18, style="Themed.TCombobox")
        month_cb.grid(row=0, column=1, sticky="w", pady=6)
        month_cb.bind("<<ComboboxSelected>>", lambda e: self._update_polio_sundays())

        # Year
        tk.Label(inputs, text="Select Year:", fg=t["FG_TEXT"], bg=t["CARD_BG"],
                 font=("Segoe UI", 10)).grid(row=1, column=0, sticky="e", padx=(0, 8), pady=6)
        self.year_var = tk.StringVar()
        years = [str(y) for y in range(2024, 2101)]
        year_cb = ttk.Combobox(inputs, textvariable=self.year_var, values=years,
                               state="readonly", width=18, style="Themed.TCombobox")
        year_cb.grid(row=1, column=1, sticky="w", pady=6)
        year_cb.bind("<<ComboboxSelected>>", lambda e: self._update_polio_sundays())

        # Polio checkbox + day
        self.include_polio = tk.BooleanVar(value=False)
        self.polio_check = tk.Checkbutton(
            inputs, text="Polio Campaign", variable=self.include_polio,
            command=self._toggle_polio_day, fg=t["FG_TEXT"], bg=t["CARD_BG"],
            selectcolor=t["CARD_BG"], activebackground=t["CARD_BG"], font=("Segoe UI", 10),
            state="disabled"
        )
        self.polio_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 2))

        self.polio_day_label = tk.Label(inputs, text="Polio Day (Sundays):",
                                        fg=t["FG_TEXT"], bg=t["CARD_BG"], font=("Segoe UI", 10))
        self.polio_day_var = tk.StringVar()
        self.polio_day_cb = ttk.Combobox(inputs, textvariable=self.polio_day_var,
                                         state="readonly", width=18, style="Themed.TCombobox")

        # Buttons
        self._button(card, "Generate Format", t["BTN_GREEN"], self._generate_format).pack(pady=(6, 2))
        self._button(card, "Back to Home", t["BTN_ORANGE"], self._show_home).pack(pady=(2, 0))

        self._footer()

    def _toggle_polio_day(self):
        # Show/hide polio day combobox
        if self.include_polio.get():
            self._update_polio_sundays()
            self.polio_day_label.grid(row=3, column=0, sticky="e", padx=(0, 8), pady=6)
            self.polio_day_cb.grid(row=3, column=1, sticky="w", pady=6)
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
        t = self.THEMES[self.theme_mode]
        msg = "Report Format"
        try:
            month_name = self.month_var.get()
            if not month_name:
                messagebox.showerror("Error", "Please select a month.")
                return
            month_num = ["January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"].index(month_name) + 1

            if not self.year_var.get():
                messagebox.showerror("Error", "Please select a year.")
                return
            year = int(self.year_var.get())

            polio_day = int(self.polio_day_var.get()) if (self.include_polio.get() and self.polio_day_var.get()) else None

            temp_folder = os.path.join(os.getcwd(), "temp_generated")
            os.makedirs(temp_folder, exist_ok=True)

            # Call your generator
            Format_Generator(month_num, year, polio_day, temp_folder)

            # capture generated file
            self.generated_file_path = None
            for f in os.listdir(temp_folder):
                self.generated_file_path = os.path.join(temp_folder, f)

            self._show_download(msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ------------------ Download Screen ------------------
    def _show_download(self, msg):
        self._clear_root()
        t = self.THEMES[self.theme_mode]
        self.root.configure(bg=t["BG_ROOT"])

        self._build_topbar()
        self._heading("Your file is ready to download!")

        card = self._card(content_height=170)
        self._button(card, "Download", t["BTN_GREEN"], self._download_file).pack(pady=(6, 2))
        self._button(card, "Back to Home", t["BTN_ORANGE"], self._show_home).pack(pady=(2, 0))
        self._footer()
        messagebox.showinfo("Success", f"{msg} generated successfully.")

    def _download_file(self):
        if not self.generated_file_path:
            messagebox.showerror("Error", "No file generated to download.")
            return
        folder = filedialog.askdirectory(title="Select Download Location")
        if not folder:
            return
        try:
            dest = os.path.join(folder, os.path.basename(self.generated_file_path))
            shutil.copy2(self.generated_file_path, dest)
            messagebox.showinfo("Download", f"File saved to:\n{dest}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        self._clear_temp_folders()

    # ------------------ Generate Report Screen ------------------
    def _show_generate_report(self):
        self._clear_temp_folders()
        self._clear_root()
        t = self.THEMES[self.theme_mode]
        self.root.configure(bg=t["BG_ROOT"])

        self._build_topbar()
        self._heading("Report Builder")
        self._subtext("Transform your data into insights in seconds.")

        card = self._card(content_height=260)

        self.report_file_path = None
        self.selected_file_label = None  # No label yet

        # Upload button
        upload_btn = self._button(card, "Upload Excel File", t["BTN_PINK"],
                                  lambda: self._select_file(card, upload_btn))
        upload_btn.pack()

        self._button(card, "Generate Report", t["BTN_TEAL"], self._generate_report_from_file).pack()
        self._button(card, "Back to Home", t["BTN_ORANGE"], self._show_home).pack()

        self._footer()

    # -------------------------
    # Select File (Logic) for report format file
    # -------------------------
    def _select_file(self, parent_widget, after_widget):
        # Remove old label
        if self.selected_file_label:
            self.selected_file_label.destroy()
            self.selected_file_label = None

        # Clear previous paths
        self.report_file_path = None
        self.generated_file_path = None

        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not path:
            return  # user cancelled

        filename = os.path.basename(path)

        # Month_Year_Report_Format.xlsx
        pattern = r"^(January|February|March|April|May|June|July|August|September|October|November|December)_(\d{4})_Report_Format\.xlsx$"

        if not re.match(pattern, filename):
            messagebox.showerror(
                "Invalid File",
                "Please select a file in the format:\nMonth_Year_Report_Format.xlsx\nExample: September_2025_Report_Format.xlsx",
            )
            return

        self.report_file_path = path

        if self.selected_file_label is None:
            t = self.THEMES[self.theme_mode]
            self.selected_file_label = tk.Label(
                parent_widget,
                text=f"Selected: {os.path.basename(path)}",
                fg=t["FG_TEXT"],
                bg=t["CARD_BG"],
                font=("Segoe UI", 10, "italic"),
            )
            # place below the upload button
            self.selected_file_label.pack(pady=(2, 5), after=after_widget)
        else:
            self.selected_file_label.config(text=f"Selected: {os.path.basename(path)}")

    # -------------------------
    # Generate report from file (validations)
    # -------------------------
    def _generate_report_from_file(self):
        if not getattr(self, "report_file_path", None):
            messagebox.showerror("Error", "Please upload an Excel file first.")
            return
        try:
            temp_folder = os.path.join(os.getcwd(), "temp_generated_report")
            os.makedirs(temp_folder, exist_ok=True)

            # Read Excel file
            df = pd.read_excel(self.report_file_path)

            # Required columns
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

            # Missing columns?
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                raise ValueError(f"The selected file is missing required columns: {', '.join(missing)}")

            # Empty columns?
            empty_cols = [col for col in required_columns if df[col].isna().all()]
            if empty_cols:
                raise ValueError(f"The following columns have no data: {', '.join(empty_cols)}")

            # If all checks pass, generate
            Report_Generator_py(self.report_file_path, temp_folder)

            # capture generated file
            self.generated_file_path = None
            for f in os.listdir(temp_folder):
                self.generated_file_path = os.path.join(temp_folder, f)

            self._show_download("Report")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# -------------------------
# Bootstrap
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ICDSAutoDeskApp(root)
    root.mainloop()
