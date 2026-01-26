@echo off
chcp 65001 >nul
title PDF AI Analyzer - Liquid Glass

cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════
echo   PDF AI Analyzer - Liquid Glass
echo   使用 PyMuPDF 进行 PDF 转换 (无需安装 Poppler)
echo ═══════════════════════════════════════════════════════════
echo.

REM 检查依赖是否已安装
echo [检查依赖]...
python3 -c "import fitz; import PySide6" 2>nul
if errorlevel 1 (
    echo 正在安装依赖...
    python3 -m pip install -r requirements.txt -q
)

REM 使用系统 python3 启动 PySide6 界面
echo [启动应用]...
python3 src/gui_pyside.py

REM 如果失败，尝试 venv
if errorlevel 1 (
    echo.
    echo 尝试使用 venv...
    if exist venv\Scripts\python.exe (
        venv\Scripts\python.exe src/gui_pyside.py
    ) else (
        echo [错误] 启动失败，请确保已安装依赖:
        echo   python3 -m pip install -r requirements.txt
    )
)

pause
