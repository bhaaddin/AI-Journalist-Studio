@echo off
title AI Journalist Studio - Installation
chcp 65001 >nul

echo ============================================
echo    AI Journalist Studio - Installation
echo ============================================
echo.

REM --------------------------------------------------
REM Step 1: Check Python
REM --------------------------------------------------
echo [1/5] Checking Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Download it from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set pyver=%%v
echo    Found Python %pyver%
echo.

REM --------------------------------------------------
REM Step 2: Check pip
REM --------------------------------------------------
echo [2/5] Checking pip...

pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available.
    echo Run: python -m ensurepip --upgrade
    pause
    exit /b 1
)
echo    pip is available
echo.

REM --------------------------------------------------
REM Step 3: Install requirements
REM --------------------------------------------------
echo [3/5] Installing Python dependencies...

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    echo Try: pip install --upgrade pip
    pause
    exit /b 1
)
echo    Dependencies installed successfully
echo.

REM --------------------------------------------------
REM Step 4: Check Ollama
REM --------------------------------------------------
echo [4/5] Checking Ollama...

where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Ollama is not installed or not in PATH.
    echo Download it from: https://ollama.com/download
    echo.
    echo After installing, run:
    echo   ollama pull qwen2.5-coder:1.5b
    echo   ollama pull qwen2.5-coder:7b
    echo   ollama pull llama3.2:3b
    echo   ollama serve
    echo.
    set OLLAMA_MISSING=1
) else (
    echo    Found Ollama
    echo.

    REM --------------------------------------------------
    REM Step 5: Check models
    REM --------------------------------------------------
    echo [5/5] Checking Ollama models...

    ollama list 2>nul | findstr "qwen2.5-coder:1.5b" >nul
    if %errorlevel% neq 0 (
        echo    Model qwen2.5-coder:1.5b not found.
        choice /c YN /m "Pull it now (suggested)?"
        if errorlevel 2 (
            echo    Skipped. You can pull it later with: ollama pull qwen2.5-coder:1.5b
        ) else (
            echo    Pulling qwen2.5-coder:1.5b...
            ollama pull qwen2.5-coder:1.5b
        )
    ) else (
        echo    Model qwen2.5-coder:1.5b found
    )

    ollama list 2>nul | findstr "qwen2.5-coder:7b" >nul
    if %errorlevel% neq 0 (
        echo    Model qwen2.5-coder:7b not found.
        choice /c YN /m "Pull it now (needed for deep mode)?"
        if errorlevel 2 (
            echo    Skipped. Pull later: ollama pull qwen2.5-coder:7b
        ) else (
            echo    Pulling qwen2.5-coder:7b (this may take a while)...
            ollama pull qwen2.5-coder:7b
        )
    ) else (
        echo    Model qwen2.5-coder:7b found
    )

    ollama list 2>nul | findstr "llama3.2:3b" >nul
    if %errorlevel% neq 0 (
        echo    Model llama3.2:3b not found.
        choice /c YN /m "Pull it now (suggested)?"
        if errorlevel 2 (
            echo    Skipped. Pull later: ollama pull llama3.2:3b
        ) else (
            echo    Pulling llama3.2:3b...
            ollama pull llama3.2:3b
        )
    ) else (
        echo    Model llama3.2:3b found
    )
)

echo.
echo ============================================
echo    Installation complete!
echo ============================================
echo.
echo Next steps:
echo   1. Start Ollama:     ollama serve
echo   2. Run journalist:   python journalist.py "Your topic"
echo   3. Or open the UI:   python journalist.py --web
echo.

if "%OLLAMA_MISSING%"=="1" (
    echo NOTE: Ollama was not detected. Install it from:
    echo       https://ollama.com/download
)

echo.
pause
