# ICDS AutoDesk

## Project Overview
ICDS AutoDesk is an automated desktop tool for generating ICDS reports with ease.

1. Create standardized report formats for any given month/year
2. Generate comprehensive reports based on the created formats
3. Manage food stock data and calculate balances

## Folder Structure

<!-- TREE_START -->
```
├── App.py
├── Application.py
├── Format_Generator.ipynb
├── Generate_Format.py
├── Generate_Report.py
├── ICDS Report
│   ├── Report
│   │   ├── April_2025_Report.xlsx
│   │   ├── February_2025_Report.xlsx
│   │   ├── January_2025_Report.xlsx
│   │   ├── July_2025_Report.xlsx
│   │   ├── June_2025_Report.xlsx
│   │   ├── March_2025_Report.xlsx
│   │   └── May_2025_Report.xlsx
│   └── Report_Format
│       ├── April_2025_Report_Format.xlsx
│       ├── August_2025_Report_Format.xlsx
│       ├── February_2025_Report_Format.xlsx
│       ├── January_2025_Report_Format.xlsx
│       ├── July_2025_Report_Format.xlsx
│       ├── June_2025_Report_Format.xlsx
│       ├── March_2025_Report_Format.xlsx
│       └── May_2025_Report_Format.xlsx
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


### Format Generator (`Generate_Format.py`)
    - Creates Excel templates for monthly ICDS reports
    - Handles holidays and Sundays with special formatting
    - Includes optional Polio campaign day tracking
    - Generates separate sheets for daily reports and stock management

    ### Report Generator (`Generate_Report.py`)
    - Processes completed report formats to generate final reports
    - Calculates food consumption and remaining balances
    - Handles different meal types (Rice Day/Khichdi Day)
    - Provides progress tracking during report generation
    - Includes comprehensive error handling

    ### Main Functions (`Main_Func.py`)
    - Core logic for both format and report generation
    - Handles date calculations, food ratio computations
    - Manages stock balance tracking with reset functionality
    - Applies consistent styling and formatting to Excel outputs

    ## Installation

    1. Clone the repository
    2. Install requirements: `pip install -r requirements.txt`
    3. Run `setup.bat` to configure the environment (Windows only)

    ## Usage

    ### Generating a Report Format
    Run `Generate_Format.py` and provide:
    - Month (1-12)
    - Year (2000-2100)
    - Optional Polio campaign day

    ### Generating a Report
    Run `Generate_Report.py` which will process the most recently created format file.

    ## File Structure
    
    ## Dependencies

    - Python 3.7+
    - pandas
    - openpyxl
    - numpy

    ## Configuration

    - Modify `holiday_list.py` to add/update holidays
    - Edit paths in `Main_Func.py` to change default save locations

    ## Notes

    - Output files are saved to the Downloads folder by default
    - The system handles food stock balances with automatic resets
    - Special formatting is applied for Sundays, holidays, and Polio days

    For questions or issues, please contact the maintainer.