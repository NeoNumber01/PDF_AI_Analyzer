# PDF AI Analyzer

<p align="center">
  <strong>🤖 多平台 AI 图像分析自动化工具</strong>
</p>

<p align="center">
  <a href="./README_EN.md">English</a> | 简体中文
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/GUI-PySide6-green.svg" alt="GUI">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

---

## ✨ 功能特性

PDF AI Analyzer 是一款自动化工具，能够将 PDF 文件逐页转换为图片，并自动发送给多个主流 AI 平台进行分析和解释。

### 🎯 核心功能

- **📄 PDF 转图片**: 使用 PyMuPDF 将 PDF 每一页高质量转换为图片（无需安装 Poppler）
- **🤖 多平台支持**: 支持 ChatGPT、Claude、Google Gemini、DeepSeek 四大 AI 平台
- **🔄 自动化处理**: 自动上传图片、发送提示词、等待回复、处理下一页
- **💾 会话保持**: 浏览器登录状态自动保存，无需重复登录
- **🎨 现代化界面**: 精美的 Glassmorphism（毛玻璃）风格 GUI

### 🌐 支持的 AI 平台

| 平台 | 网址 | 状态 |
|------|------|------|
| ChatGPT | chatgpt.com | ✅ 支持 |
| Google Gemini | gemini.google.com | ✅ 支持 |
| DeepSeek | chat.deepseek.com | ✅ 支持 |
| Claude | claude.ai | ✅ 支持 |

---

## 📦 安装

### 系统要求

- **操作系统**: Windows 10/11
- **Python**: 3.11 或更高版本
- **浏览器**: Chrome 或 Edge（Playwright 会自动处理）

### 安装步骤

```powershell
# 1. 克隆项目
git clone https://github.com/NeoNumber01/PDF_AI_Analyzer.git
cd PDF_AI_Analyzer

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境 (PowerShell)
.\venv\Scripts\Activate.ps1
# 或者 (CMD)
.\venv\Scripts\activate.bat

# 4. 安装依赖
pip install -r requirements.txt

# 5. 安装 Playwright 浏览器
playwright install chromium
```

> 💡 **提示**: 本项目使用 PyMuPDF 进行 PDF 转图片，无需安装 Poppler 等外部依赖。

---

## 🚀 使用方法

### 方式一：图形界面（推荐）

**Windows 用户**：直接双击 `启动.bat` 或在 PowerShell 中运行：

```powershell
.\启动.ps1
```

**或者手动运行**：

```powershell
python src/gui_pyside.py
```

### 方式二：命令行

```powershell
# 交互式输入
python src/main.py

# 指定 PDF 文件
python src/main.py "path/to/your/file.pdf"
```

### 使用流程

1. **启动程序** - 运行启动脚本或 GUI
2. **选择 AI 平台** - 在界面中选择要使用的 AI 平台
3. **启动浏览器** - 点击"启动浏览器"按钮
4. **登录账号** - 首次使用需要手动登录对应 AI 平台的账号
5. **选择 PDF** - 选择要分析的 PDF 文件
6. **开始处理** - 点击"开始处理"，程序会自动逐页发送并等待回复

> ⚠️ **首次运行**: 需要手动登录 AI 平台账号，登录状态会被保存到 `browser_data/` 目录，下次运行无需重新登录。

---

## ⚙️ 配置

编辑 `config.py` 文件可以自定义以下配置：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `PROMPT_TEXT` | "请用中文详细解释..." | 发送给 AI 的提示词 |
| `PDF_DPI` | 200 | PDF 转图片的分辨率 |
| `WAIT_TIMEOUT` | 120000 | 等待回复的超时时间（毫秒） |
| `DELAY_BETWEEN_PAGES` | 3 | 页面间的等待时间（秒） |

---

## 📁 项目结构

```
PDF_AI_Analyzer/
├── src/
│   ├── gui_pyside.py         # PySide6 图形界面（主入口）
│   ├── base_automation.py    # AI 平台自动化基类
│   ├── chatgpt_automation.py # ChatGPT 自动化
│   ├── claude_automation.py  # Claude 自动化
│   ├── gemini_automation.py  # Gemini 自动化
│   ├── deepseek_automation.py# DeepSeek 自动化
│   ├── platform_factory.py   # 平台工厂模式
│   ├── pdf_converter.py      # PDF 转图片模块
│   └── main.py               # 命令行入口
├── browser_data/             # 浏览器数据（保持登录状态）
├── output/                   # 转换后的图片
├── config.py                 # 配置文件
├── requirements.txt          # Python 依赖
├── 启动.bat                  # Windows 启动脚本
├── 启动.ps1                  # PowerShell 启动脚本
└── 打包.bat                  # PyInstaller 打包脚本
```

---

## 🔧 故障排除

### PDF 转换失败
- 确保 PyMuPDF 已正确安装：`pip install PyMuPDF`
- 检查 PDF 文件是否损坏或加密

### 浏览器启动失败
- 运行 `playwright install chromium` 安装浏览器
- 检查 `browser_data/` 目录权限

### 登录状态丢失
- 删除 `browser_data/` 目录后重新登录
- 确保浏览器正常关闭而非强制结束

### AI 回复超时
- 增加 `config.py` 中的 `WAIT_TIMEOUT` 值
- 检查网络连接稳定性

---

## 📝 依赖列表

```
PyMuPDF>=1.23.0      # PDF 处理
Pillow>=10.0.0       # 图像处理
playwright>=1.40.0   # 浏览器自动化
python-dotenv>=1.0.0 # 环境变量
PySide6>=6.6.0       # GUI 框架
customtkinter>=5.2.0 # 备用 GUI (可选)
pywinstyles>=1.8     # Windows 风格 (可选)
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。
