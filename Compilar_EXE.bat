@echo off
cd /d "%~dp0"
set "PY=%USERPROFILE%\MonitoreoBrainChild\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" -m pip install pymodbus==3.16.1 pyserial matplotlib openpyxl pyinstaller
if errorlevel 1 goto error
"%PY%" -m PyInstaller --noconfirm --clean --onefile --windowed --name BrainChild_Monitor --icon BrainChild.ico --hidden-import matplotlib.backends.backend_tkagg monitor_brainchild_portable.py
if errorlevel 1 goto error
echo EXE creado en dist\BrainChild_Monitor.exe
explorer "%~dp0dist"
pause
exit /b 0
:error
echo Error de compilacion. Revise los mensajes anteriores.
pause
exit /b 1
