"""
国际化 (i18n) 模块
支持中英文切换
"""

# 当前语言
_current_language = "zh"

# 翻译字典
translations = {
    "zh": {
        # 窗口标题
        "app_title": "PDF AI 分析器",
        "page_preview_title": "页面预览",
        
        # 主界面按钮
        "btn_add_pdf": "添加 PDF",
        "btn_preview": "预览页面",
        "btn_launch_browser": "启动浏览器",
        "btn_start": "开始处理",
        "btn_stop": "停止",
        "btn_clear": "清空",
        "btn_move_up": "上移",
        "btn_move_down": "下移",
        "btn_add": "添加",
        "btn_reorder": "重排",
        "btn_close": "关闭",
        
        # 卡片标题
        "card_doc_queue": "文档队列",
        "card_pdf_files": "PDF 文件",
        "card_settings": "处理设置",
        "card_progress": "处理进度",
        
        # 设置标签
        "label_prompt": "AI 提示词",
        "label_delay": "页间延迟 (秒)",
        "label_platform": "AI 平台:",
        
        # 页面预览
        "btn_select_all": "全选",
        "btn_deselect_all": "取消全选",
        "btn_create_group": "创建分组",
        "btn_clear_groups": "清除分组",
        "total_pages": "共 {} 页",
        "tip_ctrl_click": "💡 Ctrl+点击多选后创建分组",
        "page_n": "第 {} 页",
        
        # 分组管理
        "group_manager": "分组管理",
        "group_n": "分组 {}",
        "group_pages": "({} 页)",
        "empty_group_hint": "将选中的页面创建分组，分组内的页面会一起发送给 AI",
        
        # 分组设置
        "group_settings": "分组设置：",
        "pages_per_batch_prefix": "每",
        "pages_per_batch_suffix": "页为一组发送给 AI",
        "will_split_to": "将分为 {} 组",
        "no_pages": "无页面",
        
        # 状态消息
        "msg_ready": "就绪",
        "msg_processing": "处理中...",
        "msg_complete": "完成",
        "msg_stopped": "已停止",
        "msg_paused": "已暂停 - 点击开始继续",
        "msg_error": "错误",
        "msg_add_pdf_first": "请先添加 PDF 文件",
        "msg_launch_browser_first": "请先启动浏览器",
        "msg_no_enabled_pages": "没有启用的页面需要处理",
        "msg_cleaning_cache": "正在清理缓存...",
        "msg_cache_cleaned": "缓存清理完成",
        "msg_batch_processing": "开始批量处理 ({} 批)...",
        "msg_resume_processing": "继续处理 (从批次 {}/{})...",
        "msg_batch_progress": "批次 {}/{} ({}页)",
        "msg_page_progress": "页面 {}/{}",
        "msg_all_complete": "全部完成",
        "msg_empty_response_retry": "检测到空白输出，{}秒后重试...",
        "msg_retry": "重试 {}/{}: 批次 {}",
        "msg_send_failed": "发送失败: {}",
        "msg_retry_failed": "重试 {} 次后仍失败，跳过此批次",
        "msg_enabled_pages": "已启用 {}/{} 页",
        "msg_selected_pages": "已选中 {} 页",
        "msg_groups_count": "共 {} 个分组",
        "msg_from_cache": "从缓存加载 {} 页",
        "msg_splitting_pdf": "正在切分 PDF 页面...",
        "msg_split_complete": "已切分 {} 页",
        "msg_select_pages_first": "请先选择要分组的页面",
        "msg_group_created": "已创建分组: 页 {}",
        "msg_select_pdf": "请选择要预览的 PDF 文件",
        "msg_progress_cleared": "进度已清除",
        "msg_removed": "已移除 {}",
        "msg_added_files": "添加了 {} 个文件",
        "msg_launching_browser": "正在启动 {} 浏览器...",
        "msg_browser_closed_progress": "浏览器已关闭 - 进度已保留 (PDF {}, 页 {})",
        "msg_browser_closed": "浏览器已关闭",
        "msg_platform_ready": "{} 就绪 - 请登录",
        "msg_launch_failed": "启动失败: {}",
        "msg_preparing": "准备中...",
        "msg_starting": "开始处理...",
        "msg_resume_legacy": "继续处理 (从 PDF {}, 页 {})...",
        "msg_no_pdf_files": "没有 PDF 文件需要处理",
        "msg_processing_pdf": "正在处理: {} ({}/{})",
        "msg_no_images": "未提取到图片",
        "msg_convert_failed": "转换失败: {}",
        "msg_retry_page": "重试 {}/{}: {} 第 {} 页",
        "msg_retry_page_failed": "重试 {} 次后仍失败，跳过此页",
        "msg_wait_retry": "等待 {} 秒后重试...",
        "msg_processing_error": "处理异常: {}",
        "msg_preview_failed": "预览失败: {}",
        "mode_single": "单页",
        "mode_fixed": "固定N页",
        "mode_custom": "自定义分组",
        "msg_group_mode": "分组模式: {}",
        "msg_pages_per_batch": "每次输入 {} 页",
        "msg_paused": "已暂停 (PDF {}, 页 {})",
        
        # 批次顺序排序
        "batch_order_title": "输入顺序",
        "batch_order_hint": "拖拽或使用按钮调整分组和页面的输入顺序，列表从上到下即为 AI 处理顺序",
        "batch_group": "分组 ({} 页): 页 {}",
        "batch_page": "页 {}",
        "btn_to_top": "移到顶部",
        "btn_to_bottom": "移到底部",
        "btn_reset": "重置顺序",
        "btn_confirm": "确定",
        "btn_cancel": "取消",
        "btn_batch_order": "输入顺序",
        
        # 新建聊天设置
        "label_new_chat_settings": "💬 聊天窗口设置",
        "label_new_chat_per_pdf": "每个PDF新建聊天",
        "label_new_chat_per_pages": "每N页新建聊天",
        "label_pages_suffix": "页",
        "msg_creating_new_chat": "正在创建新聊天窗口...",
        "msg_new_chat_created": "新聊天窗口已创建",
        "msg_new_chat_failed": "创建新聊天窗口失败: {}",
        
        # 语言
        "language": "语言",
    },
    
    "en": {
        # Window titles
        "app_title": "PDF AI Analyzer",
        "page_preview_title": "Page Preview",
        
        # Main buttons
        "btn_add_pdf": "Add PDF",
        "btn_preview": "Preview",
        "btn_launch_browser": "Launch Browser",
        "btn_start": "Start",
        "btn_stop": "Stop",
        "btn_clear": "Clear",
        "btn_move_up": "Up",
        "btn_move_down": "Down",
        "btn_add": "Add",
        "btn_reorder": "Reorder",
        "btn_close": "Close",
        
        # Card titles
        "card_doc_queue": "Documents",
        "card_pdf_files": "PDF Files",
        "card_settings": "Settings",
        "card_progress": "Progress",
        
        # Settings labels
        "label_prompt": "AI Prompt",
        "label_delay": "Delay (sec)",
        "label_platform": "Platform:",
        
        # Page preview
        "btn_select_all": "Select All",
        "btn_deselect_all": "Deselect",
        "btn_create_group": "Group",
        "btn_clear_groups": "Clear",
        "total_pages": "{} pages",
        "tip_ctrl_click": "💡 Ctrl+Click to multi-select",
        "page_n": "Page {}",
        
        # Group manager
        "group_manager": "Groups",
        "group_n": "Group {}",
        "group_pages": "({} pages)",
        "empty_group_hint": "Create groups from selected pages. Pages in a group will be sent to AI together.",
        
        # Group settings
        "group_settings": "Settings:",
        "pages_per_batch_prefix": "Send",
        "pages_per_batch_suffix": "pages per batch",
        "will_split_to": "{} groups",
        "no_pages": "No pages",
        
        # Status messages
        "msg_ready": "Ready",
        "msg_processing": "Processing...",
        "msg_complete": "Complete",
        "msg_stopped": "Stopped",
        "msg_paused": "Paused - Click Start to continue",
        "msg_error": "Error",
        "msg_add_pdf_first": "Please add PDF files first",
        "msg_launch_browser_first": "Please launch browser first",
        "msg_no_enabled_pages": "No enabled pages to process",
        "msg_cleaning_cache": "Cleaning cache...",
        "msg_cache_cleaned": "Cache cleaned",
        "msg_batch_processing": "Starting batch processing ({} batches)...",
        "msg_resume_processing": "Resuming from batch {}/{}...",
        "msg_batch_progress": "Batch {}/{} ({} pages)",
        "msg_page_progress": "Page {}/{}",
        "msg_all_complete": "All complete",
        "msg_empty_response_retry": "Empty response, retrying in {}s...",
        "msg_retry": "Retry {}/{}: Batch {}",
        "msg_send_failed": "Send failed: {}",
        "msg_retry_failed": "Failed after {} retries, skipping",
        "msg_enabled_pages": "Enabled {}/{} pages",
        "msg_selected_pages": "Selected {} pages",
        "msg_groups_count": "{} groups",
        "msg_from_cache": "Loaded {} pages from cache",
        "msg_splitting_pdf": "Splitting PDF pages...",
        "msg_split_complete": "Split {} pages",
        "msg_select_pages_first": "Please select pages first",
        "msg_group_created": "Created group: pages {}",
        "msg_select_pdf": "Please select a PDF file",
        "msg_progress_cleared": "Progress cleared",
        "msg_removed": "Removed {}",
        "msg_added_files": "Added {} files",
        "msg_launching_browser": "Launching {} browser...",
        "msg_browser_closed_progress": "Browser closed - Progress saved (PDF {}, page {})",
        "msg_browser_closed": "Browser closed",
        "msg_platform_ready": "{} ready - Please login",
        "msg_launch_failed": "Launch failed: {}",
        "msg_preparing": "Preparing...",
        "msg_starting": "Starting...",
        "msg_resume_legacy": "Resuming (from PDF {}, page {})...",
        "msg_no_pdf_files": "No PDF files to process",
        "msg_processing_pdf": "Processing: {} ({}/{})",
        "msg_no_images": "No images extracted",
        "msg_convert_failed": "Convert failed: {}",
        "msg_retry_page": "Retry {}/{}: {} page {}",
        "msg_retry_page_failed": "Failed after {} retries, skipping page",
        "msg_wait_retry": "Waiting {} seconds before retry...",
        "msg_processing_error": "Processing error: {}",
        "msg_preview_failed": "Preview failed: {}",
        "mode_single": "Single page",
        "mode_fixed": "Fixed N pages",
        "mode_custom": "Custom groups",
        "msg_group_mode": "Group mode: {}",
        "msg_pages_per_batch": "Input {} pages at a time",
        "msg_paused": "Paused (PDF {}, page {})",
        
        # Batch order
        "batch_order_title": "Input Order",
        "batch_order_hint": "Drag or use buttons to adjust the input order of groups and pages. Top to bottom is the AI processing order.",
        "batch_group": "Group ({} pages): pages {}",
        "batch_page": "Page {}",
        "btn_to_top": "To Top",
        "btn_to_bottom": "To Bottom",
        "btn_reset": "Reset Order",
        "btn_confirm": "Confirm",
        "btn_cancel": "Cancel",
        "btn_batch_order": "Input Order",
        
        # New chat settings
        "label_new_chat_settings": "💬 Chat Window Settings",
        "label_new_chat_per_pdf": "New chat per PDF",
        "label_new_chat_per_pages": "New chat every N pages",
        "label_pages_suffix": "pages",
        "msg_creating_new_chat": "Creating new chat window...",
        "msg_new_chat_created": "New chat window created",
        "msg_new_chat_failed": "Failed to create new chat: {}",
        
        # Language
        "language": "Language",
    }
}


def tr(key: str, *args) -> str:
    """
    获取翻译文本
    
    Args:
        key: 翻译键
        *args: 格式化参数
    
    Returns:
        翻译后的文本
    """
    text = translations.get(_current_language, translations["zh"]).get(key, key)
    if args:
        try:
            return text.format(*args)
        except:
            return text
    return text


def set_language(lang: str):
    """设置当前语言"""
    global _current_language
    if lang in translations:
        _current_language = lang


def get_language() -> str:
    """获取当前语言"""
    return _current_language


def toggle_language() -> str:
    """切换语言，返回新语言"""
    global _current_language
    _current_language = "en" if _current_language == "zh" else "zh"
    return _current_language


def get_available_languages() -> list:
    """获取可用语言列表"""
    return list(translations.keys())
