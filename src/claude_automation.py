"""
Claude 网页自动化模块

使用 Playwright 自动化操作 Claude 网页版
使用剪贴板粘贴方式上传图片
"""
import asyncio
import sys
import base64
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.base_automation import BaseAIAutomation
import config


class ClaudeAutomation(BaseAIAutomation):
    """Claude 网页自动化类"""
    
    PLATFORM_NAME = "Claude"
    PLATFORM_URL = "https://claude.ai/"
    
    async def upload_image_and_send(self, image_path: str, prompt: str) -> None:
        """上传图片并发送提示词 - 使用剪贴板粘贴方式"""
        print(f"[Claude] 正在上传图片: {Path(image_path).name}")
        
        # Step 1: 查找并聚焦输入区域
        input_selectors = [
            '.ProseMirror',
            'div[contenteditable="true"]',
            'div[data-placeholder]',
            'textarea',
            '.input-area',
        ]
        
        input_area = None
        for selector in input_selectors:
            try:
                element = self.page.locator(selector).first
                if await element.count() > 0:
                    input_area = element
                    await element.click()
                    print(f"[Claude] 聚焦输入区域: {selector}")
                    await asyncio.sleep(0.5)
                    break
            except:
                continue
        
        if not input_area:
            raise Exception("找不到输入区域")
        
        # Step 2: 使用剪贴板粘贴图片
        print("[Claude] 使用剪贴板粘贴方式...")
        
        try:
            await self._paste_image_from_clipboard(input_area, image_path)
            print("[Claude] 图片粘贴成功 ✓")
        except Exception as e:
            print(f"[Claude] 剪贴板方式失败: {e}")
            await self._try_file_input_upload(image_path)
        
        await asyncio.sleep(2)
        
        # Step 3: 输入提示词
        print("[Claude] 正在输入提示词...")
        await input_area.click()
        await asyncio.sleep(0.3)
        
        # Claude 使用 ProseMirror，需要键盘输入
        await self.page.keyboard.type(prompt, delay=15)
        
        await asyncio.sleep(1)
        
        # Step 4: 发送消息
        send_selectors = [
            'button[aria-label*="Send" i]',
            'button[aria-label*="发送"]',
            'button[type="submit"]',
            '[data-testid="send-button"]',
            'button:has-text("Send")',
        ]
        
        sent = False
        for selector in send_selectors:
            try:
                btn = self.page.locator(selector).first
                if await btn.count() > 0 and await btn.is_visible():
                    await btn.click(timeout=3000)
                    sent = True
                    print("[Claude] 消息已发送 ✓")
                    break
            except:
                continue
        
        if not sent:
            await self.page.keyboard.press('Enter')
            print("[Claude] 消息已发送 (Enter) ✓")
    
    async def _paste_image_from_clipboard(self, input_area, image_path: str):
        """通过剪贴板粘贴图片"""
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        image_ext = Path(image_path).suffix.lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        mime_type = mime_types.get(image_ext, 'image/png')
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 写入剪贴板
        paste_script = f'''
            async () => {{
                try {{
                    const base64 = "{image_base64}";
                    const mimeType = "{mime_type}";
                    
                    const byteCharacters = atob(base64);
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {{
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }}
                    const byteArray = new Uint8Array(byteNumbers);
                    const blob = new Blob([byteArray], {{ type: mimeType }});
                    
                    const clipboardItem = new ClipboardItem({{
                        [mimeType]: blob
                    }});
                    
                    await navigator.clipboard.write([clipboardItem]);
                    return true;
                }} catch (e) {{
                    console.error('Clipboard write failed:', e);
                    return false;
                }}
            }}
        '''
        
        success = await self.page.evaluate(paste_script)
        
        if success:
            await input_area.click()
            await asyncio.sleep(0.3)
            await self.page.keyboard.press('Control+v')
            await asyncio.sleep(2)
        else:
            await self._paste_via_datatransfer(input_area, image_path)
    
    async def _paste_via_datatransfer(self, input_area, image_path: str):
        """使用 DataTransfer 模拟粘贴"""
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        file_name = Path(image_path).name
        
        image_ext = Path(image_path).suffix.lower()
        mime_type = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg'}.get(
            image_ext.lstrip('.'), 'image/png'
        )
        
        script = f'''
            (element) => {{
                const base64 = "{image_base64}";
                const mimeType = "{mime_type}";
                const fileName = "{file_name}";
                
                const byteCharacters = atob(base64);
                const byteArray = new Uint8Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {{
                    byteArray[i] = byteCharacters.charCodeAt(i);
                }}
                const blob = new Blob([byteArray], {{ type: mimeType }});
                const file = new File([blob], fileName, {{ type: mimeType }});
                
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                
                const pasteEvent = new ClipboardEvent('paste', {{
                    bubbles: true,
                    cancelable: true,
                    clipboardData: dataTransfer
                }});
                
                element.dispatchEvent(pasteEvent);
                return true;
            }}
        '''
        
        await input_area.evaluate(script)
        await asyncio.sleep(2)
    
    async def _try_file_input_upload(self, image_path: str):
        """尝试传统 file input 上传"""
        try:
            file_inputs = self.page.locator('input[type="file"]')
            if await file_inputs.count() > 0:
                await file_inputs.first.set_input_files(image_path)
                print("[Claude] 使用 file input 上传成功")
        except:
            pass
    
    async def wait_for_response_complete(self, timeout_ms: int = None) -> str:
        """等待 Claude 完成回复"""
        if timeout_ms is None:
            timeout_ms = config.WAIT_TIMEOUT
        
        print("[Claude] 等待回复...")
        await asyncio.sleep(5)
        
        # 等待停止按钮消失
        stop_selectors = [
            'button[aria-label*="Stop" i]',
            'button[aria-label*="停止"]',
            '[data-testid="stop-button"]',
        ]
        
        for selector in stop_selectors:
            try:
                stop_button = self.page.locator(selector)
                if await stop_button.count() > 0:
                    print("[Claude] 正在生成回复...")
                    await stop_button.wait_for(state='hidden', timeout=timeout_ms)
                    break
            except:
                pass
        else:
            await self._wait_for_content_stable()
        
        await asyncio.sleep(2)
        response = await self._get_last_response()
        print("[Claude] 回复完成! ✓")
        return response
    
    async def _wait_for_content_stable(self, stable_duration: float = 5.0):
        """等待内容稳定"""
        last_content = ""
        stable_time = 0
        check_interval = 2.0
        
        while stable_time < stable_duration:
            try:
                content = await self.page.evaluate('''
                    () => {
                        const selectors = [
                            '[data-is-streaming]',
                            '.claude-response',
                            '.assistant-message',
                            '[data-message-author-role="assistant"]'
                        ];
                        for (const sel of selectors) {
                            const els = document.querySelectorAll(sel);
                            if (els.length > 0) {
                                return els[els.length - 1].textContent || '';
                            }
                        }
                        return '';
                    }
                ''')
            except:
                content = ""
            
            if content == last_content and content:
                stable_time += check_interval
            else:
                last_content = content
                stable_time = 0
            
            await asyncio.sleep(check_interval)
    
    async def _get_last_response(self) -> str:
        """获取最后一条 AI 回复"""
        try:
            return await self.page.evaluate('''
                () => {
                    const selectors = [
                        '[data-is-streaming]',
                        '.claude-response', 
                        '.assistant-message',
                        '[data-message-author-role="assistant"]'
                    ];
                    for (const sel of selectors) {
                        const els = document.querySelectorAll(sel);
                        if (els.length > 0) return els[els.length - 1].textContent || '';
                    }
                    return '';
                }
            ''')
        except:
            return ""


async def test():
    bot = ClaudeAutomation()
    try:
        await bot.start_browser()
        print("\n浏览器启动成功！等待 60 秒...")
        await asyncio.sleep(60)
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(test())
