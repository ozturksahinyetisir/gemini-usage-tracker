@echo off
title Gemini Usage Tracker - Build EXE
cd /d "%~dp0"
echo ========================================================
echo   Gemini Usage Tracker - Standalone EXE Derleniyor...
echo ========================================================
python -m PyInstaller --noconsole --onefile --icon="assets/icon.ico" --name="GeminiUsageTracker" --add-data="assets;assets" main.py
echo.
if exist "dist\GeminiUsageTracker.exe" (
    echo [BASARILI] EXE dosyasi olusturuldu: dist\GeminiUsageTracker.exe
    copy "dist\GeminiUsageTracker.exe" "GeminiUsageTracker.exe"
    echo Ana dizine kopyalandi: GeminiUsageTracker.exe
) else (
    echo [HATA] Derleme sirasinda bir hata olustu.
)
pause
