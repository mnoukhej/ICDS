@echo off
echo =====================================
echo Setting up the project...
echo =====================================

:: Create virtual environment if not exists
if not exist ".venv" (
    echo Creating virtual environment...
    py -3.12 -m venv .venv
    echo [OK] .venv created
) else (
    echo [SKIP] .venv already exists
)

:: Activate virtual environment
call .venv\Scripts\activate
echo [OK] .venv activated

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel%==0 (
    echo [OK] pip upgraded
) else (
    echo [ERROR] pip upgrade failed
)

:: Install dependencies from requirements.txt if exists
if exist requirements.txt (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel%==0 (
        echo [OK] requirements installed
    ) else (
        echo [ERROR] requirements installation failed
    )
) else (
    echo [SKIP] requirements.txt not found
)

:: Create .gitignore if not exists
if not exist ".gitignore" (
    echo Creating .gitignore...
    (
        echo .venv/
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
    echo [OK] .gitignore created
) else (
    echo [SKIP] .gitignore already exists
)

:: Create .dockerignore if not exists
if not exist ".gitignore" (
    echo Creating .dockerignore...
    (
        echo .venv> .dockerignore
        echo __pycache__>> .dockerignore
        echo build>> .dockerignore
        echo dist>> .dockerignore
        echo .git>> .dockerignore

    ) > .dockerignore
    echo [OK] .dockerignore created
) else (
    echo [SKIP] .dockerignore already exists
)




echo =====================================
echo Setup complete! Now you can run the server using run_server.bat
echo =====================================


pause
