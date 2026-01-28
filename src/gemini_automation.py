"""
Google Gemini 网页自动化模块

使用 Playwright 自动化操作 Gemini 网页版
使用剪贴板粘贴方式上传图片 (2025 版本)
"""
import asyncio
import sys
import base64
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.base_automation import BaseAIAutomation
import config


class GeminiAutomation(BaseAIAutomation):
    """Google Gemini 网页自动化类"""
    
    PLATFORM_NAME = "Google Gemini"
    PLATFORM_URL = "https://gemini.google.com/app"
    
    async def upload_images_and_send(self, image_paths: list, prompt: str) -> None:
        """上传一张或多张图片并发送提示词 - 使用剪贴板粘贴方式"""
        
        # Step 1: 查找并聚焦输入区域
        input_selectors = [
            'div.ql-editor',
            'div[contenteditable="true"]',
            'rich-textarea',
            '.text-input-field_textarea',
            'p[data-placeholder]',
        ]
        
        input_area = None
        for selector in input_selectors:
            try:
                element = self.page.locator(selector).first
                if await element.count() > 0:
                    input_area = element
                    await element.click()
                    print(f"[Gemini] 聚焦输入区域: {selector}")
                    await asyncio.sleep(0.5)
                    break
            except:
                continue
        
        if not input_area:
            raise Exception("找不到输入区域")
        
        # Step 2: 依次上传所有图片
        for image_path in image_paths:
            print(f"[Gemini] 正在上传图片: {Path(image_path).name}")
            
            try:
                # 读取图片文件
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                # 获取图片 MIME 类型
                image_ext = Path(image_path).suffix.lower()
                mime_types = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp',
                }
                mime_type = mime_types.get(image_ext, 'image/png')
                
                # 转为 base64
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                
                # 使用 JavaScript 创建 ClipboardItem 并粘贴
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
                            console.log('Image copied to clipboard');
                            return true;
                        }} catch (e) {{
                            console.error('Clipboard write failed:', e);
                            return false;
                        }}
                    }}
                '''
                
                clipboard_success = await self.page.evaluate(paste_script)
                
                if clipboard_success:
                    # 聚焦输入框并粘贴
                    await input_area.click()
                    await asyncio.sleep(0.3)
                    
                    # 使用 Ctrl+V 粘贴
                    await self.page.keyboard.press('Control+v')
                    await asyncio.sleep(2)  # 等待图片加载
                    
                    print(f"[Gemini] 图片粘贴成功 ✓")
                else:
                    raise Exception("剪贴板写入失败")
                    
            except Exception as e:
                print(f"[Gemini] 剪贴板方式失败: {e}")
                
                # 备用方法：使用 DataTransfer 模拟拖放
                print("[Gemini] 尝试使用 DataTransfer 方式...")
                try:
                    await self._upload_via_datatransfer(input_area, image_path)
                except Exception as e2:
                    print(f"[Gemini] DataTransfer 方式也失败: {e2}")
                    raise Exception(f"所有上传方式都失败")
            
            await asyncio.sleep(1)
        
        # 等待所有图片上传完成
        if len(image_paths) > 1:
            await asyncio.sleep(2)
        
        # Step 3: 输入提示词
        print("[Gemini] 正在输入提示词...")
        
        # 确保聚焦在输入区域
        await input_area.click()
        await asyncio.sleep(0.3)
        
        # 使用键盘输入
        await self.page.keyboard.type(prompt, delay=15)
        
        await asyncio.sleep(1)
        
        # Step 4: 发送消息
        send_selectors = [
            'button[aria-label*="发送" i]',
            'button[aria-label*="send" i]',
            'button[aria-label*="提交" i]',
            'button[aria-label*="submit" i]',
            '.send-button',
            'button[type="submit"]',
        ]
        
        sent = False
        for selector in send_selectors:
            try:
                btn = self.page.locator(selector).first
                if await btn.count() > 0:
                    # 检查按钮是否可见且可用
                    if await btn.is_visible() and await btn.is_enabled():
                        await btn.click(timeout=3000)
                        sent = True
                        print("[Gemini] 消息已发送 ✓")
                        break
            except:
                continue
        
        if not sent:
            # 尝试按 Enter 发送
            await self.page.keyboard.press('Enter')
            print("[Gemini] 消息已发送 (Enter) ✓")
    
    async def _upload_via_datatransfer(self, input_area, image_path: str):
        """使用 DataTransfer 模拟文件拖放"""
        
        # 读取文件
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        file_name = Path(image_path).name
        
        image_ext = Path(image_path).suffix.lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        mime_type = mime_types.get(image_ext, 'image/png')
        
        # 使用 JavaScript 创建并触发 paste 事件
        script = f'''
            (element) => {{
                const base64 = "{image_base64}";
                const mimeType = "{mime_type}";
                const fileName = "{file_name}";
                
                // 将 base64 转换为 blob
                const byteCharacters = atob(base64);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {{
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }}
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], {{ type: mimeType }});
                
                // 创建 File 对象
                const file = new File([blob], fileName, {{ type: mimeType }});
                
                // 创建 DataTransfer
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                
                // 创建并触发 paste 事件
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
        print("[Gemini] DataTransfer 粘贴完成")
    
    async def wait_for_response_complete(self, timeout_ms: int = None) -> str:
        """等待 Gemini 完成回复"""
        if timeout_ms is None:
            timeout_ms = config.WAIT_TIMEOUT
        
        print("[Gemini] 等待回复...")
        await asyncio.sleep(5)
        
        # 等待内容稳定
        await self._wait_for_gemini_stable()
        
        await asyncio.sleep(2)
        response = await self._get_last_response()
        print("[Gemini] 回复完成! ✓")
        return response
    
    async def _wait_for_gemini_stable(self, stable_duration: float = 5.0):
        """等待 Gemini 回复稳定"""
        last_content = ""
        stable_time = 0
        check_interval = 2.0
        max_wait = 120
        total_wait = 0
        
        while stable_time < stable_duration and total_wait < max_wait:
            try:
                current_content = await self.page.evaluate('''
                    () => {
                        const selectors = [
                            '.model-response-text',
                            '.response-content', 
                            '.markdown-content',
                            '[data-message-author-role="model"]',
                            'message-content'
                        ];
                        
                        for (const sel of selectors) {
                            const elements = document.querySelectorAll(sel);
                            if (elements.length > 0) {
                                return elements[elements.length - 1].textContent || '';
                            }
                        }
                        return '';
                    }
                ''')
            except:
                current_content = ""
            
            if current_content == last_content and current_content:
                stable_time += check_interval
                print(f"[Gemini] 内容稳定中... {stable_time:.0f}s/{stable_duration:.0f}s")
            else:
                last_content = current_content
                stable_time = 0
            
            await asyncio.sleep(check_interval)
            total_wait += check_interval
    
    async def _get_last_response(self) -> str:
        """获取最后一条 AI 回复"""
        try:
            result = await self.page.evaluate('''
                () => {
                    const selectors = [
                        '.model-response-text',
                        '.response-content',
                        '.markdown-content',
                        '[data-message-author-role="model"]'
                    ];
                    
                    for (const sel of selectors) {
                        const elements = document.querySelectorAll(sel);
                        if (elements.length > 0) {
                            return elements[elements.length - 1].textContent || '';
                        }
                    }
                    return '';
                }
            ''')
            return result
        except:
            pass
        return ""


async def test():
    """测试函数"""
    bot = GeminiAutomation()
    try:
        await bot.start_browser()
        print("\n浏览器启动成功！")
        print("等待 60 秒后关闭...")
        await asyncio.sleep(60)
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(test())
