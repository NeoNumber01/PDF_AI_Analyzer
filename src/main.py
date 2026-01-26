"""
PDF AI Analyzer 主程序

将 PDF 逐页发送给 ChatGPT 进行中文解释
支持批量处理多个 PDF 文件
"""
import asyncio
import sys
from pathlib import Path
from typing import List

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pdf_converter import convert_pdf_to_images
from src.chatgpt_automation import ChatGPTAutomation
import config


def get_user_input(prompt: str, default: str = None) -> str:
    """获取用户输入，支持默认值"""
    if default:
        user_input = input(f"{prompt} (默认: {default}): ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def get_custom_prompt() -> str:
    """获取自定义提示词"""
    print("\n" + "-"*50)
    print("设置提示词")
    print("-"*50)
    print(f"默认提示词: {config.PROMPT_TEXT}")
    print()
    
    choice = input("使用默认提示词? (Y/n): ").strip().lower()
    
    if choice == 'n':
        print("\n请输入自定义提示词 (输入完成后按 Enter):")
        custom_prompt = input("> ").strip()
        if custom_prompt:
            print(f"已设置提示词: {custom_prompt}")
            return custom_prompt
        else:
            print("输入为空，使用默认提示词")
            return config.PROMPT_TEXT
    else:
        return config.PROMPT_TEXT


def collect_pdf_files() -> List[str]:
    """收集要处理的 PDF 文件列表"""
    print("\n" + "="*60)
    print("   批量 PDF 文件管理")
    print("="*60)
    
    pdf_files = []
    
    print("\n请添加要处理的 PDF 文件")
    print("操作说明:")
    print("  - 输入 PDF 文件路径（可拖入文件）")
    print("  - 输入 'done' 或直接按 Enter 完成添加")
    print("  - 输入 'list' 查看当前列表")
    print("  - 输入 'remove N' 移除第 N 个文件")
    print("  - 输入 'clear' 清空列表")
    print("  - 输入 'up N' 将第 N 个文件上移")
    print("  - 输入 'down N' 将第 N 个文件下移")
    print()
    
    while True:
        if pdf_files:
            print(f"\n当前已添加 {len(pdf_files)} 个文件")
        
        user_input = input("\n添加 PDF (或输入命令): ").strip().strip('"').strip("'")
        
        if not user_input or user_input.lower() == 'done':
            if pdf_files:
                break
            else:
                print("请至少添加一个 PDF 文件")
                continue
        
        # 命令处理
        if user_input.lower() == 'list':
            if pdf_files:
                print("\n当前 PDF 列表（按处理顺序）:")
                for i, f in enumerate(pdf_files, 1):
                    print(f"  {i}. {Path(f).name}")
            else:
                print("列表为空")
            continue
        
        if user_input.lower() == 'clear':
            pdf_files.clear()
            print("列表已清空")
            continue
        
        if user_input.lower().startswith('remove '):
            try:
                idx = int(user_input.split()[1]) - 1
                if 0 <= idx < len(pdf_files):
                    removed = pdf_files.pop(idx)
                    print(f"已移除: {Path(removed).name}")
                else:
                    print("无效的序号")
            except:
                print("用法: remove N (N为文件序号)")
            continue
        
        if user_input.lower().startswith('up '):
            try:
                idx = int(user_input.split()[1]) - 1
                if 1 <= idx < len(pdf_files):
                    pdf_files[idx], pdf_files[idx-1] = pdf_files[idx-1], pdf_files[idx]
                    print(f"已上移: {Path(pdf_files[idx-1]).name}")
                else:
                    print("无法上移（已在顶部或序号无效）")
            except:
                print("用法: up N (N为文件序号)")
            continue
        
        if user_input.lower().startswith('down '):
            try:
                idx = int(user_input.split()[1]) - 1
                if 0 <= idx < len(pdf_files) - 1:
                    pdf_files[idx], pdf_files[idx+1] = pdf_files[idx+1], pdf_files[idx]
                    print(f"已下移: {Path(pdf_files[idx+1]).name}")
                else:
                    print("无法下移（已在底部或序号无效）")
            except:
                print("用法: down N (N为文件序号)")
            continue
        
        # 添加文件
        pdf_path = Path(user_input)
        if pdf_path.exists():
            if pdf_path.suffix.lower() == '.pdf':
                pdf_files.append(str(pdf_path))
                print(f"已添加: {pdf_path.name} (第 {len(pdf_files)} 个)")
            else:
                print("错误: 不是 PDF 文件")
        else:
            print(f"错误: 文件不存在 - {user_input}")
    
    # 显示最终列表
    print("\n" + "-"*50)
    print("最终处理顺序:")
    print("-"*50)
    for i, f in enumerate(pdf_files, 1):
        print(f"  {i}. {Path(f).name}")
    print("-"*50)
    
    return pdf_files


async def wait_for_user_ready(bot: ChatGPTAutomation) -> str:
    """等待用户完成登录、选择模型后确认开始"""
    import concurrent.futures
    
    print("\n" + "="*60)
    print("   PDF AI Analyzer - 交互式设置")
    print("="*60)
    
    # 步骤1: 等待登录
    print("\n[步骤 1] 登录 ChatGPT")
    print("-"*50)
    print("请在浏览器中登录你的 ChatGPT 账号")
    print("（如果已登录则可直接继续）")
    
    def wait_step1():
        input("\n>>> 登录完成后按 Enter 继续 <<<")
    
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, wait_step1)
    
    # 步骤2: 选择模型和模式
    print("\n[步骤 2] 选择模型和模式")
    print("-"*50)
    print("请在浏览器中完成以下操作:")
    print("  1. 点击左上角选择你想使用的模型 (如 GPT-4, GPT-4o 等)")
    print("  2. 如需开启特定模式，请在网页上设置")
    print("  3. 确保你处于一个新的聊天窗口")
    
    def wait_step2():
        input("\n>>> 模型选择完成后按 Enter 继续 <<<")
    
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, wait_step2)
    
    # 步骤3: 设置提示词
    print("\n[步骤 3] 设置提示词")
    
    def get_prompt():
        return get_custom_prompt()
    
    with concurrent.futures.ThreadPoolExecutor() as pool:
        prompt = await loop.run_in_executor(pool, get_prompt)
    
    # 步骤4: 确认开始
    print("\n[步骤 4] 确认开始")
    print("-"*50)
    print("准备就绪！程序将开始自动处理 PDF")
    print(f"提示词: {prompt}")
    
    def wait_step4():
        input("\n>>> 按 Enter 开始执行 <<<")
    
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, wait_step4)
    
    return prompt


async def process_single_pdf(bot: ChatGPTAutomation, pdf_path: str, prompt: str, pdf_index: int, total_pdfs: int) -> bool:
    """
    处理单个 PDF 文件
    
    Returns:
        是否成功完成
    """
    pdf_name = Path(pdf_path).name
    
    print("\n" + "="*60)
    print(f"  处理 PDF [{pdf_index}/{total_pdfs}]: {pdf_name}")
    print("="*60)
    
    # 转换 PDF 为图片
    print("\n[转换] PDF 转图片...")
    try:
        image_paths = convert_pdf_to_images(pdf_path)
    except Exception as e:
        print(f"错误: PDF 转换失败 - {e}")
        return False
    
    total_pages = len(image_paths)
    print(f"共 {total_pages} 页")
    
    # 逐页处理
    for i, image_path in enumerate(image_paths, start=1):
        print(f"\n>>> [{pdf_name}] 第 {i}/{total_pages} 页 <<<")
        
        try:
            # 发送图片和提示词
            await bot.upload_image_and_send(image_path, prompt)
            
            # 等待回复完成
            await bot.wait_for_response_complete()
            
            print(f"第 {i} 页处理完成 ✓")
            
            # 页间延迟
            if i < total_pages:
                print(f"等待 {config.DELAY_BETWEEN_PAGES} 秒...")
                await asyncio.sleep(config.DELAY_BETWEEN_PAGES)
        except Exception as e:
            print(f"错误: 处理第 {i} 页时出错 - {e}")
            return False
    
    print(f"\n✓ [{pdf_name}] 处理完成!")
    return True


async def analyze_pdfs(pdf_files: List[str]) -> None:
    """
    批量分析 PDF 文件
    
    Args:
        pdf_files: PDF 文件路径列表
    """
    total_pdfs = len(pdf_files)
    
    print("\n" + "="*60)
    print(f"   准备处理 {total_pdfs} 个 PDF 文件")
    print("="*60)
    
    # 初始化 ChatGPT 自动化
    print("\n[启动浏览器] 打开 ChatGPT")
    print("-"*40)
    
    bot = ChatGPTAutomation()
    
    try:
        await bot.start_browser()
        
        # 等待用户完成登录和设置
        prompt = await wait_for_user_ready(bot)
        
        print("\n" + "="*60)
        print("开始批量处理")
        print("="*60)
        
        success_count = 0
        failed_files = []
        
        for idx, pdf_path in enumerate(pdf_files, start=1):
            success = await process_single_pdf(bot, pdf_path, prompt, idx, total_pdfs)
            
            if success:
                success_count += 1
            else:
                failed_files.append(Path(pdf_path).name)
            
            # PDF 间延迟
            if idx < total_pdfs:
                print(f"\n准备处理下一个 PDF (等待 5 秒)...")
                await asyncio.sleep(5)
        
        # 总结
        print("\n" + "="*60)
        print("🎉 批量处理完成!")
        print("="*60)
        print(f"成功: {success_count}/{total_pdfs}")
        
        if failed_files:
            print(f"\n失败的文件:")
            for f in failed_files:
                print(f"  - {f}")
        
        # 保持浏览器打开以便查看结果
        print("\n浏览器将保持打开，你可以查看和复制结果")
        print("按 Ctrl+C 或关闭窗口退出程序")
        
        try:
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            pass
    
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot.close()


def main():
    """命令行入口"""
    print("="*60)
    print("   PDF AI Analyzer - 批量处理版")
    print("="*60)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 命令行提供了文件
        pdf_files = []
        for arg in sys.argv[1:]:
            path = Path(arg.strip('"').strip("'"))
            if path.exists() and path.suffix.lower() == '.pdf':
                pdf_files.append(str(path))
                print(f"已添加: {path.name}")
            else:
                print(f"跳过无效文件: {arg}")
        
        if not pdf_files:
            print("错误: 没有有效的 PDF 文件")
            input("按 Enter 退出...")
            sys.exit(1)
        
        # 询问是否需要调整顺序
        print(f"\n已添加 {len(pdf_files)} 个文件")
        choice = input("是否需要调整顺序或添加更多文件? (y/N): ").strip().lower()
        
        if choice == 'y':
            # 进入交互式管理
            for f in pdf_files:
                print(f"  - {Path(f).name}")
            pdf_files = collect_pdf_files()
    else:
        # 交互式添加文件
        pdf_files = collect_pdf_files()
    
    if not pdf_files:
        print("错误: 没有要处理的 PDF 文件")
        input("按 Enter 退出...")
        sys.exit(1)
    
    asyncio.run(analyze_pdfs(pdf_files))


if __name__ == "__main__":
    main()
