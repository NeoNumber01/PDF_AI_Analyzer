"""
PDF AI Analyzer - Liquid Glass UI
macOS Sonoma 风格毛玻璃界面

设计系统：
- 双主题支持 (深色/浅色)
- 玻璃拟态组件 (GlassCard, GlassButton, GlassInput)
- 8px 网格间距系统
- 三档文字对比度
"""

import asyncio
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import sys
import queue

sys.path.insert(0, str(Path(__file__).parent.parent))
import config

# ═══════════════════════════════════════════════════════════
# 依赖检测
# ═══════════════════════════════════════════════════════════
# CustomTkinter 在某些系统上有透明度兼容性问题，暂时禁用
HAS_CTK = False
# try:
#     import customtkinter as ctk
#     HAS_CTK = True
# except ImportError:
#     HAS_CTK = False

try:
    import pywinstyles
    HAS_BLUR = False  # 暂时禁用
except ImportError:
    HAS_BLUR = False

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = False  # 暂时禁用
except ImportError:
    HAS_DND = False


# ═══════════════════════════════════════════════════════════
# 设计系统 - Design Tokens
# ═══════════════════════════════════════════════════════════

class DesignTokens:
    """Liquid Glass 设计 Token"""
    
    # 间距 (8px Grid)
    SPACING = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 20, "2xl": 24, "3xl": 32}
    
    # 圆角
    RADIUS = {"card": 20, "button": 14, "input": 12, "badge": 8}
    
    # 字体
    FONT_FAMILY = "Segoe UI"
    FONT_MONO = "Consolas"
    FONT_SIZES = {"title": 15, "body": 13, "small": 11, "mono": 10}

    @staticmethod
    def dark():
        """深色主题 Token"""
        return {
            # 背景
            "bg_base": "#0A0A0F",
            "bg_elevated": "#0D0D14",
            "bg_surface": "#12121A",
            
            # 玻璃 (rgba 转换后的近似 HEX)
            "glass_bg": "#15151F",           # rgba(255,255,255,0.06) on #0A0A0F
            "glass_bg_hover": "#1A1A26",     # rgba(255,255,255,0.09)
            "glass_bg_active": "#1F1F2D",    # rgba(255,255,255,0.12)
            
            # 边框
            "border_subtle": "#1A1A24",      # 8%
            "border_default": "#222230",     # 12%
            "border_hover": "#2D2D40",       # 18%
            "border_focus": "#5B9CF6",     # accent 混合后
            
            # 文字
            "text_title": "#EAEAEB",         # 92%
            "text_body": "#C7C7CC",          # 78%
            "text_muted": "#8C8C99",         # 55%
            "text_disabled": "#595966",      # 35%
            
            # 强调色
            "accent": "#3B82F6",
            "accent_hover": "#60A5FA",
            "accent_muted": "#1A2A4A",
            "success": "#10B981",
            "success_hover": "#34D399",
            "danger": "#EF4444",
            "danger_bg": "#2A1515",        # 12%
            "danger_border": "#8B3333",    # 35%
            "danger_hover": "#F87171",
            
            # 分隔线
            "divider": "#1A1A24",            # 8%
            
            # 滚动条
            "scrollbar_thumb": "#333344",
            "scrollbar_thumb_hover": "#444455",
            
            # 阴影 (Tkinter 不支持，用于参考)
            "shadow": "0 8px 24px rgba(0,0,0,0.35)",
        }

    @staticmethod
    def light():
        """浅色主题 Token"""
        return {
            # 背景
            "bg_base": "#F5F5F7",
            "bg_elevated": "#FAFAFA",
            "bg_surface": "#FFFFFF",
            
            # 玻璃
            "glass_bg": "#FFFFFF",
            "glass_bg_hover": "#F8F8FC",
            "glass_bg_active": "#F0F0F5",
            
            # 边框
            "border_subtle": "#E8E8EC",
            "border_default": "#DDDDE3",
            "border_hover": "#CCCCDD",
            "border_focus": "#5B8FEB",
            
            # 文字
            "text_title": "#1A1A1F",         # 85%
            "text_body": "#555560",          # 65%
            "text_muted": "#8888A0",         # 45%
            "text_disabled": "#BBBBCC",
            
            # 强调色
            "accent": "#2563EB",
            "accent_hover": "#3B82F6",
            "accent_muted": "#E8EDF8",
            "success": "#059669",
            "success_hover": "#10B981",
            "danger": "#DC2626",
            "danger_bg": "#FCE8E8",
            "danger_border": "#E8A0A0",
            "danger_hover": "#EF4444",
            
            # 分隔线
            "divider": "#E5E5EA",
            
            # 滚动条
            "scrollbar_thumb": "#CCCCDD",
            "scrollbar_thumb_hover": "#AAAACC",
            
            "shadow": "0 8px 20px rgba(0,0,0,0.10)",
        }


# ═══════════════════════════════════════════════════════════
# 主应用
# ═══════════════════════════════════════════════════════════

class PDFAnalyzerGUI:
    """Liquid Glass 风格 PDF 分析器"""
    
    def __init__(self):
        # 主题状态
        self.is_dark = True
        self.tokens = DesignTokens.dark()
        self.spacing = DesignTokens.SPACING
        self.radius = DesignTokens.RADIUS
        
        # 初始化 CTK (使用 try-except 避免透明度问题)
        global HAS_CTK
        if HAS_CTK:
            try:
                ctk.set_appearance_mode("dark")
                ctk.set_default_color_theme("blue")
            except Exception as e:
                print(f"CustomTkinter 初始化失败: {e}")
                HAS_CTK = False
        
        # 创建窗口
        if HAS_DND:
            self.root = TkinterDnD.Tk()
        elif HAS_CTK:
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()
        
        self.root.title("PDF AI Analyzer")
        self.root.geometry("1000x900")
        self.root.minsize(850, 750)
        self.root.configure(bg=self.tokens["bg_base"])
        
        # 应用毛玻璃
        self._apply_blur()
        
        # 状态
        self.pdf_files = []
        self.is_running = False
        self.bot = None
        self.log_queue = queue.Queue()
        
        # 构建 UI
        self._build_ui()
        self._check_log_queue()
    
    def _apply_blur(self):
        """Windows 毛玻璃效果"""
        if HAS_BLUR and not HAS_DND:  # TkinterDnD 与透明效果冲突
            try:
                pywinstyles.apply_style(self.root, "acrylic")
            except:
                pass
    
    def toggle_theme(self):
        """切换主题"""
        self.is_dark = not self.is_dark
        self.tokens = DesignTokens.dark() if self.is_dark else DesignTokens.light()
        if HAS_CTK:
            ctk.set_appearance_mode("dark" if self.is_dark else "light")
        # 重建 UI 以应用新主题
        for widget in self.root.winfo_children():
            widget.destroy()
        self._build_ui()
    
    # ═══════════════════════════════════════════════════════
    # 组件工厂
    # ═══════════════════════════════════════════════════════
    
    def _glass_card(self, parent, title="", icon=""):
        """创建 GlassCard"""
        outer = tk.Frame(parent, bg=self.tokens["bg_base"])
        
        if HAS_CTK:
            card = ctk.CTkFrame(
                outer,
                corner_radius=self.radius["card"],
                fg_color=self.tokens["glass_bg"],
                border_width=1,
                border_color=self.tokens["border_default"]
            )
        else:
            card = tk.Frame(outer, bg=self.tokens["glass_bg"],
                          highlightthickness=1,
                          highlightbackground=self.tokens["border_default"])
        
        card.pack(fill=tk.BOTH, expand=True)
        
        # Header
        if title:
            header = tk.Frame(card, bg=self.tokens["glass_bg"])
            header.pack(fill=tk.X, padx=self.spacing["xl"], pady=(self.spacing["xl"], self.spacing["lg"]))
            
            if HAS_CTK:
                if icon:
                    icon_lbl = ctk.CTkLabel(header, text=icon, font=ctk.CTkFont(size=16),
                                           text_color=self.tokens["accent"])
                    icon_lbl.pack(side=tk.LEFT, padx=(0, self.spacing["sm"]))
                
                title_lbl = ctk.CTkLabel(
                    header, text=title,
                    font=ctk.CTkFont(family=DesignTokens.FONT_FAMILY, 
                                    size=DesignTokens.FONT_SIZES["title"], weight="bold"),
                    text_color=self.tokens["text_title"]
                )
                title_lbl.pack(side=tk.LEFT)
            else:
                lbl = tk.Label(header, text=f"{icon} {title}" if icon else title,
                              font=(DesignTokens.FONT_FAMILY, DesignTokens.FONT_SIZES["title"], 'bold'),
                              bg=self.tokens["glass_bg"], fg=self.tokens["text_title"])
                lbl.pack(side=tk.LEFT)
            
            # 极淡分隔线
            if HAS_CTK:
                div = ctk.CTkFrame(card, height=1, fg_color=self.tokens["divider"])
                div.pack(fill=tk.X, padx=self.spacing["xl"])
        
        return card, outer
    
    def _glass_button(self, parent, text, command, style="primary", width=None):
        """创建 GlassButton"""
        styles = {
            "primary": {
                "fg": self.tokens["accent"],
                "hover": self.tokens["accent_hover"],
                "text": "#FFFFFF",
                "border": None
            },
            "secondary": {
                "fg": self.tokens["glass_bg"],
                "hover": self.tokens["glass_bg_hover"],
                "text": self.tokens["text_body"],
                "border": self.tokens["border_default"]
            },
            "success": {
                "fg": self.tokens["success"],
                "hover": self.tokens["success_hover"],
                "text": "#FFFFFF",
                "border": None
            },
            "danger": {
                "fg": "transparent",
                "hover": self.tokens["danger_bg"],
                "text": self.tokens["danger"],
                "border": self.tokens["danger_border"]
            }
        }
        s = styles.get(style, styles["primary"])
        
        if HAS_CTK:
            btn = ctk.CTkButton(
                parent,
                text=text,
                command=command,
                font=ctk.CTkFont(family=DesignTokens.FONT_FAMILY, 
                                size=DesignTokens.FONT_SIZES["body"], weight="bold"),
                corner_radius=self.radius["button"],
                height=40,
                width=width or 0,
                fg_color=s["fg"] if s["fg"] != "transparent" else self.tokens["bg_base"],
                hover_color=s["hover"],
                text_color=s["text"],
                border_width=1 if s["border"] else 0,
                border_color=s["border"] or "transparent"
            )
        else:
            btn = tk.Button(parent, text=text, command=command,
                          font=(DesignTokens.FONT_FAMILY, 11, 'bold'),
                          bg=s["fg"] if s["fg"] != "transparent" else self.tokens["bg_base"],
                          fg=s["text"], relief=tk.FLAT, cursor="hand2")
        return btn
    
    def _glass_input(self, parent, textvariable, placeholder="", width=None):
        """创建 GlassInput"""
        if HAS_CTK:
            entry = ctk.CTkEntry(
                parent,
                textvariable=textvariable,
                font=ctk.CTkFont(family=DesignTokens.FONT_FAMILY, size=DesignTokens.FONT_SIZES["body"]),
                height=42,
                corner_radius=self.radius["input"],
                fg_color=self.tokens["bg_base"],
                border_color=self.tokens["border_default"],
                border_width=1,
                text_color=self.tokens["text_body"],
                placeholder_text=placeholder,
                width=width or 0
            )
        else:
            entry = tk.Entry(parent, textvariable=textvariable,
                           font=(DesignTokens.FONT_FAMILY, 12),
                           bg=self.tokens["bg_base"], fg=self.tokens["text_body"],
                           insertbackground=self.tokens["text_body"],
                           highlightthickness=1,
                           highlightbackground=self.tokens["border_default"],
                           highlightcolor=self.tokens["accent"])
        return entry
    
    def _glass_listbox(self, parent, height=8):
        """创建 GlassListbox"""
        listbox = tk.Listbox(
            parent,
            selectmode=tk.SINGLE,
            height=height,
            font=(DesignTokens.FONT_MONO, DesignTokens.FONT_SIZES["body"]),
            bg=self.tokens["bg_base"],
            fg=self.tokens["text_body"],
            selectbackground=self.tokens["accent_muted"],
            selectforeground=self.tokens["text_title"],
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.tokens["border_default"],
            highlightcolor=self.tokens["accent"],
            activestyle="none"
        )
        return listbox
    
    def _glass_text(self, parent, height=8):
        """创建 GlassText (日志)"""
        text = tk.Text(
            parent,
            height=height,
            font=(DesignTokens.FONT_MONO, DesignTokens.FONT_SIZES["mono"]),
            bg=self.tokens["bg_base"],
            fg=self.tokens["text_muted"],
            insertbackground=self.tokens["accent"],
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.tokens["border_default"],
            highlightcolor=self.tokens["accent"],
            state=tk.DISABLED,
            wrap=tk.WORD,
            padx=self.spacing["lg"],
            pady=self.spacing["md"]
        )
        return text
    
    # ═══════════════════════════════════════════════════════
    # 构建 UI
    # ═══════════════════════════════════════════════════════
    
    def _build_ui(self):
        """构建界面"""
        self.root.configure(bg=self.tokens["bg_base"])
        
        # 主容器
        main = tk.Frame(self.root, bg=self.tokens["bg_base"])
        main.pack(fill=tk.BOTH, expand=True, padx=self.spacing["3xl"], pady=self.spacing["2xl"])
        
        # 顶部
        self._build_header(main)
        
        # 内容区 (两列)
        content = tk.Frame(main, bg=self.tokens["bg_base"])
        content.pack(fill=tk.BOTH, expand=True, pady=(self.spacing["xl"], 0))
        
        # 左列
        left = tk.Frame(content, bg=self.tokens["bg_base"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, self.spacing["md"]))
        
        self._build_files_card(left)
        self._build_settings_card(left)
        
        # 右列
        right = tk.Frame(content, bg=self.tokens["bg_base"])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(self.spacing["md"], 0))
        
        self._build_log_card(right)
        self._build_progress_card(right)
        
        # 底部按钮
        self._build_controls(main)
    
    def _build_header(self, parent):
        """标题区"""
        header = tk.Frame(parent, bg=self.tokens["bg_base"])
        header.pack(fill=tk.X, pady=(0, self.spacing["lg"]))
        
        # 左侧标题
        left = tk.Frame(header, bg=self.tokens["bg_base"])
        left.pack(side=tk.LEFT)
        
        if HAS_CTK:
            title = ctk.CTkLabel(
                left, text="PDF AI Analyzer",
                font=ctk.CTkFont(family=DesignTokens.FONT_FAMILY, size=26, weight="bold"),
                text_color=self.tokens["text_title"]
            )
            title.pack(anchor="w")
            
            subtitle = ctk.CTkLabel(
                left, text="使用 ChatGPT 智能分析 PDF 文档",
                font=ctk.CTkFont(family=DesignTokens.FONT_FAMILY, size=13),
                text_color=self.tokens["text_muted"]
            )
            subtitle.pack(anchor="w", pady=(4, 0))
        else:
            title = tk.Label(left, text="PDF AI Analyzer",
                           font=(DesignTokens.FONT_FAMILY, 22, 'bold'),
                           bg=self.tokens["bg_base"], fg=self.tokens["text_title"])
            title.pack(anchor="w")
        
        # 右侧主题切换
        if HAS_CTK:
            theme_btn = ctk.CTkButton(
                header, text="D" if self.is_dark else "L",
                command=self.toggle_theme,
                width=40, height=40,
                corner_radius=self.radius["button"],
                fg_color=self.tokens["glass_bg"],
                hover_color=self.tokens["glass_bg_hover"],
                text_color=self.tokens["text_body"],
                border_width=1,
                border_color=self.tokens["border_default"]
            )
            theme_btn.pack(side=tk.RIGHT)
    
    def _build_files_card(self, parent):
        """文件列表卡片"""
        card, outer = self._glass_card(parent, "文档队列", "")
        outer.pack(fill=tk.BOTH, expand=True, pady=(0, self.spacing["md"]))
        
        # 列表容器
        list_frame = tk.Frame(card, bg=self.tokens["glass_bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, 
                       padx=self.spacing["xl"], pady=(self.spacing["lg"], self.spacing["md"]))
        
        self.file_listbox = self._glass_listbox(list_frame, height=7)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL,
                               command=self.file_listbox.yview,
                               bg=self.tokens["glass_bg"],
                               troughcolor=self.tokens["bg_base"],
                               activebackground=self.tokens["scrollbar_thumb_hover"])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        # 拖拽支持
        if HAS_DND:
            self.file_listbox.drop_target_register(DND_FILES)
            self.file_listbox.dnd_bind('<<Drop>>', self._on_drop)
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._on_drop)
        
        self.drag_data = {"index": None}
        self.file_listbox.bind('<Button-1>', self._on_drag_start)
        self.file_listbox.bind('<B1-Motion>', self._on_drag_motion)
        self.file_listbox.bind('<ButtonRelease-1>', self._on_drag_end)
        
        # 提示
        if HAS_CTK:
            hint = ctk.CTkLabel(
                card, text="拖拽文件到此处添加 · 支持批量处理",
                font=ctk.CTkFont(family=DesignTokens.FONT_FAMILY, size=11),
                text_color=self.tokens["text_muted"]
            )
            hint.pack(pady=(0, self.spacing["md"]))
        
        # 按钮
        btn_frame = tk.Frame(card, bg=self.tokens["glass_bg"])
        btn_frame.pack(fill=tk.X, padx=self.spacing["xl"], pady=(0, self.spacing["xl"]))
        
        for text, cmd, style in [
            ("添加", self.add_files, "secondary"),
            ("移除", self.remove_file, "secondary"),
            ("↑", self.move_up, "secondary"),
            ("↓", self.move_down, "secondary"),
            ("清空", self.clear_files, "danger"),
        ]:
            btn = self._glass_button(btn_frame, text, cmd, style)
            btn.pack(side=tk.LEFT, padx=(0, self.spacing["sm"]))
    
    def _build_settings_card(self, parent):
        """设置卡片"""
        card, outer = self._glass_card(parent, "处理设置", "")
        outer.pack(fill=tk.X)
        
        content = tk.Frame(card, bg=self.tokens["glass_bg"])
        content.pack(fill=tk.X, padx=self.spacing["xl"], pady=(self.spacing["lg"], self.spacing["xl"]))
        
        # 提示词
        if HAS_CTK:
            prompt_lbl = ctk.CTkLabel(content, text="AI 提示词",
                                     font=ctk.CTkFont(size=12),
                                     text_color=self.tokens["text_muted"])
            prompt_lbl.pack(anchor="w", pady=(0, self.spacing["sm"]))
        
        self.prompt_var = tk.StringVar(value=config.PROMPT_TEXT)
        self.prompt_entry = self._glass_input(content, self.prompt_var, "输入发送给 ChatGPT 的指令...")
        self.prompt_entry.pack(fill=tk.X, pady=(0, self.spacing["lg"]))
        
        # 延迟
        delay_frame = tk.Frame(content, bg=self.tokens["glass_bg"])
        delay_frame.pack(fill=tk.X)
        
        if HAS_CTK:
            delay_lbl = ctk.CTkLabel(delay_frame, text="页间延迟 (秒)",
                                    font=ctk.CTkFont(size=12),
                                    text_color=self.tokens["text_muted"])
            delay_lbl.pack(side=tk.LEFT)
        
        self.delay_var = tk.StringVar(value=str(config.DELAY_BETWEEN_PAGES))
        delay_entry = self._glass_input(delay_frame, self.delay_var, width=100)
        delay_entry.pack(side=tk.RIGHT)
    
    def _build_log_card(self, parent):
        """日志卡片"""
        card, outer = self._glass_card(parent, "实时日志", "")
        outer.pack(fill=tk.BOTH, expand=True, pady=(0, self.spacing["md"]))
        
        log_frame = tk.Frame(card, bg=self.tokens["glass_bg"])
        log_frame.pack(fill=tk.BOTH, expand=True, 
                      padx=self.spacing["xl"], pady=(self.spacing["lg"], self.spacing["xl"]))
        
        self.log_text = self._glass_text(log_frame)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll = tk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview,
                            bg=self.tokens["glass_bg"],
                            troughcolor=self.tokens["bg_base"])
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scroll.set)
    
    def _build_progress_card(self, parent):
        """进度卡片"""
        card, outer = self._glass_card(parent, "处理进度", "")
        outer.pack(fill=tk.X)
        
        content = tk.Frame(card, bg=self.tokens["glass_bg"])
        content.pack(fill=tk.X, padx=self.spacing["xl"], pady=(self.spacing["lg"], self.spacing["xl"]))
        
        # 进度头部
        header = tk.Frame(content, bg=self.tokens["glass_bg"])
        header.pack(fill=tk.X, pady=(0, self.spacing["md"]))
        
        if HAS_CTK:
            self.progress_label = ctk.CTkLabel(
                header, text="0%",
                font=ctk.CTkFont(family=DesignTokens.FONT_FAMILY, size=20, weight="bold"),
                text_color=self.tokens["accent"]
            )
            self.progress_label.pack(side=tk.RIGHT)
            
            # 进度条
            self.progress_var = tk.DoubleVar()
            self.progress_bar = ctk.CTkProgressBar(
                content,
                variable=self.progress_var,
                height=6,
                corner_radius=3,
                fg_color=self.tokens["divider"],
                progress_color=self.tokens["accent"]
            )
            self.progress_bar.pack(fill=tk.X)
            self.progress_bar.set(0)
            
            # 状态
            self.status_var = tk.StringVar(value="就绪")
            self.status_label = ctk.CTkLabel(
                content, textvariable=self.status_var,
                font=ctk.CTkFont(size=12),
                text_color=self.tokens["text_muted"]
            )
            self.status_label.pack(pady=(self.spacing["md"], 0))
        else:
            self.progress_label = tk.Label(header, text="0%",
                                         font=(DesignTokens.FONT_FAMILY, 16, 'bold'),
                                         bg=self.tokens["glass_bg"], fg=self.tokens["accent"])
            self.progress_label.pack(side=tk.RIGHT)
            
            self.progress_var = tk.DoubleVar()
            from tkinter import ttk
            self.progress_bar = ttk.Progressbar(content, variable=self.progress_var, maximum=100)
            self.progress_bar.pack(fill=tk.X)
            
            self.status_var = tk.StringVar(value="就绪")
            self.status_label = tk.Label(content, textvariable=self.status_var,
                                        font=(DesignTokens.FONT_FAMILY, 10),
                                        bg=self.tokens["glass_bg"], fg=self.tokens["text_muted"])
            self.status_label.pack(pady=(8, 0))
    
    def _build_controls(self, parent):
        """控制按钮"""
        controls = tk.Frame(parent, bg=self.tokens["bg_base"])
        controls.pack(fill=tk.X, pady=(self.spacing["xl"], 0))
        
        btn_container = tk.Frame(controls, bg=self.tokens["bg_base"])
        btn_container.pack()
        
        self.start_btn = self._glass_button(btn_container, "启动浏览器", 
                                           self.start_browser, "primary", 140)
        self.start_btn.pack(side=tk.LEFT, padx=self.spacing["sm"])
        
        self.ready_btn = self._glass_button(btn_container, "开始处理",
                                           self.start_processing, "success", 120)
        self.ready_btn.pack(side=tk.LEFT, padx=self.spacing["sm"])
        if HAS_CTK:
            self.ready_btn.configure(state="disabled")
        else:
            self.ready_btn.config(state=tk.DISABLED)
        
        self.stop_btn = self._glass_button(btn_container, "停止",
                                          self.stop_processing, "danger", 100)
        self.stop_btn.pack(side=tk.LEFT, padx=self.spacing["sm"])
        if HAS_CTK:
            self.stop_btn.configure(state="disabled")
        else:
            self.stop_btn.config(state=tk.DISABLED)
    
    # ═══════════════════════════════════════════════════════
    # 事件处理
    # ═══════════════════════════════════════════════════════
    
    def _on_drag_start(self, event):
        idx = self.file_listbox.nearest(event.y)
        if 0 <= idx < len(self.pdf_files):
            self.drag_data["index"] = idx
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(idx)
    
    def _on_drag_motion(self, event):
        if self.drag_data["index"] is None:
            return
        target = self.file_listbox.nearest(event.y)
        current = self.drag_data["index"]
        if target != current and 0 <= target < len(self.pdf_files):
            self.pdf_files[current], self.pdf_files[target] = \
                self.pdf_files[target], self.pdf_files[current]
            self.file_listbox.delete(current)
            self.file_listbox.insert(current, Path(self.pdf_files[current]).name)
            self.file_listbox.delete(target)
            self.file_listbox.insert(target, Path(self.pdf_files[target]).name)
            self.drag_data["index"] = target
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(target)
    
    def _on_drag_end(self, event):
        self.drag_data["index"] = None
    
    def _on_drop(self, event):
        files = self._parse_drop(event.data)
        added = 0
        for f in files:
            if f.lower().endswith('.pdf') and f not in self.pdf_files:
                self.pdf_files.append(f)
                self.file_listbox.insert(tk.END, Path(f).name)
                added += 1
        if added:
            self.log(f"✓ 已添加 {added} 个文件")
            self._update_status()
    
    def _parse_drop(self, data):
        import re
        if '{' in data:
            files = re.findall(r'\{([^}]+)\}', data)
            remaining = re.sub(r'\{[^}]+\}', '', data).strip()
            if remaining:
                files.extend(remaining.split())
            return [f.strip() for f in files if f.strip()]
        return [f.strip() for f in data.split() if f.strip()]
    
    def log(self, msg):
        self.log_queue.put(msg)
    
    def _check_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.root.after(100, self._check_log_queue)
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="选择 PDF",
            filetypes=[("PDF", "*.pdf"), ("All", "*.*")]
        )
        added = 0
        for f in files:
            if f not in self.pdf_files:
                self.pdf_files.append(f)
                self.file_listbox.insert(tk.END, Path(f).name)
                added += 1
        if added:
            self.log(f"已添加 {added} 个文件")
        self._update_status()
    
    def remove_file(self):
        sel = self.file_listbox.curselection()
        if sel:
            idx = sel[0]
            name = Path(self.pdf_files.pop(idx)).name
            self.file_listbox.delete(idx)
            self.log(f"已移除 {name}")
        self._update_status()
    
    def move_up(self):
        sel = self.file_listbox.curselection()
        if sel and sel[0] > 0:
            idx = sel[0]
            self.pdf_files[idx], self.pdf_files[idx-1] = self.pdf_files[idx-1], self.pdf_files[idx]
            text = self.file_listbox.get(idx)
            self.file_listbox.delete(idx)
            self.file_listbox.insert(idx-1, text)
            self.file_listbox.selection_set(idx-1)
    
    def move_down(self):
        sel = self.file_listbox.curselection()
        if sel and sel[0] < len(self.pdf_files) - 1:
            idx = sel[0]
            self.pdf_files[idx], self.pdf_files[idx+1] = self.pdf_files[idx+1], self.pdf_files[idx]
            text = self.file_listbox.get(idx)
            self.file_listbox.delete(idx)
            self.file_listbox.insert(idx+1, text)
            self.file_listbox.selection_set(idx+1)
    
    def clear_files(self):
        self.pdf_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.log("已清空")
        self._update_status()
    
    def _update_status(self):
        count = len(self.pdf_files)
        self.status_var.set(f"已添加 {count} 个文件" if count else "就绪")
    
    def _update_progress(self, value):
        if HAS_CTK:
            self.progress_bar.set(value / 100)
            self.progress_label.configure(text=f"{value:.0f}%")
        else:
            self.progress_var.set(value)
            self.progress_label.config(text=f"{value:.0f}%")
    
    def start_browser(self):
        if not self.pdf_files:
            messagebox.showwarning("提示", "请先添加 PDF 文件")
            return
        if HAS_CTK:
            self.start_btn.configure(state="disabled")
        else:
            self.start_btn.config(state=tk.DISABLED)
        self.status_var.set("启动中...")
        self.log("正在启动浏览器...")
        threading.Thread(target=self._start_browser_thread, daemon=True).start()
    
    def _start_browser_thread(self):
        try:
            from src.chatgpt_automation import ChatGPTAutomation
            async def start():
                self.bot = ChatGPTAutomation()
                await self.bot.start_browser()
            asyncio.run(start())
            self.root.after(0, self._browser_started)
        except Exception as e:
            self.log(f"[ERROR] {e}")
            if HAS_CTK:
                self.root.after(0, lambda: self.start_btn.configure(state="normal"))
    
    def _browser_started(self):
        self.log("浏览器已启动")
        self.log("   请登录 ChatGPT 并选择模型")
        self.log("   然后点击「开始处理」")
        self.status_var.set("请登录后开始处理")
        if HAS_CTK:
            self.ready_btn.configure(state="normal")
        else:
            self.ready_btn.config(state=tk.NORMAL)
    
    def start_processing(self):
        if HAS_CTK:
            self.ready_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        else:
            self.ready_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        self.is_running = True
        prompt = self.prompt_var.get()
        try:
            delay = float(self.delay_var.get())
        except:
            delay = config.DELAY_BETWEEN_PAGES
        self.log("\n▶ 开始处理")
        self.status_var.set("处理中...")
        threading.Thread(target=self._process_thread, args=(prompt, delay), daemon=True).start()
    
    def _process_thread(self, prompt, delay):
        async def process():
            total = len(self.pdf_files)
            for i, pdf in enumerate(self.pdf_files, 1):
                if not self.is_running:
                    break
                name = Path(pdf).name
                self.log(f"\n[{i}/{total}] {name}")
                try:
                    from src.pdf_converter import convert_pdf_to_images
                    images = convert_pdf_to_images(pdf)
                except Exception as e:
                    self.log(f"[ERROR] {e}")
                    continue
                pages = len(images)
                for j, img in enumerate(images, 1):
                    if not self.is_running:
                        break
                    self.log(f"  • 第 {j}/{pages} 页")
                    progress = ((i-1)/total + j/pages/total) * 100
                    self.root.after(0, lambda p=progress: self._update_progress(p))
                    try:
                        await self.bot.upload_image_and_send(img, prompt)
                        await self.bot.wait_for_response_complete()
                        self.log("    [OK]")
                        if j < pages:
                            await asyncio.sleep(delay)
                    except Exception as e:
                        self.log(f"    [ERROR] {e}")
                if i < total and self.is_running:
                    await asyncio.sleep(5)
            self.log("\n=== 完成 ===")
            self.root.after(0, self._done)
        asyncio.run(process())
    
    def _done(self):
        if HAS_CTK:
            self.stop_btn.configure(state="disabled")
            self.start_btn.configure(state="normal")
            self.ready_btn.configure(state="disabled")
        else:
            self.stop_btn.config(state=tk.DISABLED)
            self.start_btn.config(state=tk.NORMAL)
            self.ready_btn.config(state=tk.DISABLED)
        self._update_progress(100)
        self.status_var.set("完成")
        self.is_running = False
        messagebox.showinfo("完成", "所有 PDF 处理完成！")
    
    def stop_processing(self):
        self.is_running = False
        self.log("\n正在停止...")
        self.status_var.set("停止中...")
    
    def run(self):
        self.root.mainloop()
    
    def on_closing(self):
        if self.is_running:
            if not messagebox.askyesno("确认", "正在处理，确定退出？"):
                return
        if self.bot:
            try:
                asyncio.run(self.bot.close())
            except:
                pass
        self.root.destroy()


def main():
    app = PDFAnalyzerGUI()
    app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.run()


if __name__ == "__main__":
    main()
