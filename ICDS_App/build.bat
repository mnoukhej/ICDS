@echo off
REM ================================
REM Build Script for ICDS_App
REM ================================

REM Step 1: Look for setup.bat
if exist setup.bat (
    echo Running setup.bat for environment setup...
    call setup.bat
) else (
    echo setup.bat not found. Performing inline setup...

    REM Check if venv exists
    if not exist ".venv\" (
        echo Virtual environment not found. Creating one...
        py -3.12 -m venv .venv

        echo Installing requirements...
        call .venv\Scripts\activate.bat
        pip install --upgrade pip
        if exist requirements.txt (
            pip install -r requirements.txt
        ) else (
            echo requirements.txt not found. Skipping...
        )
        deactivate
    )
)

REM Step 2: Activate venv
call .venv\Scripts\activate.bat

REM Step 3: Clean old build/dist if they exist
echo Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Step 4: Run PyInstaller inside venv
echo Building executable...
python -m PyInstaller --noconsole --onefile --icon=icon.ico --add-data "logo.png;." Application.py

echo.
echo ✅ Build completed! Check the "dist" folder for your exe file.
pause
