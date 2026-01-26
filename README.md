# PDF AI Analyzer

将 PDF 文件逐页发送给 ChatGPT 进行中文解释的自动化工具。

## 功能

1. 将 PDF 每一页转换为图片
2. 自动打开 ChatGPT 网页版
3. 逐页发送图片并附带提示词
4. 等待 ChatGPT 回复完成后自动处理下一页
5. 直到所有页面处理完成

## 安装

### 1. 安装 Poppler (PDF 转图片依赖)

**Windows:**
1. 下载 [Poppler for Windows](https://github.com/osber/poppler-windows/releases)
2. 解压到 `C:\poppler`
3. 将 `C:\poppler\bin` 添加到系统 PATH 环境变量

### 2. 创建虚拟环境并安装依赖

```bash
# 进入项目目录
cd "c:\Users\Shu Leo\Desktop\chatgpt导出\PDF_AI_Analyzer"

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境 (Windows PowerShell)
.\venv\Scripts\activate

# 安装依赖
python3 -m pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

## 使用方法

### 运行程序

```bash
# 方法1: 命令行参数
python3 src/main.py "path/to/your/file.pdf"

# 方法2: 交互式输入
python3 src/main.py
# 然后输入 PDF 路径
```

### 首次运行

1. 程序会自动打开浏览器并导航到 ChatGPT
2. 如果未登录，请手动登录你的 ChatGPT 账号
3. 登录状态会被保存，下次运行无需重新登录

## 配置

编辑 `config.py` 可以修改以下配置：

| 配置项 | 默认值 | 说明 |
|-------|-------|------|
| `PROMPT_TEXT` | "请用中文详细解释一下这张图片的内容。" | 发送给 ChatGPT 的提示词 |
| `PDF_DPI` | 200 | PDF 转图片的分辨率 |
| `WAIT_TIMEOUT` | 120000 | 等待回复的超时时间（毫秒） |
| `DELAY_BETWEEN_PAGES` | 3 | 页间等待时间（秒） |

## 项目结构

```
PDF_AI_Analyzer/
├── browser_data/          # 浏览器数据（保持登录状态）
├── output/                # 转换后的图片
├── src/
│   ├── __init__.py
│   ├── pdf_converter.py   # PDF 转图片模块
│   ├── chatgpt_automation.py  # ChatGPT 自动化
│   └── main.py            # 主程序
├── config.py              # 配置文件
├── requirements.txt       # 依赖列表
└── README.md
```

## 注意事项

1. **登录状态**：首次运行需要手动登录 ChatGPT，之后会自动保持登录
2. **网络要求**：需要稳定的网络连接
3. **运行时间**：根据 PDF 页数和 ChatGPT 回复速度，可能需要较长时间
4. **界面变化**：如果 ChatGPT 网页更新，可能需要更新选择器

## 故障排除

### PDF 转换失败
- 确保 Poppler 已正确安装并添加到 PATH
- 重新打开终端使 PATH 变更生效

### 登录检测不到
- 手动登录 ChatGPT 后，程序会自动检测到并继续

### 上传失败
- 检查图片是否正确生成在 `output/` 目录
- 尝试增加 `DELAY_BETWEEN_PAGES` 配置值
