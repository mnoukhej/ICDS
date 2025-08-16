# ICDS AutoDesk

## Project Overview
    ICDS AutoDesk is an automated desktop tool designed to simplify the generation of ICDS (Integrated Child Development Services) reports.
    It provides ready-to-use Excel formats, processes completed data, and generates final reports with accurate stock and balance calculations.

# ✨ Key Features

    📑 Format Generator – Create standardized monthly report templates

    📊 Report Generator – Generate final reports from completed formats

    🍲 Food Stock Management – Track stock, consumption, and balances

    📅 Holiday & Sunday Handling – Auto-format special days including optional Polio campaigns

    ⚡ Automation & Error Handling – Progress tracking with validation and recovery

## Folder Structure

<!-- TREE_START -->
```
├── App.py
├── Application.py
├── Format_Generator.ipynb
├── Generate_Format.py
├── Generate_Report.py
├── ICDS_App
│   ├── Application.exe
│   ├── Application.py
│   ├── Application.spec
│   ├── Main_Func.py
│   ├── README.md
│   ├── SetupBuilder.iss
│   ├── Txt_Files
│   │   ├── LICENSE.txt
│   │   ├── README_AFTER.txt
│   │   └── README_BEFORE.txt
│   ├── holiday_list.py
│   ├── icon.ico
│   ├── logo.png
│   ├── requirements.txt
│   └── setup.bat
├── Main_Func.py
├── README.md
├── Report_Generator.ipynb
├── holiday_list.py
├── logo.png
├── requirements.txt
├── setup.bat
└── update_tree.py
```
<!-- TREE_END -->


## ⚙️ Modules
# 📝 Format Generator (Generate_Format.py)

    Generates monthly ICDS report Excel templates

    Applies formatting for Sundays, holidays, and Polio campaign days

    Creates sheets for daily reporting and stock management

# 📊 Report Generator (Generate_Report.py)

    Processes completed format files to generate final reports

    Calculates food consumption & stock balances

    Supports multiple meal types (Rice/Khichdi days)

    Tracks progress with error handling

# 🛠️ Core Functions (Main_Func.py)

    Handles all date & ratio calculations

    Manages stock balances with reset option

    Provides consistent Excel formatting & styling



## 🚀 Installation

1. Clone the repository:

    git clone <repo-url>
    cd ICDS_AutoDesk


2. Install dependencies:

    pip install -r requirements.txt


3. Run the setup script (Windows only):

    setup.bat


## 📦 Dependencies

    Python 3.7+

    pandas

    openpyxl

    numpy

## 🔧 Configuration

    Update holiday_list.py to add or modify holidays

    Edit paths in Main_Func.py to change default save location



<hr>

## 📸 Screenshots
    ![App Screenshot](logo.png)


## ▶️ Usage
    Run the application:
    python Application.py

## 📜 License
This project is licensed under the terms of the [MIT License](ICDS_App/Txt_Files/LICENSE.txt).


### 📝 Format Generator
- Generates monthly ICDS report Excel templates  
- Applies formatting for Sundays, holidays, and Polio campaign days  
- Creates sheets for daily reporting and stock management  
