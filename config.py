"""
PDF AI Analyzer 配置文件
"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 浏览器用户数据目录（用于保持登录状态）
BROWSER_DATA_DIR = PROJECT_ROOT / "browser_data"

# ChatGPT URL
CHATGPT_URL = "https://chatgpt.com/"

# 默认提示词
PROMPT_TEXT = "请用中文详细解释一下这张图片的内容。"

# 等待超时时间（毫秒）
WAIT_TIMEOUT = 120000  # 2分钟

# 图片输出目录
OUTPUT_DIR = PROJECT_ROOT / "output"

# PDF 转图片的 DPI（分辨率）
PDF_DPI = 200

# 每次发送后的等待时间（秒）
DELAY_BETWEEN_PAGES = 3

# 确保目录存在
OUTPUT_DIR.mkdir(exist_ok=True)
BROWSER_DATA_DIR.mkdir(exist_ok=True)
