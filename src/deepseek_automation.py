"""
DeepSeek Chat 网页自动化模块

使用 Playwright 自动化操作 DeepSeek 网页版
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


class DeepSeekAutomation(BaseAIAutomation):
    """DeepSeek Chat 网页自动化类"""
    
    PLATFORM_NAME = "DeepSeek"
    PLATFORM_URL = "https://chat.deepseek.com/"
    
    async def upload_images_and_send(self, image_paths: list, prompt: str) -> None:
        """上传一张或多张图片并发送提示词 - 使用剪贴板粘贴方式"""
        
        # Step 1: 查找输入区域选择器
        input_selectors = [
            '#chat-input',
            'textarea[placeholder]',
            'textarea',
            'div[contenteditable="true"]',
            '.chat-input',
        ]
        
        async def find_and_focus_input():
            """查找并聚焦输入区域"""
            for selector in input_selectors:
                try:
                    element = self.page.locator(selector).first
                    if await element.count() > 0:
                        await element.click()
                        print(f"[DeepSeek] 聚焦输入区域: {selector}")
                        await asyncio.sleep(0.5)
                        return element
                except:
                    continue
            return None
        
        input_area = await find_and_focus_input()
        if not input_area:
            raise Exception("找不到输入区域")
        
        # Step 2: 依次上传所有图片
        for idx, image_path in enumerate(image_paths):
            print(f"[DeepSeek] 正在上传图片 {idx+1}/{len(image_paths)}: {Path(image_path).name}")
            
            # 每次上传前重新聚焦输入区域（解决递归输入问题）
            if idx > 0:
                await asyncio.sleep(0.5)
                input_area = await find_and_focus_input()
                if not input_area:
                    print(f"[DeepSeek] 警告: 无法聚焦输入区域, 跳过图片 {idx+1}")
                    continue
            
            upload_success = False
            
            # 优先尝试 file input 方式（更可靠）
            try:
                file_uploaded = await self._try_file_input_upload(image_path)
                if file_uploaded:
                    upload_success = True
                    print(f"[DeepSeek] 图片 {idx+1} 上传成功 (file input) ✓")
            except Exception as e:
                print(f"[DeepSeek] file input 方式失败: {e}")
            
            # 如果 file input 失败，尝试剪贴板方式
            if not upload_success:
                try:
                    await self._paste_image_from_clipboard(input_area, image_path)
                    upload_success = True
                    print(f"[DeepSeek] 图片 {idx+1} 粘贴成功 (clipboard) ✓")
                except Exception as e:
                    print(f"[DeepSeek] 剪贴板方式失败: {e}")
            
            if not upload_success:
                print(f"[DeepSeek] 警告: 图片 {idx+1} 上传失败，继续处理下一张")
                continue
            
            # 每张图片上传后都等待解析（解决递归输入问题）
            if len(image_paths) > 1:
                print(f"[DeepSeek] 等待图片 {idx+1} 解析...")
                await self._wait_for_image_parsed(timeout=15.0)
            
            await asyncio.sleep(1)
        
        # Step 3: 最终等待所有图片解析完成
        print("[DeepSeek] 等待所有图片解析...")
        await self._wait_for_image_parsed()
        print("[DeepSeek] 图片解析完成 ✓")
        
        # Step 4: 输入提示词
        print("[DeepSeek] 正在输入提示词...")
        input_area = await find_and_focus_input()
        if not input_area:
            raise Exception("输入提示词时找不到输入区域")
        
        await asyncio.sleep(0.3)
        
        # 对于 textarea 使用 fill，对于 contenteditable 使用 type
        try:
            tag = await input_area.evaluate("el => el.tagName.toLowerCase()")
            if tag == 'textarea':
                await input_area.fill(prompt)
            else:
                await self.page.keyboard.type(prompt, delay=15)
        except:
            await self.page.keyboard.type(prompt, delay=15)
        
        await asyncio.sleep(1)
        
        # Step 5: 发送消息
        send_selectors = [
            'button[type="submit"]',
            'button[aria-label*="Send" i]',
            'button[aria-label*="发送"]',
            '[data-testid="send-button"]',
            '.send-button',
            'button:has-text("发送")',
        ]
        
        sent = False
        for selector in send_selectors:
            try:
                btn = self.page.locator(selector).first
                if await btn.count() > 0 and await btn.is_visible():
                    await btn.click(timeout=3000)
                    sent = True
                    print("[DeepSeek] 消息已发送 ✓")
                    break
            except:
                continue
        
        if not sent:
            await self.page.keyboard.press('Enter')
            print("[DeepSeek] 消息已发送 (Enter) ✓")
    
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
            # 备用：DataTransfer 方式
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
    
    async def _try_file_input_upload(self, image_path: str) -> bool:
        """尝试传统 file input 上传，返回是否成功"""
        try:
            # 尝试多种 file input 选择器
            file_input_selectors = [
                'input[type="file"]',
                'input[type="file"][accept*="image"]',
                '#image-upload',
                '.upload-input',
            ]
            
            for selector in file_input_selectors:
                try:
                    file_inputs = self.page.locator(selector)
                    if await file_inputs.count() > 0:
                        await file_inputs.first.set_input_files(image_path)
                        await asyncio.sleep(1)  # 等待文件处理
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            print(f"[DeepSeek] file input 上传异常: {e}")
            return False
    
    async def _wait_for_image_parsed(self, timeout: float = 30.0):
        """
        等待图片解析完成
        DeepSeek 粘贴图片后会先解析，解析完成后才能发送
        """
        check_interval = 1.0
        elapsed = 0
        
        while elapsed < timeout:
            try:
                # 检测解析状态的多种可能指示器：
                # 1. 检查是否有加载指示器/进度条
                # 2. 检查发送按钮是否可用
                # 3. 检查是否有图片预览显示
                
                is_parsing = await self.page.evaluate('''
                    () => {
                        // 检查是否有加载中的指示器
                        const loadingIndicators = [
                            '.loading',
                            '.parsing',
                            '.uploading',
                            '[class*="loading"]',
                            '[class*="parsing"]',
                            '.spinner',
                            'svg.animate-spin',
                            '[class*="spin"]'
                        ];
                        
                        for (const sel of loadingIndicators) {
                            const el = document.querySelector(sel);
                            if (el && el.offsetParent !== null) {
                                return true; // 还在解析中
                            }
                        }
                        
                        // 检查发送按钮是否被禁用
                        const sendBtn = document.querySelector('button[type="submit"], button[aria-label*="Send" i], button[aria-label*="发送"]');
                        if (sendBtn && sendBtn.disabled) {
                            return true; // 按钮禁用，可能还在处理
                        }
                        
                        // 检查是否有图片预览
                        const imagePreviews = document.querySelectorAll('img[src*="blob:"], img[src*="data:"], .image-preview, [class*="preview"]');
                        if (imagePreviews.length > 0) {
                            return false; // 有图片预览，解析完成
                        }
                        
                        return false;
                    }
                ''')
                
                if not is_parsing:
                    # 额外等待一下确保完全就绪
                    await asyncio.sleep(1)
                    return
                    
            except Exception as e:
                print(f"[DeepSeek] 检测解析状态出错: {e}")
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
            
            if elapsed % 5 == 0:
                print(f"[DeepSeek] 图片解析中... {elapsed:.0f}s")
        
        print("[DeepSeek] 图片解析等待超时，继续执行...")
    
    async def wait_for_response_complete(self, timeout_ms: int = None) -> str:
        """等待 DeepSeek 完成回复"""
        if timeout_ms is None:
            timeout_ms = config.WAIT_TIMEOUT
        
        print("[DeepSeek] 等待回复...")
        await asyncio.sleep(3)
        
        max_wait = timeout_ms / 1000
        elapsed = 0
        check_interval = 2.0
        last_content_len = 0
        stable_count = 0
        required_stable = 2  # 连续 2 次长度不变
        
        while elapsed < max_wait:
            try:
                # 获取页面上的回复数量和最后回复的长度
                info = await self.page.evaluate('''
                    () => {
                        // DeepSeek 可能使用的选择器
                        const selectors = [
                            '.ds-markdown',
                            '[class*="markdown"]',
                            '.message-content',
                            '[class*="message"]',
                            '[class*="answer"]',
                            '[class*="response"]',
                            '.prose',
                        ];
                        
                        for (const sel of selectors) {
                            const els = document.querySelectorAll(sel);
                            if (els.length > 0) {
                                const last = els[els.length - 1];
                                return {
                                    selector: sel,
                                    count: els.length,
                                    length: last.textContent?.length || 0,
                                    preview: (last.textContent || '').slice(0, 50)
                                };
                            }
                        }
                        return { selector: null, count: 0, length: 0, preview: '' };
                    }
                ''')
                
                current_len = info.get('length', 0)
                
                # 只在首次或有变化时打印调试信息
                if elapsed == 0 or current_len != last_content_len:
                    print(f"[DeepSeek] 选择器: {info.get('selector')}, 回复数: {info.get('count')}, 长度: {current_len}")
                
                if current_len > 0 and current_len == last_content_len:
                    stable_count += 1
                    if stable_count >= required_stable:
                        print("[DeepSeek] 回复完成! ✓")
                        return await self._get_last_response()
                else:
                    stable_count = 0
                
                last_content_len = current_len
                
            except Exception as e:
                print(f"[DeepSeek] 检测出错: {e}")
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
            
            if elapsed % 10 == 0:
                print(f"[DeepSeek] 等待中... ({elapsed:.0f}s)")
        
        print("[DeepSeek] 等待超时")
        return await self._get_last_response()
    
    async def _wait_for_content_stable(self, stable_duration: float = 5.0):
        """等待内容稳定 - 备用方法"""
        last_len = 0
        stable_time = 0
        check_interval = 2.0
        
        while stable_time < stable_duration:
            content = await self._get_last_response()
            current_len = len(content)
            
            if current_len > 0 and current_len == last_len:
                stable_time += check_interval
            else:
                last_len = current_len
                stable_time = 0
            
            await asyncio.sleep(check_interval)
    
    async def _get_last_response(self) -> str:
        """获取最后一条 AI 回复"""
        try:
            return await self.page.evaluate('''
                () => {
                    // DeepSeek 常用选择器
                    const selectors = [
                        '.ds-markdown',
                        '[class*="markdown"]',
                        '.message-content',
                        '[class*="message"]',
                        '[class*="answer"]',
                        '.prose',
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
            return ""


async def test():
    bot = DeepSeekAutomation()
    try:
        await bot.start_browser()
        print("\n浏览器启动成功！等待 60 秒...")
        await asyncio.sleep(60)
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(test())
