import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import calendar
from Main_Func import Format_Generator, Report_Generator_py


class ICDSReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ICDS Report Generator")
        self.root.geometry("420x350")
        self.root.configure(bg="#1e1e1e")

        self.show_home()

    def clear_window(self):
        """Remove all widgets from the current window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    # --------------------
    # Screen 1: Home
    # --------------------
    def show_home(self):
        self.clear_window()
        tk.Label(self.root, text="Welcome to Report Generator", font=("Arial", 14, "bold"),
                 fg="#ffae00", bg="#1e1e1e").pack(pady=20)

        tk.Button(self.root, text="Create a New Report Format", bg="#28a745", fg="white", font=("Arial", 12),
                  command=self.show_generate_format).pack(pady=10, ipadx=10, ipady=5)

        tk.Button(self.root, text="View or Generate Reports", bg="#dc3545", fg="white", font=("Arial", 12),
                  command=self.show_generate_report).pack(pady=10, ipadx=10, ipady=5)

    # --------------------
    # Screen 2: Generate Format
    # --------------------
    def show_generate_format(self):
        self.clear_window()
        tk.Label(self.root, text="Generate Reports Format", font=("Arial", 14, "bold"),
                 fg="#ffae00", bg="#1e1e1e").pack(pady=20)

        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(pady=10)

        # Month Selection
        tk.Label(frame, text="Select Month:", fg="white", bg="#1e1e1e").grid(row=0, column=0, sticky="e", pady=5)
        self.month_var = tk.StringVar()
        month_names = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        month_cb = ttk.Combobox(frame, textvariable=self.month_var, values=month_names, state="readonly")
        month_cb.grid(row=0, column=1, pady=5)
        month_cb.bind("<<ComboboxSelected>>", lambda e: self.update_polio_sundays())

        # Year Selection
        tk.Label(frame, text="Select Year:", fg="white", bg="#1e1e1e").grid(row=1, column=0, sticky="e", pady=5)
        self.year_var = tk.StringVar()
        year_cb = ttk.Combobox(frame, textvariable=self.year_var, values=[str(y) for y in range(2000, 2101)], state="readonly")
        year_cb.grid(row=1, column=1, pady=5)
        year_cb.bind("<<ComboboxSelected>>", lambda e: self.update_polio_sundays())

        # Polio Checkbox
        self.include_polio = tk.BooleanVar()
        polio_check = tk.Checkbutton(frame, text="Include Polio Campaign", variable=self.include_polio,
                                     command=self.toggle_polio_day, fg="white", bg="#1e1e1e", selectcolor="#1e1e1e")
        polio_check.grid(row=2, column=0, columnspan=2, pady=5)

        # Polio Day Selection (hidden initially)
        self.polio_day_label = tk.Label(frame, text="Polio Day (Sundays):", fg="white", bg="#1e1e1e")
        self.polio_day_var = tk.StringVar()
        self.polio_day_cb = ttk.Combobox(frame, textvariable=self.polio_day_var, state="readonly")

        # Buttons
        tk.Button(self.root, text="Generate Format", bg="#28a745", fg="white",
                  command=self.generate_format).pack(pady=10, ipadx=10, ipady=5)
        tk.Button(self.root, text="Back", bg="#dc3545", fg="white",
                  command=self.show_home).pack(pady=5, ipadx=10, ipady=5)

    def toggle_polio_day(self):
        """Show or hide Polio day dropdown."""
        if self.include_polio.get():
            self.update_polio_sundays()
            self.polio_day_label.grid(row=3, column=0, sticky="e", pady=5)
            self.polio_day_cb.grid(row=3, column=1, pady=5)
        else:
            self.polio_day_label.grid_forget()
            self.polio_day_cb.grid_forget()

    def update_polio_sundays(self):
        """Update Polio day dropdown with all Sundays of the selected month/year."""
        try:
            if not self.month_var.get() or not self.year_var.get():
                return

            month_number = ["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"].index(self.month_var.get()) + 1
            year = int(self.year_var.get())

            # Get all Sundays in month
            sundays = []
            for day in range(1, calendar.monthrange(year, month_number)[1] + 1):
                if calendar.weekday(year, month_number, day) == 6:  # Sunday
                    sundays.append(str(day))

            self.polio_day_cb['values'] = sundays
            if sundays:
                self.polio_day_cb.current(0)
        except Exception as e:
            print("Error updating Sundays:", e)

    def generate_format(self):
        """Generate the report format file."""
        try:
            month_name = self.month_var.get()
            if not month_name:
                messagebox.showerror("Error", "Please select a month.")
                return

            month_number = ["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"].index(month_name) + 1

            year = int(self.year_var.get()) if self.year_var.get() else None
            if not year:
                messagebox.showerror("Error", "Please select a year.")
                return

            polio_day = int(self.polio_day_var.get()) if self.include_polio.get() and self.polio_day_var.get() else None

            folder_location = fr"C:\Users\MUHAMMAD NOUKHEZ\Downloads"

            
            Format_Generator(month_number, year, polio_day, folder_location)
            self.show_download_screen()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --------------------
    # Screen 3: Download Ready
    # --------------------
    def show_download_screen(self):
        self.clear_window()
        tk.Label(self.root, text="Your file is ready to download!", font=("Arial", 14, "bold"),
                 fg="#ffae00", bg="#1e1e1e").pack(pady=20)

        tk.Button(self.root, text="Download", bg="#28a745", fg="white",
                  command=self.download_file).pack(pady=10, ipadx=10, ipady=5)
        tk.Button(self.root, text="Back", bg="#dc3545", fg="white",
                  command=self.show_home).pack(pady=5, ipadx=10, ipady=5)

    def download_file(self):
        # This should move/copy the generated file to user's chosen location
        messagebox.showinfo("Download", "File download simulation complete!")

    # --------------------
    # Generate Report Section
    # --------------------
    def show_generate_report(self):
        self.clear_window()
        tk.Label(self.root, text="Generate Report", font=("Arial", 14, "bold"),
                 fg="#ffae00", bg="#1e1e1e").pack(pady=20)

        tk.Button(self.root, text="Select Report File", bg="#28a745", fg="white",
                  command=self.select_file).pack(pady=10, ipadx=10, ipady=5)

        tk.Button(self.root, text="Back", bg="#dc3545", fg="white",
                  command=self.show_home).pack(pady=5, ipadx=10, ipady=5)

    def select_file(self):
        output_folder_location = fr"C:\Users\MUHAMMAD NOUKHEZ\Downloads"
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            try:
                Report_Generator_py(file_path, output_folder_location)
                messagebox.showinfo("Success", "Report generated successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))


# ----------------------
# Run Application
# ----------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ICDSReportApp(root)
    root.mainloop()
