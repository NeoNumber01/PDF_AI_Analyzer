"""
ChatGPT 网页自动化模块

使用 Playwright 自动化操作 ChatGPT 网页版
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.base_automation import BaseAIAutomation
import config


class ChatGPTAutomation(BaseAIAutomation):
    """ChatGPT 网页自动化类"""
    
    PLATFORM_NAME = "ChatGPT"
    PLATFORM_URL = "https://chatgpt.com/"
    
    # ChatGPT 特定选择器
    SELECTORS = {
        'file_input': [
            'input[type="file"][accept*="image"]',
            'input[type="file"]',
        ],
        'attach_button': [
            '[data-testid="attachment-button"]',
            'button[aria-label*="Attach"]',
            'button[aria-label*="附件"]',
            'button[aria-label*="Upload"]',
        ],
        'input_box': [
            '#prompt-textarea',
            'textarea[placeholder*="Message"]',
            'textarea[placeholder*="消息"]',
            '[contenteditable="true"]',
        ],
        'send_button': [
            '[data-testid="send-button"]',
            'button[aria-label*="Send"]',
            'button[aria-label*="发送"]',
        ],
        'stop_button': [
            '[data-testid="stop-button"]',
            'button[aria-label*="Stop"]',
            'button[aria-label*="停止"]',
        ],
        'response_container': [
            '[data-message-author-role="assistant"]',
        ],
    }
    
    async def upload_images_and_send(self, image_paths: list, prompt: str) -> None:
        """
        上传一张或多张图片并发送提示词
        
        Args:
            image_paths: 图片文件路径列表
            prompt: 提示词文本
        """
        # 记录发送前的消息数量，用于后续检测空白回复
        self._initial_message_count = await self._get_message_count()
        print(f"[ChatGPT] 发送前消息数量: {self._initial_message_count}")
        
        # 依次上传所有图片
        for image_path in image_paths:
            print(f"[ChatGPT] 正在上传图片: {Path(image_path).name}")
            
            # 使用更精确的选择器 - 选择第一个文件输入
            file_input = self.page.locator('input[type="file"][accept*="image"]').first
            
            try:
                await file_input.set_input_files(image_path, timeout=10000)
                print(f"图片上传成功 ✓")
            except Exception as e:
                print(f"直接上传失败，尝试点击附件按钮...")
                # 尝试点击附件按钮
                await self._try_click(self.SELECTORS['attach_button'])
                await asyncio.sleep(1)
                
                # 再次尝试上传
                file_input = self.page.locator('input[type="file"][accept*="image"]').first
                await file_input.set_input_files(image_path)
                print(f"图片上传成功 ✓")
            
            await asyncio.sleep(2)  # 等待图片上传完成
        
        # 等待所有图片上传完成
        if len(image_paths) > 1:
            await asyncio.sleep(2)
        
        # 输入提示词
        print("[ChatGPT] 正在输入提示词...")
        
        input_box = await self._try_find(self.SELECTORS['input_box'])
        
        if input_box:
            await input_box.click()
            await input_box.fill(prompt)
        else:
            raise Exception("找不到输入框")
        
        await asyncio.sleep(1)
        
        # 点击发送按钮
        if await self._try_click(self.SELECTORS['send_button'], timeout=5000):
            print("消息已发送 ✓")
    
    async def wait_for_response_complete(self, timeout_ms: int = None) -> str:
        """
        等待 ChatGPT 完成回复
        
        Args:
            timeout_ms: 超时时间（毫秒）
        
        Returns:
            ChatGPT 的回复内容
        """
        if timeout_ms is None:
            timeout_ms = config.WAIT_TIMEOUT
        
        print("[ChatGPT] 等待回复...")
        
        # 等待一小段时间让回复开始
        await asyncio.sleep(5)
        
        # 方法1: 等待 "Stop" 按钮消失
        stop_found = False
        for selector in self.SELECTORS['stop_button']:
            try:
                stop_button = self.page.locator(selector)
                if await stop_button.count() > 0:
                    stop_found = True
                    print("ChatGPT 正在生成回复...")
                    # 等待 stop 按钮消失
                    await stop_button.wait_for(state='hidden', timeout=timeout_ms)
                    break
            except:
                pass
        
        if not stop_found:
            # 使用备用方法：等待内容稳定
            print("使用备用方法检测回复完成...")
            await self._wait_for_content_stable(self.SELECTORS['response_container'][0])
        
        # 获取最后一条回复内容
        await asyncio.sleep(2)
        response = await self._get_last_response()
        
        print("回复完成! ✓")
        return response
    
    async def _get_last_response(self) -> str:
        """获取最后一条 AI 回复"""
        try:
            messages = self.page.locator('[data-message-author-role="assistant"]')
            count = await messages.count()
            if count > 0:
                content = await messages.last.text_content()
                return content if content else ""
        except:
            pass
        return ""
    
    async def _get_message_count(self) -> int:
        """获取当前 AI 回复的数量"""
        try:
            messages = self.page.locator('[data-message-author-role="assistant"]')
            return await messages.count()
        except:
            return 0
    
    async def _detect_empty_response(self, initial_count: int) -> bool:
        """
        检测是否为空白回复
        
        Args:
            initial_count: 发送消息前的 AI 回复数量
        
        Returns:
            True 如果检测到空白回复
        """
        try:
            messages = self.page.locator('[data-message-author-role="assistant"]')
            current_count = await messages.count()
            
            # 如果有新回复产生
            if current_count > initial_count:
                # 获取最新回复的内容
                last_message = messages.last
                content = await last_message.text_content()
                
                if content is None or content.strip() == "":
                    print("[ChatGPT] 检测到空白回复")
                    return True
            else:
                # 没有新回复产生，可能是发送失败
                print("[ChatGPT] 警告：没有检测到新回复")
                return True
                
            return False
        except Exception as e:
            print(f"[ChatGPT] 检测回复时出错: {e}")
            return True


async def test():
    """测试函数"""
    bot = ChatGPTAutomation()
    try:
        await bot.start_browser()
        print("\n浏览器启动成功！")
        print("等待 30 秒后关闭...")
        await asyncio.sleep(30)
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(test())
