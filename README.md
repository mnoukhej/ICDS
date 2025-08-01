# ICDS Report Generator

    ##Overview

    This project provides tools for generating and processing ICDS (Integrated Child Development Services) reports. It includes functionality to:

    1. Create standardized report formats for any given month/year
    2. Generate comprehensive reports based on the created formats
    3. Manage food stock data and calculate balances

    ## Features

    ICDS/
    ├── __pycache__/
    ├── .venv/
    ├── .gitignore
    ├── Format_Generator.ipynb       # Jupyter notebook version of format generator
    ├── Generate_Format.py           # Script to generate report templates
    ├── Generate_Report.py           # Script to process completed templates
    ├── holiday_list.py              # Contains holiday definitions
    ├── Main_Func.py                 # Core functionality
    ├── README.md                    # This file
    ├── Report_Generator.ipynb       # Jupyter notebook version of report generator
    ├── requirements.txt             # Python dependencies
    └── setup.bat                    # Windows setup script

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
    
