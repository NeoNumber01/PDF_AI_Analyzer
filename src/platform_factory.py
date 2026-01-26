"""
AI 平台工厂模块

根据平台 ID 创建对应的自动化实例
"""
import sys
from pathlib import Path
from typing import Dict, Type

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.base_automation import BaseAIAutomation


# 平台配置
AI_PLATFORMS = {
    "chatgpt": {
        "name": "ChatGPT",
        "url": "https://chatgpt.com/",
        "module": "src.chatgpt_automation",
        "class": "ChatGPTAutomation",
    },
    "gemini": {
        "name": "Google Gemini",
        "url": "https://gemini.google.com/",
        "module": "src.gemini_automation",
        "class": "GeminiAutomation",
    },
    "deepseek": {
        "name": "DeepSeek",
        "url": "https://chat.deepseek.com/",
        "module": "src.deepseek_automation",
        "class": "DeepSeekAutomation",
    },
    "claude": {
        "name": "Claude",
        "url": "https://claude.ai/",
        "module": "src.claude_automation",
        "class": "ClaudeAutomation",
    },
}

DEFAULT_PLATFORM = "chatgpt"


def get_platform_names() -> Dict[str, str]:
    """获取所有平台 ID 和名称的映射"""
    return {k: v["name"] for k, v in AI_PLATFORMS.items()}


def get_automation(platform_id: str) -> BaseAIAutomation:
    """
    根据平台 ID 获取对应的自动化实例
    
    Args:
        platform_id: 平台标识符 (chatgpt, gemini, deepseek, claude)
    
    Returns:
        对应平台的自动化实例
    
    Raises:
        ValueError: 如果平台 ID 无效
    """
    if platform_id not in AI_PLATFORMS:
        raise ValueError(f"不支持的平台: {platform_id}。可用平台: {list(AI_PLATFORMS.keys())}")
    
    platform_config = AI_PLATFORMS[platform_id]
    module_name = platform_config["module"]
    class_name = platform_config["class"]
    
    # 动态导入模块
    import importlib
    module = importlib.import_module(module_name)
    automation_class = getattr(module, class_name)
    
    return automation_class()


def list_platforms():
    """列出所有支持的平台"""
    print("支持的 AI 平台:")
    print("-" * 40)
    for pid, info in AI_PLATFORMS.items():
        print(f"  {pid:12} - {info['name']:20} ({info['url']})")


if __name__ == "__main__":
    list_platforms()
