# 📁 Icds

## Project Overview
ICDS AutoDesk is an automated desktop tool designed to simplify the generation of ICDS (Integrated Child Development Services) reports.
It provides ready-to-use Excel formats, processes completed data, and generates final reports with accurate stock and balance calculations.

### ✨ Key Features
- 📑 Format Generator – Create standardized monthly report templates
- 📊 Report Generator – Generate final reports from completed formats
- 🍲 Food Stock Management – Track stock, consumption, and balances
- 📅 Holiday & Sunday Handling – Auto-format special days including optional Polio campaigns
- ⚡ Automation & Error Handling – Progress tracking with validation and recovery

## Folder Structure

<!-- TREE_START -->
```
├── Code
│   ├── App.py
│   ├── Application.py
│   ├── Format_Generator.ipynb
│   ├── Generate_Format.py
│   ├── Generate_Report.py
│   ├── Main_Func.py
│   ├── Report_Generator.ipynb
│   ├── debug.ipynb
│   ├── food_ratios.py
│   ├── holiday_list.py
│   └── logo.png
├── ICDS_App
│   ├── Application.py
│   ├── Application.spec
│   ├── Dockerfile
│   ├── Main_Func.py
│   ├── SetupBuilder.iss
│   ├── Txt_Files
│   │   ├── LICENSE.txt
│   │   ├── README_AFTER.txt
│   │   └── README_BEFORE.txt
│   ├── build.bat
│   ├── food_ratios.py
│   ├── holiday_list.py
│   ├── icon.ico
│   ├── logo.png
│   ├── requirements.txt
│   ├── setup.bat
│   └── updater.py
├── README.md
├── requirements.txt
├── setup.bat
├── update_tree.py
└── version.json
```
<!-- TREE_END -->


## ⚙️ Modules
### 📝 Format Generator
- Generates monthly ICDS report Excel templates  
- Applies formatting for Sundays, holidays, and Polio campaign days  
- Creates sheets for daily reporting and stock management  

### 📊 Report Generator (Generate_Report.py)
- Processes completed format files to generate final reports
- Calculates food consumption & stock balances
- Supports multiple meal types (Rice/Khichdi days)
- Tracks progress with error handling

### 🛠️ Core Functions (Main_Func.py)
- Handles all date & ratio calculations
- Manages stock balances with reset option
- Provides consistent Excel formatting & styling



## 🚀 Installation

### For Linux / macOS

1. Clone the repository:
   ```bash
   git clone https://github.com/mnoukhej/ICDS.git

2. Change Directroy
   ```bash
   cd ICDS

3. Run the setup script (Windows only):
   ```bash
   ./setup.bat

4. Run the application:
   ```bash
   python Application.py

## 📦 Dependencies
- Python 3.9+
- pandas
- openpyxl
- numpy

## 🔧 Configuration
- Update holiday_list.py to add or modify holidays
- Edit paths in Main_Func.py to change default save location

## 📜 License


## 👨‍💻 Developer & Organization Credit

| **Attribute** | **Details** |
| :--- | :--- |
| 👤 **Developer Name** | **Muhammad Noukhez** |
| 🏢 **Company Name** | **CodeX404 Solutions** |
| 🌐 **Official Website** | [**codex404solutions.com**](https://codex404solutions.com/) |
| 📧 **Email** | [mnoukhej@gmail.com](mailto:mnoukhej@gmail.com) |
| 🐙 **GitHub** | [@mnoukhej](https://github.com/mnoukhej) |
| 💼 **LinkedIn** | [linkedin.com/in/mnoukhej](https://www.linkedin.com/in/mnoukhej/) |

---

<div align="center">

[![Developer: Muhammad Noukhez](https://img.shields.io/badge/Developer-Muhammad%20Noukhez-00f2fe?style=for-the-badge&logo=github&logoColor=black)](https://github.com/mnoukhej)
[![Company: CodeX404 Solutions](https://img.shields.io/badge/Company-CodeX404%20Solutions-4facfe?style=for-the-badge&logo=rocket&logoColor=white)](https://codex404solutions.com/)
[![Website: codex404solutions.com](https://img.shields.io/badge/Website-codex404solutions.com-667eea?style=for-the-badge&logo=googlechrome&logoColor=white)](https://codex404solutions.com/)

<sub>Engineered & Maintained by **Muhammad Noukhez** • **CodeX404 Solutions** ([codex404solutions.com](https://codex404solutions.com/))</sub>

</div>
