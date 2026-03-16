@echo off
setlocal

REM Create build with PyInstaller (onedir)
pyinstaller --noconfirm --clean --onedir --windowed ^
  --add-data "Assets;Assets" ^
  --add-data "DB;DB" ^
  main.py

endlocal
