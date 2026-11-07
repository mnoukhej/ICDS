import tkinter as tk
import pandas as pd
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageDraw, ImageTk
import calendar
import re
import shutil
import os
from Main_Func import Format_Generator, Report_Generator_py


# -------------------------------
# Themed, reusable Tkinter app
# -------------------------------
class ICDSReportApp:
    # Theme colors
    BG_ROOT = "#1e1e1e"       # window background
    BG_CARD = "#2b2b2b"       # card background
    FG_HEADING = "#ffb400"    # gold heading
    FG_MUTED = "#aaaaaa"      # footer
    BTN_GREEN = "#00a97f"
    BTN_RED = "#d9534f"
    BTN_PINK = "#d600a1"
    BTN_TEAL = "#28a78d"
    BTN_ORANGE = "#c9402f"

    def __init__(self, root):
        self.root = root
        self.root.title("ICDS Report Generator")


        # Center window on screen
        window_width = 520
        window_height = 420
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2)) - 100  # Adjust y to fit in view
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.root.configure(bg=self.BG_ROOT)
        self.root.resizable(False, False)

        # Set app icon (ignore if not found)
        self._set_icon_safely("logo.png")

        # Style ttk for dark comboboxes
        self._style_ttk_dark()

        # Reset temp folders on startup
        self._clear_temp_folders()

        # First screen
        self._show_home()

    # -------------------------
    # Utilities (Design)
    # -------------------------
    def _set_icon_safely(self, path: str):
        try:
            icon_img = tk.PhotoImage(file=path)
            self.root.iconphoto(False, icon_img)
            self._icon_img_ref = icon_img  # prevent GC
        except Exception:
            pass  # fail silently if no logo.png

    def _style_ttk_dark(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(
            "Dark.TCombobox",
            fieldbackground="#3c3c3c",
            background="#3c3c3c",
            foreground="white",
            arrowcolor="white",
            bordercolor="#3c3c3c",
            lightcolor="#3c3c3c",
            darkcolor="#3c3c3c",
        )
        style.map("Dark.TCombobox",
                  fieldbackground=[("readonly", "#3c3c3c")],
                  foreground=[("readonly", "white")])

    def _rounded_rect_image(self, size, color, radius=15):
        """Return a PhotoImage of a rounded rectangle for background cards/buttons."""
        w, h = size
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        drw = ImageDraw.Draw(img)
        drw.rounded_rectangle((0, 0, w, h), radius=radius, fill=color)
        return ImageTk.PhotoImage(img)

    def _adjust_hex(self, hex_color: str, factor: float):
        """Lighten/Darken a hex color by multiplier factor."""
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _button(self, parent, text, bg, command, width=360, height=44, pad=(8, 8)):
        """
        Rounded button with hover. Returns the outer label (so caller can .pack/.grid).
        """
        normal = self._rounded_rect_image((width, height), bg, radius=12)
        hover = self._rounded_rect_image((width, height), self._adjust_hex(bg, 1.12), radius=12)

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

    def _heading(self, text):
        lbl = tk.Label(self.root, text=text, font=("Segoe UI", 18, "bold"),
                       fg=self.FG_HEADING, bg=self.BG_ROOT)
        lbl.pack(pady=(22, 10))
        return lbl

    def _footer(self):
        lbl = tk.Label(self.root,
                       text="© 2026 ICDS Report Generator | Developed by Muhammad Noukhez • CodeX404 Solutions (codex404solutions.com)",
                       font=("Segoe UI", 8, "italic"),
                       fg=self.FG_MUTED, bg=self.BG_ROOT)
        lbl.pack(side="bottom", pady=8)
        return lbl

    def _card(self, content_height=220, width=460, pad_y=8):
        """
        Creates a centered 'card' with rounded background and returns the usable inner frame.
        The card height should cover the inner content + some padding.
        """
        wrapper = tk.Frame(self.root, bg=self.BG_ROOT)
        wrapper.pack(pady=pad_y)

        # background image
        bg_img = self._rounded_rect_image((width, content_height), self.BG_CARD, radius=18)
        bg_lbl = tk.Label(wrapper, image=bg_img, bg=self.BG_ROOT, bd=0)
        bg_lbl.image = bg_img
        bg_lbl.pack()

        # inner frame placed on top, with nice padding
        inner = tk.Frame(wrapper, bg=self.BG_CARD)
        # Put inner frame inside bg label (so z-order is correct)
        inner.place(in_=bg_lbl, relx=0.5, rely=0.5, anchor="center")
        # add internal padding by a container
        inner_pad = tk.Frame(inner, bg=self.BG_CARD)
        inner_pad.pack(padx=18, pady=18, fill="both", expand=True)

        return inner_pad

    def _clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()

    # -------------------------
    # Utilities (Logic)
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
# --------------- Screens -----------------------------------
# -----------------------------------------------------------

    def _show_home(self):
        self._clear_temp_folders()
        self._clear_root()
        self._heading("Welcome to Report Generator")

        card = self._card(content_height=210)

        # Buttons on home
        self._button(card, "Create a New Report Format", self.BTN_GREEN,
                     self._show_generate_format).pack()
        self._button(card, "View or Generate Reports", self.BTN_RED,
                     self._show_generate_report).pack()

        self._footer()

# -------------------------------------------------------------
# ----------- Generate Format Screen --------------------------
# -------------------------------------------------------------
    
    def _show_generate_format(self):
        self._clear_temp_folders()
        self._clear_root()
        self._heading("Generate Reports Format")

        # Card sized to fit inputs + buttons
        card = self._card(content_height=280)

        # Inputs section
        inputs = tk.Frame(card, bg=self.BG_CARD)
        inputs.pack(pady=(0, 10))

        # Month
        tk.Label(inputs, text="Select Month:", fg="white", bg=self.BG_CARD,
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="e", padx=(0, 8), pady=6)
        self.month_var = tk.StringVar()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        month_cb = ttk.Combobox(inputs, textvariable=self.month_var, values=months,
                                state="readonly", width=18, style="Dark.TCombobox")
        month_cb.grid(row=0, column=1, sticky="w", pady=6)
        month_cb.bind("<<ComboboxSelected>>", lambda e: self._update_polio_sundays())

        # Year
        tk.Label(inputs, text="Select Year:", fg="white", bg=self.BG_CARD,
                 font=("Segoe UI", 10)).grid(row=1, column=0, sticky="e", padx=(0, 8), pady=6)
        self.year_var = tk.StringVar()
        years = [str(y) for y in range(2024, 2101)]
        year_cb = ttk.Combobox(inputs, textvariable=self.year_var, values=years,
                               state="readonly", width=18, style="Dark.TCombobox")
        year_cb.grid(row=1, column=1, sticky="w", pady=6)
        year_cb.bind("<<ComboboxSelected>>", lambda e: self._update_polio_sundays())

        # Polio checkbox + day
        self.include_polio = tk.BooleanVar(value=False)
        self.polio_check = tk.Checkbutton(
            inputs, text="Polio Campaign", variable=self.include_polio,
            command=self._toggle_polio_day, fg="white", bg=self.BG_CARD,
            selectcolor=self.BG_CARD, activebackground=self.BG_CARD, font=("Segoe UI", 10),
            state="disabled"
        )
        self.polio_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 2))

        self.polio_day_label = tk.Label(inputs, text="Polio Day (Sundays):",
                                        fg="white", bg=self.BG_CARD, font=("Segoe UI", 10))
        self.polio_day_var = tk.StringVar()
        self.polio_day_cb = ttk.Combobox(inputs, textvariable=self.polio_day_var,
                                         state="readonly", width=18, style="Dark.TCombobox")

        # Buttons
        self._button(card, "Generate Format", self.BTN_GREEN, self._generate_format).pack(pady=(6, 2))
        self._button(card, "Back", self.BTN_RED, self._show_home).pack(pady=(2, 0))

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
            month_ok = bool(self.month_var.get())
            year_ok = bool(self.year_var.get())

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

            Format_Generator(month_num, year, polio_day, temp_folder)

            # capture generated file
            self.generated_file_path = None
            for f in os.listdir(temp_folder):
                self.generated_file_path = os.path.join(temp_folder, f)
            self._show_download(msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))


# -------------------------------------------------------------
# ------------------ Download Screen --------------------------
# -------------------------------------------------------------

    def _show_download(self, msg):
        self._clear_root()
        self._heading("Your file is ready to download!")

        card = self._card(content_height=170)
        self._button(card, "Download", self.BTN_GREEN, self._download_file).pack(pady=(6, 2))
        self._button(card, "Back", self.BTN_RED, self._show_home).pack(pady=(2, 0))
        self._footer()
        messagebox.showinfo("Success", f"{msg} generated successfully.")


    def _download_file(self):
        if not hasattr(self, "generated_file_path") or not self.generated_file_path:
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



# -------------------------------------------------------------
# ----------- Generate Report Screen --------------------------
# -------------------------------------------------------------

    
    def _show_generate_report(self):
        self._clear_temp_folders()
        self._clear_root()
        self._heading("Generate Report")

        card = self._card(content_height=240)
        self.report_file_path = None
        self.selected_file_label = None  # No label yet

       # Upload button
        upload_btn = self._button(card, "Upload Excel File", self.BTN_PINK,
                                lambda: self._select_file(card, upload_btn))
        
        upload_btn.pack()

        self._button(card, "Generate Report", self.BTN_TEAL, self._generate_report_from_file).pack()
        self._button(card, "Back", self.BTN_ORANGE, self._show_home).pack()

        self._footer()



    # -------------------------
    # Select File (Logic)
    # -------------------------
    def _select_file(self, parent_widget, after_widget):

        # 🔹 Remove old label from UI if it exists
        if self.selected_file_label:
            self.selected_file_label.destroy()
            self.selected_file_label = None

        # 🔹 Clear previous file path & generated file path
        self.report_file_path = None
        self.generated_file_path = None

        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])

        if not path:
            return  # User cancelled 
    

        filename = os.path.basename(path)

        # Regex pattern to match: Month_Year_Report_Format.xlsx
        pattern = r"^(January|February|March|April|May|June|July|August|September|October|November|December)_(\d{4})_Report_Format\.xlsx$"
    
        if not re.match(pattern, filename):
            messagebox.showerror("Invalid File", "Please select a file in the format:\nMonth_Year_Report_Format.xlsx\nExample: September_2025_Report_Format.xlsx")
            return

        self.report_file_path = path
        if self.selected_file_label is None:
            self.selected_file_label = tk.Label(
                parent_widget,
                text=f"Selected: {os.path.basename(path)}",
                fg="white",
                bg=self.BG_CARD,
                font=("Arial", 10, "italic")
            )
            self.selected_file_label.pack(pady=(2, 5), after=after_widget)
        else:
            self.selected_file_label.config(text=f"Selected: {os.path.basename(path)}")

        
    # -------------------------
    # _generate_report_from_file
    # -------------------------
    def _generate_report_from_file(self):
        if not getattr(self, "report_file_path", None):
            messagebox.showerror("Error", "Please upload an Excel file first.")
            return
        try:
            temp_folder = os.path.join(os.getcwd(), "temp_generated_report")
            os.makedirs(temp_folder, exist_ok=True)


            # ✅ Read Excel file
            df = pd.read_excel(self.report_file_path)

            # ✅ Required columns
            required_columns = [
                "Date",
                "Days",
                "Pregnant (Mothers)",
                "Lactating (Mothers)",
                "Boys (6m - 3y)",
                "Girls (6m - 3y)",
                "Boys (3y - 6y)",
                "Girls (3y - 6y)"
            ]

            # ✅ Check missing columns
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                raise ValueError(f"The selected file is missing required columns: {', '.join(missing)}")

            # ✅ Check empty columns
            empty_cols = [col for col in required_columns if df[col].isna().all()]
            if empty_cols:
                raise ValueError(f"The following columns have no data: {', '.join(empty_cols)}")

            # ✅ If all checks pass, run report generator
            Report_Generator_py(self.report_file_path, temp_folder)
            # messagebox.showinfo("Success", "Report generated successfully.")
            msg = "Report"

            

            # capture generated file
            self.generated_file_path = None
            for f in os.listdir(temp_folder):
                self.generated_file_path = os.path.join(temp_folder, f)

            self._show_download(msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))


# -------------------------
# Bootstrap
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ICDSReportApp(root)
    root.mainloop()
