@echo off
cd /d "%~dp0"

echo Verification de Python...

python --version >nul 2>&1

if %errorlevel% neq 0 (
    echo Python non trouve, installation...

    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.13.5/python-3.13.5-amd64.exe

    python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1

    timeout /t 15
)

echo Installation des bibliotheques...
python -m pip install -r requirements.txt

echo Lancement du jeu...
python ..\code\main.py