"""
AI 平台自动化基类

定义所有 AI 平台自动化类的通用接口
"""
import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Page, BrowserContext


class BaseAIAutomation(ABC):
    """AI 平台自动化基类"""
    
    PLATFORM_NAME: str = "Base"
    PLATFORM_URL: str = ""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def start_browser(self) -> None:
        """启动浏览器并打开目标平台"""
        import sys
        import os
        import subprocess
        sys.path.insert(0, str(Path(__file__).parent.parent))
        import config
        
        print(f"正在启动浏览器 ({self.PLATFORM_NAME})...")
        
        # 首次启动时自动安装 Playwright 浏览器
        await self._ensure_browser_installed()
        
        self.playwright = await async_playwright().start()
        
        # 查找系统已安装的浏览器
        chrome_path = self._find_chrome_executable()
        
        # 使用持久化上下文保持登录状态
        launch_options = {
            'user_data_dir': str(config.BROWSER_DATA_DIR),
            'headless': False,
            'viewport': {'width': 1280, 'height': 900},
            'args': ['--disable-blink-features=AutomationControlled']
        }
        
        # 如果找到系统 Chrome/Edge，使用它
        if chrome_path:
            launch_options['executable_path'] = chrome_path
            print(f"使用系统浏览器: {chrome_path}")
        
        try:
            self.context = await self.playwright.chromium.launch_persistent_context(**launch_options)
        except Exception as e:
            print(f"启动浏览器失败: {e}")
            print("尝试不使用指定路径...")
            # 移除 executable_path 重试
            if 'executable_path' in launch_options:
                del launch_options['executable_path']
            self.context = await self.playwright.chromium.launch_persistent_context(**launch_options)
        
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()
        
        print(f"正在打开 {self.PLATFORM_NAME}: {self.PLATFORM_URL}")
        # 使用 domcontentloaded 替代 networkidle，避免单页应用超时
        # 增加超时时间到 60 秒
        try:
            await self.page.goto(self.PLATFORM_URL, wait_until='domcontentloaded', timeout=60000)
        except Exception as e:
            print(f"页面加载超时，继续执行... {e}")
        
        # 额外等待页面稳定
        await asyncio.sleep(3)
        
        await self._check_login_status()
    
    async def _check_login_status(self) -> None:
        """等待页面加载完成"""
        await asyncio.sleep(2)
        print("浏览器已准备就绪")
    
    async def _ensure_browser_installed(self) -> None:
        """确保 Playwright 浏览器已安装，如果没有则自动安装"""
        import subprocess
        import os
        
        print("检查浏览器是否已安装...")
        
        # 检查是否可以找到 Playwright 浏览器
        try:
            # 尝试获取浏览器路径
            from playwright._impl._driver import compute_driver_executable
            driver_executable = compute_driver_executable()
            
            # 检查 chromium 是否存在
            result = subprocess.run(
                [driver_executable, 'install', 'chromium', '--dry-run'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if 'already installed' in result.stdout.lower() or result.returncode == 0:
                print("浏览器已安装 ✓")
                return
        except Exception as e:
            print(f"检查浏览器状态时出错: {e}")
        
        # 如果没有安装，则安装
        print("正在安装 Chromium 浏览器（首次运行需要，请稍候...）")
        try:
            # 使用 playwright install chromium
            result = subprocess.run(
                ['playwright', 'install', 'chromium'],
                capture_output=True,
                text=True,
                timeout=300  # 5 分钟超时
            )
            
            if result.returncode == 0:
                print("浏览器安装完成 ✓")
            else:
                print(f"安装输出: {result.stdout}")
                print(f"安装错误: {result.stderr}")
                raise Exception("浏览器安装失败")
                
        except FileNotFoundError:
            # playwright 命令不存在，尝试用 python -m playwright
            print("尝试使用 python -m playwright 安装...")
            import sys
            result = subprocess.run(
                [sys.executable, '-m', 'playwright', 'install', 'chromium'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("浏览器安装完成 ✓")
            else:
                raise Exception(f"浏览器安装失败: {result.stderr}")
    
    def _find_chrome_executable(self) -> Optional[str]:
        """查找系统已安装的 Chrome 或 Edge 浏览器"""
        import os
        import platform
        
        if platform.system() != 'Windows':
            return None
        
        # Windows 上常见的浏览器路径
        possible_paths = [
            # Chrome
            os.path.expandvars(r'%PROGRAMFILES%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
            # Edge
            os.path.expandvars(r'%PROGRAMFILES%\Microsoft\Edge\Application\msedge.exe'),
            os.path.expandvars(r'%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    @abstractmethod
    async def upload_images_and_send(self, image_paths: list, prompt: str) -> None:
        """
        上传一张或多张图片并发送提示词
        
        Args:
            image_paths: 图片文件路径列表（可以是1张或多张）
            prompt: 提示词文本
        """
        pass
    
    async def upload_image_and_send(self, image_path: str, prompt: str) -> None:
        """
        上传单张图片并发送提示词（兼容旧接口）
        
        Args:
            image_path: 图片文件路径
            prompt: 提示词文本
        """
        await self.upload_images_and_send([image_path], prompt)
    
    @abstractmethod
    async def wait_for_response_complete(self, timeout_ms: int = None) -> str:
        """
        等待 AI 完成回复
        
        Args:
            timeout_ms: 超时时间（毫秒）
        
        Returns:
            AI 的回复内容
        """
        pass
    
    async def close(self) -> None:
        """关闭浏览器"""
        print("正在关闭浏览器...")
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        print("浏览器已关闭")
    
    # ═══════════════════════════════════════════════════════════
    # 通用辅助方法
    # ═══════════════════════════════════════════════════════════
    
    async def _try_click(self, selectors: list, timeout: int = 3000) -> bool:
        """尝试点击多个选择器中的第一个可用的"""
        for selector in selectors:
            try:
                btn = self.page.locator(selector)
                if await btn.count() > 0:
                    await btn.first.click(timeout=timeout)
                    return True
            except:
                pass
        return False
    
    async def _try_find(self, selectors: list):
        """尝试查找多个选择器中的第一个可用的"""
        for selector in selectors:
            try:
                element = self.page.locator(selector).first
                if await element.count() > 0:
                    return element
            except:
                pass
        return None
    
    async def _wait_for_content_stable(self, content_selector: str, stable_duration: float = 5.0) -> None:
        """等待内容稳定（不再变化）"""
        last_content = ""
        stable_time = 0
        check_interval = 2.0
        
        while stable_time < stable_duration:
            try:
                messages = self.page.locator(content_selector)
                count = await messages.count()
                if count > 0:
                    current_content = await messages.last.text_content()
                else:
                    current_content = ""
            except:
                current_content = ""
            
            if current_content == last_content and current_content:
                stable_time += check_interval
                print(f"内容稳定中... {stable_time:.0f}s/{stable_duration:.0f}s")
            else:
                last_content = current_content
                stable_time = 0
            
            await asyncio.sleep(check_interval)
