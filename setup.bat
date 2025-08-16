@echo off
echo Setting up the project...

:: Create virtual environment
python -m venv .venv
echo .venv created

:: Activate virtual environment
call .venv\Scripts\activate.bat
echo .venv activated.

:: Upgrade pip
echo Upgrading pip...
python.exe -m pip install --upgrade pip
echo pip upgrade -- done

:: Install ipykernel
echo Installing ipykernel...
pip install ipykernel

:: Install dependencies from requirements.txt if it exists
if exist requirements.txt (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    echo requirements installed
) else (
    echo No requirements.txt found. Skipping dependency installation.
)

:: Create and configure .gitignore
echo Creating .gitignore file...
(
    echo .venv/
    echo .venv/**/__init__.py
    echo __pycache__/
    echo *.pyc
    echo *.pyo
    echo *.log
    echo db.sqlite3
    echo .env
    echo .idea/
    echo .vscode/
    echo .DS_Store
    echo build/
    echo dist/
    echo *.egg-info/
    echo *.egg
    echo .pytest_cache/ 
    echo .coverage
    echo .mypy_cache/
    echo .tox/
    echo .coverage.*
    echo .ipynb_checkpoints/
    echo *.exe
    echo /SetupFile/
    echo .spec
) > .gitignore
echo .gitignore file created.

echo.
echo Setup complete! Now you can run the server using run_server.bat

pause
