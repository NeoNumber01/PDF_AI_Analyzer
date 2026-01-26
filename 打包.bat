@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════
echo   PDF AI Analyzer - 完整打包脚本
echo ═══════════════════════════════════════════════════════════
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python
    pause
    exit /b 1
)

:: 安装/更新 PyInstaller
echo [1/4] 安装 PyInstaller...
pip install --upgrade pyinstaller

:: 清理旧的打包文件
echo [2/4] 清理旧文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: 创建 spec 文件并打包
echo [3/4] 开始打包...
echo.

python -c "
import PyInstaller.__main__
import sys
import os

# 获取 PySide6 路径
try:
    import PySide6
    pyside6_path = os.path.dirname(PySide6.__file__)
    print(f'PySide6 路径: {pyside6_path}')
except:
    pyside6_path = None
    print('警告: 找不到 PySide6')

# 打包参数
args = [
    'src/gui_pyside.py',
    '--noconfirm',
    '--onedir',
    '--windowed',
    '--name=PDF_AI_Analyzer',
    '--add-data=config.py;.',
    '--add-data=src;src',
]

# 添加 PySide6
if pyside6_path:
    args.append(f'--add-data={pyside6_path};PySide6')

# 隐藏导入
hidden = [
    'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets',
    'playwright', 'playwright.async_api',
    'fitz', 'PIL', 'PIL.Image',
]
for h in hidden:
    args.append(f'--hidden-import={h}')

PyInstaller.__main__.run(args)
"

if errorlevel 1 (
    echo.
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo [4/4] 打包完成！
echo.
echo 输出目录: dist\PDF_AI_Analyzer\
echo.
pause
