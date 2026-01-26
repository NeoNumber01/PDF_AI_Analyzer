# PDF AI Analyzer 一键启动脚本 (PowerShell)
# Liquid Glass UI 版本
# 使用 PyMuPDF 进行 PDF 转换 (无需安装 Poppler)

$Host.UI.RawUI.WindowTitle = "PDF AI Analyzer"

Write-Host ""
Write-Host "  ═══════════════════════════════════════════════════════════" -ForegroundColor DarkCyan
Write-Host "    PDF AI Analyzer - Liquid Glass" -ForegroundColor Cyan
Write-Host "    使用 PyMuPDF 进行 PDF 转换 (无需安装 Poppler)" -ForegroundColor DarkGray
Write-Host "  ═══════════════════════════════════════════════════════════" -ForegroundColor DarkCyan
Write-Host ""

# 切换到脚本所在目录
Set-Location $PSScriptRoot

# 激活虚拟环境 (如果存在)
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
    Write-Host "[venv] 虚拟环境已激活" -ForegroundColor DarkGray
}

# 检查依赖
Write-Host "[检查依赖]..." -ForegroundColor Yellow
$checkResult = python3 -c "import fitz; import PySide6" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "正在安装依赖..." -ForegroundColor Yellow
    python3 -m pip install -r requirements.txt -q
}

# 启动 PySide6 GUI
Write-Host "[启动应用]..." -ForegroundColor Green
python3 src/gui_pyside.py

# 如果失败，显示错误信息
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[错误] 启动失败" -ForegroundColor Red
    Write-Host "请确保已安装依赖: python3 -m pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "按回车键退出"
}
