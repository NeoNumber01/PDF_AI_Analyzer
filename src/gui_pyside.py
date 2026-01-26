"""
PDF AI Analyzer - PySide6 Liquid Glass UI v3 Reference
Glassmorphism 极致精修版 - No Log Window

Design: Deep Space Background + High-End Glass + Noise Texture
"""

import sys
import asyncio
import threading
import random
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QFrame, QGraphicsDropShadowEffect, QFileDialog, QMessageBox, QSizePolicy,
    QComboBox
)
from PySide6.QtCore import Qt, QSize, Signal, QPoint, QTimer, QRectF, QMimeData, QUrl
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QLinearGradient, QRadialGradient,
    QFont, QPainterPath, QPixmap, QDrag
)

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


# ═══════════════════════════════════════════════════════════
# Design Tokens v3 - Deep Space Glass
# ═══════════════════════════════════════════════════════════

@dataclass
class Tokens:
    """Extreme Glassmorphism Design Tokens"""
    
    # 背景 (Deep Nebula)
    bg_start: str = "#0D0D18"        # 深空黑蓝
    bg_mid: str = "#1A1A2E"          # 中层深蓝
    bg_end: str = "#16213E"          # 底部由深转亮
    
    # 光斑 (更梦幻)
    blob_1: tuple = (70, 50, 255, 30)    # Electric Blue
    blob_2: tuple = (180, 40, 255, 25)   # Neon Purple
    blob_3: tuple = (0, 230, 255, 20)    # Cyan
    blob_4: tuple = (255, 60, 120, 18)   # Magenta
    
    # 玻璃材质
    glass_fill_top: tuple = (255, 255, 255, 14)
    glass_fill_bottom: tuple = (255, 255, 255, 5)
    
    border_top: tuple = (255, 255, 255, 50)
    border_bottom: tuple = (0, 0, 0, 60)
    
    # 阴影
    shadow_color: tuple = (0, 0, 0, 90)
    shadow_blur: int = 35
    shadow_offset: int = 12
    
    # 控件属性
    radius_card: int = 24
    radius_button: int = 16
    radius_input: int = 12
    
    # 间距
    space_s: int = 8
    space_m: int = 16
    space_l: int = 24
    space_xl: int = 32
    
    # text
    text_primary: str = "#FFFFFF"
    text_secondary: str = "rgba(255, 255, 255, 0.85)"
    text_tertiary: str = "#94A3B8"  # 明亮的蓝灰色 (Tailwind Slate 400)，确保禁用状态清晰可见
    
    accent: str = "#3B82F6"
    accent_glow: tuple = (59, 130, 246, 60)
    
    danger: str = "#EF4444"
    danger_glow: tuple = (239, 68, 68, 40)
    
    success: str = "#10B981"
    
    divider: str = "rgba(255, 255, 255, 0.08)"
    
    # 滚动条
    scrollbar_thumb: str = "rgba(255, 255, 255, 0.15)"


T = Tokens()


def rgba(r, g, b, a): return QColor(r, g, b, a)
def hex_c(h): return QColor(h)


# ═══════════════════════════════════════════════════════════
# Advanced Background
# ═══════════════════════════════════════════════════════════

class LiquidBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._noise_pixmap = None
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        w, h = rect.width(), rect.height()
        
        bg_grad = QLinearGradient(0, 0, w, h)
        bg_grad.setColorAt(0, hex_c(T.bg_start))
        bg_grad.setColorAt(0.6, hex_c(T.bg_mid))
        bg_grad.setColorAt(1, hex_c(T.bg_end))
        painter.fillRect(rect, bg_grad)
        
        self._draw_blob(painter, w*0.8, h*0.2, w*0.6, T.blob_1)
        self._draw_blob(painter, w*0.2, h*0.7, w*0.5, T.blob_2)
        self._draw_blob(painter, w*0.5, h*0.5, w*0.4, T.blob_3)
        self._draw_blob(painter, w*0.9, h*0.9, w*0.3, T.blob_4)
        
        if not self._noise_pixmap or self._noise_pixmap.size() != rect.size():
            self._generate_noise(w, h)
        painter.drawPixmap(0, 0, self._noise_pixmap)
        
    def _draw_blob(self, painter, cx, cy, radius, color):
        r, g, b, a = color
        grad = QRadialGradient(cx, cy, radius)
        grad.setColorAt(0, rgba(r,g,b,a))
        grad.setColorAt(1, rgba(r,g,b,0))
        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(int(cx), int(cy)), int(radius), int(radius))

    def _generate_noise(self, w, h):
        img = QPixmap(w, h)
        img.fill(Qt.transparent)
        p = QPainter(img)
        p.setPen(rgba(255, 255, 255, 4))
        for _ in range(int(w * h * 0.05)): 
            x = random.randint(0, w)
            y = random.randint(0, h)
            p.drawPoint(x, y)
        p.end()
        self._noise_pixmap = img


# ═══════════════════════════════════════════════════════════
# High-End Glass Card
# ═══════════════════════════════════════════════════════════

class GlassCard(QFrame):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(T.shadow_blur)
        shadow.setOffset(0, T.shadow_offset)
        shadow.setColor(rgba(*T.shadow_color))
        self.setGraphicsEffect(shadow)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(T.space_l, T.space_l, T.space_l, T.space_l)
        self.main_layout.setSpacing(T.space_m)
        
        if title:
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: {T.text_secondary};
                    font-size: 13px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                    text-transform: uppercase;
                    background: transparent;
                }}
            """)
            self.main_layout.addWidget(self.title_label)
        
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(T.space_m)
        self.main_layout.addWidget(self.content)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), T.radius_card, T.radius_card)
        
        # Fill
        fill_grad = QLinearGradient(0, 0, rect.width(), rect.height())
        fill_grad.setColorAt(0, rgba(*T.glass_fill_top))
        fill_grad.setColorAt(1, rgba(*T.glass_fill_bottom))
        painter.fillPath(path, fill_grad)
        
        # Top Border
        grad_top = QLinearGradient(0, 0, rect.width(), 0)
        grad_top.setColorAt(0, rgba(255,255,255,0))
        grad_top.setColorAt(0.5, rgba(*T.border_top))
        grad_top.setColorAt(1, rgba(255,255,255,0))
        p_top = QPen(QBrush(grad_top), 1)
        
        # Full Border
        painter.setPen(QPen(rgba(255,255,255,15), 1))
        painter.drawPath(path)
        
        # Overlay Top Highlight
        painter.setPen(p_top)
        painter.drawPath(path)

    def addWidget(self, widget):
        self.content_layout.addWidget(widget)
        
    def addLayout(self, layout):
        self.content_layout.addLayout(layout)


# ═══════════════════════════════════════════════════════════
# Status Bar
# ═══════════════════════════════════════════════════════════

class StatusBar(GlassCard):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedHeight(60)
        
        container = QHBoxLayout()
        container.setContentsMargins(0, 0, 0, 0)
        
        self.icon_label = QLabel("ℹ️")
        self.icon_label.setStyleSheet("font-size: 16px; background: transparent;")
        container.addWidget(self.icon_label)
        
        self.msg_label = QLabel("就绪")
        self.msg_label.setStyleSheet(f"""
            color: {T.text_primary};
            font-size: 14px;
            font-family: 'Segoe UI';
            background: transparent;
        """)
        container.addWidget(self.msg_label)
        container.addStretch()
        
        self.addLayout(container)
        
    def show_message(self, msg: str, type: str = "info"):
        icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}
        colors = {"info": T.text_primary, "success": T.success, "error": T.danger, "warning": "#FBBF24"}
        
        self.icon_label.setText(icons.get(type, "ℹ️"))
        self.msg_label.setStyleSheet(f"color: {colors.get(type, T.text_primary)}; background: transparent; font-size: 14px;")
        self.msg_label.setText(msg)


# ═══════════════════════════════════════════════════════════
# Buttons & Widgets
# ═══════════════════════════════════════════════════════════

class GlassButton(QPushButton):
    def __init__(self, text, style="primary", parent=None):
        super().__init__(text, parent)
        self.style_type = style
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self._hover = False
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), T.radius_button, T.radius_button)
        
        color = hex_c(T.accent) if self.style_type == "primary" else rgba(255,255,255,10)
        if self.style_type == "danger": color = hex_c(T.danger)
        
        if self._hover:
            p.setPen(QPen(rgba(255,255,255,100), 2))
            glow_col = T.accent_glow if self.style_type == "primary" else (255,255,255,20)
            if self.style_type == "danger": glow_col = T.danger_glow
            glow_path = QPainterPath()
            glow_path.addRoundedRect(QRectF(rect).adjusted(1,1,-1,-1), T.radius_button, T.radius_button)
            p.fillPath(glow_path, rgba(*glow_col))
        else:
            p.setPen(Qt.NoPen)
            
        if not self.isEnabled():
            color = rgba(60, 60, 80, 80)  # 更明显的灰色背景
            p.setPen(QPen(rgba(100, 100, 120, 100), 1))  # 添加边框表示禁用
            
        p.fillPath(path, color)
        if not self.isEnabled():
            p.drawPath(path)  # 绘制禁用边框
        
        p.setPen(hex_c(T.text_primary) if self.isEnabled() else hex_c(T.text_tertiary))
        p.setFont(QFont("Segoe UI", 10, QFont.Bold))
        p.drawText(rect, Qt.AlignCenter, self.text())
        
    def enterEvent(self, e):
        self._hover = True
        self.update()
    def leaveEvent(self, e):
        self._hover = False
        self.update()

class IconButton(GlassButton):
    def __init__(self, icon, tip="", parent=None):
        super().__init__(icon, "secondary", parent)
        self.setFixedSize(36, 36)
        self.setToolTip(tip)

class GlassInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(44)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: {T.radius_input}px;
                color: {T.text_primary};
                padding: 0 {T.space_m}px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {T.accent};
                background: rgba(0, 0, 0, 0.3);
            }}
        """)

class GlassProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.setFixedHeight(8)
        
    def setValue(self, v):
        self.value = v
        self.update()
        
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        
        track = QPainterPath()
        track.addRoundedRect(QRectF(rect), 4, 4)
        p.fillPath(track, rgba(255,255,255,20))
        
        if self.value > 0:
            pw = rect.width() * self.value / 100
            fill = QPainterPath()
            fill.addRoundedRect(QRectF(0, 0, pw, rect.height()), 4, 4)
            grad = QLinearGradient(0,0,pw,0)
            grad.setColorAt(0, hex_c(T.accent))
            grad.setColorAt(1, QColor("#60A5FA"))
            p.fillPath(fill, grad)

class DraggableListWidget(QListWidget):
    filesDropped = Signal(list)
    orderChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setDragDropOverwriteMode(False)
        self.setSpacing(2)
        
        self.setStyleSheet(f"""
            QListWidget {{
                background: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: {T.radius_input}px;
                color: {T.text_secondary};
                outline: none;
                padding: {T.space_s}px;
            }}
            QListWidget::item {{
                height: 42px;
                border-radius: 8px;
                color: transparent; /* Text drawn by widget */
            }}
            QListWidget::item:selected {{
                background: {T.accent}22;
                border: 1px solid {T.accent}44;
            }}
            QListWidget::item:hover:!selected {{
                background: rgba(255,255,255,0.05);
            }}
        """)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
        else: super().dragEnterEvent(e)
        
    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            files = [u.toLocalFile() for u in e.mimeData().urls() if u.toLocalFile().endswith('.pdf')]
            if files: self.filesDropped.emit(files)
            e.acceptProposedAction()
        else:
            super().dropEvent(e)
            self.orderChanged.emit()

class FileItemWidget(QWidget):
    def __init__(self, text, path, on_delete, parent=None):
        super().__init__(parent)
        self.path = path
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 5, 0)
        layout.setSpacing(5)
        
        self.label = QLabel(text)
        self.label.setStyleSheet(f"color: {T.text_primary}; background: transparent; border: none; font-size: 13px;")
        layout.addWidget(self.label, 1)
        
        # Tiny X button
        self.btn_del = QPushButton("×")
        self.btn_del.setFixedSize(24, 24)
        self.btn_del.setCursor(Qt.PointingHandCursor)
        self.btn_del.clicked.connect(lambda: on_delete(path))
        self.btn_del.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                color: {T.text_tertiary};
                font-weight: bold;
                padding-bottom: 2px;
            }}
            QPushButton:hover {{
                background: rgba(239, 68, 68, 0.2);
                border-color: {T.danger};
                color: {T.danger};
            }}
        """)
        layout.addWidget(self.btn_del)


# ═══════════════════════════════════════════════════════════
# Main Window - Layout v3
# ═══════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    # 自定义信号用于跨线程 GUI 更新
    sig_log = Signal(str, str)          # message, level
    sig_enable_start = Signal(bool)     # enabled
    sig_enable_browser = Signal(bool)   # enabled
    sig_enable_stop = Signal(bool)      # enabled
    sig_progress = Signal(int, str)     # value, text
    sig_reset_ui = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF AI Analyzer")
        self.resize(1200, 800)
        self.pdf_files = []
        self.is_running = False
        self.bot = None
        # 断点续传：记录当前处理进度
        self.current_pdf_index = 0  # 当前处理的 PDF 索引
        self.current_page_index = 0  # 当前处理的页面索引
        self.processed_images = {}  # {pdf_path: [已处理的图片路径列表]}
        
        # 创建持久的事件循环 (在单独线程中运行)
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self._loop_thread.start()
        
        # 先创建 UI (按钮等)
        self.ui()
        
        # UI 创建后再连接信号
        self.sig_log.connect(self._do_log)
        self.sig_enable_start.connect(lambda e: self.btn_start.setEnabled(e))
        self.sig_enable_browser.connect(lambda e: self.btn_browser.setEnabled(e))
        self.sig_enable_stop.connect(lambda e: self.btn_stop.setEnabled(e))
        self.sig_progress.connect(self._upd_prog)
        self.sig_reset_ui.connect(self._reset_ui)
    
    def _do_log(self, msg, level):
        """接收信号并更新状态栏"""
        self.status.show_message(msg, level)
        print(f"[{level.upper()}] {msg}")
    
    def _run_loop(self):
        """在后台线程中运行事件循环"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
    
    def _run_async(self, coro):
        """在持久事件循环中运行协程"""
        return asyncio.run_coroutine_threadsafe(coro, self._loop)
        
    def ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        self.bg = LiquidBackground(central)
        self.bg.setGeometry(0, 0, 2000, 2000)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self._topbar(main_layout)
        
        # 内容区域
        content = QHBoxLayout()
        content.setContentsMargins(T.space_l, T.space_l, T.space_l, T.space_l)
        content.setSpacing(T.space_l)
        
        self._sidebar(content)
        self._workspace(content)
        
        main_layout.addLayout(content)
        
    def _topbar(self, layout):
        bar = QWidget()
        bar.setFixedHeight(64)
        bar.setStyleSheet(f"border-bottom: 1px solid {T.divider}; background: rgba(0,0,0,0.2);")
        
        l = QHBoxLayout(bar)
        l.setContentsMargins(T.space_xl, 0, T.space_xl, 0)
        
        title = QLabel("PDF AI Analyzer")
        title.setStyleSheet(f"color: {T.text_primary}; font-size: 18px; font-weight: bold; background: transparent;")
        l.addWidget(title)
        l.addStretch()
        
        # 平台选择下拉框
        platform_label = QLabel("AI 平台:")
        platform_label.setStyleSheet(f"color: {T.text_secondary}; font-size: 13px; background: transparent; margin-right: 8px;")
        l.addWidget(platform_label)
        
        self.platform_combo = QComboBox()
        self.platform_combo.setFixedSize(140, 36)
        self.platform_combo.setStyleSheet(f"""
            QComboBox {{
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                color: {T.text_primary};
                padding: 0 12px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                border: 1px solid {T.accent};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {T.text_secondary};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background: #1a1a2e;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: {T.text_primary};
                selection-background-color: {T.accent};
            }}
        """)
        # 添加平台选项
        from src.platform_factory import get_platform_names
        for pid, name in get_platform_names().items():
            self.platform_combo.addItem(name, pid)
        l.addWidget(self.platform_combo)
        
        l.addSpacing(16)
        
        self.btn_browser = GlassButton("启动浏览器", "primary")
        self.btn_browser.clicked.connect(self._start_browser)
        
        self.btn_start = GlassButton("开始处理", "primary")
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self._start_processing)
        
        self.btn_stop = GlassButton("停止", "danger")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop)
        
        for b in [self.btn_browser, self.btn_start, self.btn_stop]:
            b.setFixedWidth(120)
            l.addWidget(b)
            
        layout.addWidget(bar)
        
    def _sidebar(self, layout):
        card = GlassCard("文档队列")
        card.setMinimumWidth(320)
        
        self.file_list = DraggableListWidget()
        self.file_list.filesDropped.connect(self._on_drop)
        self.file_list.orderChanged.connect(self._on_reorder)
        card.addWidget(self.file_list)
        
        # Tools
        tools = QHBoxLayout()
        for i, tip, func in [
            ("+", "添加", self._add),
            ("↑", "上移", self._up), ("↓", "下移", self._down), ("×", "清空", self._clear)
        ]:
            b = IconButton(i, tip)
            b.clicked.connect(func)
            tools.addWidget(b)
        card.addLayout(tools)
        
        # 55% 占比
        layout.addWidget(card, 55)
        
    def _workspace(self, layout):
        space = QVBoxLayout()
        space.setSpacing(T.space_l)
        
        progress_card = GlassCard("处理进度")
        progress_h = QHBoxLayout()
        self.p_bar = GlassProgressBar()
        progress_h.addWidget(self.p_bar, 1)
        self.p_lbl = QLabel("0%")
        self.p_lbl.setStyleSheet(f"color: {T.accent}; font-weight: bold; font-size: 18px; margin-left: 10px; background: transparent;")
        progress_h.addWidget(self.p_lbl)
        progress_card.addLayout(progress_h)
        self.p_status = QLabel("等待开始...")
        self.p_status.setStyleSheet(f"color: {T.text_tertiary}; font-size: 13px; margin-top: 5px; background: transparent;")
        progress_card.addWidget(self.p_status)
        space.addWidget(progress_card)
        
        settings_card = GlassCard("处理设置")
        form = QVBoxLayout()
        form.setSpacing(T.space_m)
        l1 = QLabel("AI 提示词")
        l1.setStyleSheet(f"color: {T.text_secondary}; background: transparent;")
        form.addWidget(l1)
        self.in_prompt = GlassInput("输入自定义 Prompt...")
        self.in_prompt.setText(config.PROMPT_TEXT)
        form.addWidget(self.in_prompt)
        l2 = QLabel("页间延迟 (秒)")
        l2.setStyleSheet(f"color: {T.text_secondary}; background: transparent;")
        form.addWidget(l2)
        self.in_delay = GlassInput()
        self.in_delay.setText(str(config.DELAY_BETWEEN_PAGES))
        self.in_delay.setFixedWidth(100)
        form.addWidget(self.in_delay)
        settings_card.addLayout(form)
        space.addWidget(settings_card)
        
        self.status = StatusBar()
        space.addWidget(self.status)
        
        space.addStretch()
        
        # 45% 占比
        layout.addLayout(space, 45)

    # Logic
    def _log(self, msg, type="info"):
        self.status.show_message(msg, type)
        print(f"[{type.upper()}] {msg}")

    def _add(self):
        fs, _ = QFileDialog.getOpenFileNames(self, "PDF", "", "*.pdf")
        self._on_drop(fs)
        
    def _render_list(self):
        """完全重建列表 (为了保证 ItemWidget 正确显示)"""
        self.file_list.clear() # Clears widgets too
        for path in self.pdf_files:
            item = QListWidgetItem()
            # 存储 path 到 user role
            item.setData(Qt.UserRole, path)
            self.file_list.addItem(item)
            
            # 创建 Custom Widget
            wid = FileItemWidget(Path(path).name, path, self._remove_item)
            item.setSizeHint(wid.sizeHint())
            self.file_list.setItemWidget(item, wid)
            
    def _remove_item(self, path):
        if path in self.pdf_files:
            idx = self.pdf_files.index(path)
            self.pdf_files.pop(idx)
            self._render_list()
            self._log(f"已移除 {Path(path).name}")

    def _on_drop(self, files):
        new_cnt = 0
        for f in files:
            if f not in self.pdf_files:
                self.pdf_files.append(f)
                new_cnt += 1
        if new_cnt:
            self._render_list()
            self._log(f"添加了 {new_cnt} 个文件")
            
    # Reorder logic needs to check actual item widgets or internal model if using standard drag
    # Problem: QListWidget internal drag drop might lose ItemWidget or re-instantiate items.
    # Safest way: Update pdf_files order based on new QListWidget order (from UserRole), then re-render widgets.
    def _on_reorder(self):
        new_list = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            path = item.data(Qt.UserRole)
            if path:
                new_list.append(path)
        
        # Update model
        self.pdf_files = new_list
        # Re-render to ensure widgets are alive and correct
        self._render_list()
        
    def _up(self): self._move(-1)
    def _down(self): self._move(1)
    def _move(self, d):
        r = self.file_list.currentRow()
        nr = r + d
        if 0 <= nr < len(self.pdf_files):
            self.pdf_files[r], self.pdf_files[nr] = self.pdf_files[nr], self.pdf_files[r]
            # Since we use _render_list, selection might be lost. 
            self._render_list()
            self.file_list.setCurrentRow(nr)
            
    def _clear(self):
        self.pdf_files = []
        self._render_list()
        
    def _start_browser(self):
        self.btn_browser.setEnabled(False)
        self.platform_combo.setEnabled(False)  # 禁用平台切换
        
        # 获取选中的平台
        platform_id = self.platform_combo.currentData()
        platform_name = self.platform_combo.currentText()
        
        self._log(f"正在启动 {platform_name} 浏览器...", "info")
        print(f"[DEBUG] _start_browser called for platform: {platform_id}")
        
        async def start():
            print("[DEBUG] start() coroutine running")
            try:
                from src.platform_factory import get_automation
                self.bot = get_automation(platform_id)
                print(f"[DEBUG] {platform_name} Automation created, calling start_browser...")
                await self.bot.start_browser()
                print("[DEBUG] start_browser completed, emitting signals...")
                
                # 注册浏览器关闭事件监听器
                def on_browser_close():
                    print("[DEBUG] Browser closed by user")
                    self.bot = None
                    # 检查是否有进度可以保留
                    has_progress = self.current_pdf_index > 0 or self.current_page_index > 0
                    if has_progress:
                        self.sig_log.emit(f"浏览器已关闭 - 进度已保留 (PDF {self.current_pdf_index + 1}, 页 {self.current_page_index + 1})", "warning")
                    else:
                        self.sig_log.emit("浏览器已关闭", "warning")
                    self.sig_enable_browser.emit(True)
                    self.sig_enable_start.emit(False)
                    self.sig_enable_stop.emit(False)  # 禁用停止按钮
                    self.is_running = False  # 确保标记为非运行状态
                    # 不调用 sig_reset_ui，保留进度！只更新状态文字
                    # 重新启用平台选择 (需在主线程)
                    from PySide6.QtCore import QMetaObject, Qt as QtCoreQt, Q_ARG
                    QMetaObject.invokeMethod(self.platform_combo, "setEnabled", QtCoreQt.QueuedConnection, Q_ARG(bool, True))
                
                # 监听 context 关闭事件
                if self.bot.context:
                    self.bot.context.on("close", on_browser_close)
                
                # 使用信号进行跨线程 GUI 更新
                self.sig_log.emit(f"{platform_name} 就绪 - 请登录", "success")
                self.sig_enable_start.emit(True)
                print("[DEBUG] signals emitted")
            except Exception as e:
                import traceback
                print(f"[DEBUG] Exception in start(): {e}")
                print(traceback.format_exc())
                self.sig_log.emit(f"启动失败: {e}", "error")
                self.sig_enable_browser.emit(True)
                # 重新启用平台选择
                self.platform_combo.setEnabled(True)
        
        future = self._run_async(start())
        def on_done(fut):
            try:
                fut.result()
                print("[DEBUG] start() future completed successfully")
            except Exception as e:
                print(f"[DEBUG] start() future failed: {e}")
        future.add_done_callback(on_done)
        
    def _start_processing(self):
        print("[DEBUG] _start_processing called")  # 调试日志
        
        if not self.pdf_files:
            self._log("请先添加 PDF 文件", "warning")
            return
            
        if self.bot is None:
            self._log("请先启动浏览器", "warning")
            return
        
        self.is_running = True
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        
        # 检查是否是续传（有进度记录）
        is_resume = self.current_pdf_index > 0 or self.current_page_index > 0
        if is_resume:
            self._log(f"继续处理 (从 PDF {self.current_pdf_index + 1}, 页 {self.current_page_index + 1})...", "info")
        else:
            self.p_bar.setValue(0)
            self.p_lbl.setText("0%")
            self.p_status.setText("准备中...")
            self._log("开始处理...")
        
        prompt = self.in_prompt.text()
        try: delay = float(self.in_delay.text())
        except: delay = 3.0
        
        # 保存起始位置
        start_pdf = self.current_pdf_index
        start_page = self.current_page_index
        
        async def process():
            try:
                total = len(self.pdf_files)
                print(f"[DEBUG] 开始处理，共 {total} 个 PDF 文件")
                print(f"[DEBUG] pdf_files = {self.pdf_files}")
                print(f"[DEBUG] start_pdf={start_pdf}, start_page={start_page}")
                
                if total == 0:
                    self.sig_log.emit("没有 PDF 文件需要处理", "warning")
                    self.sig_reset_ui.emit()
                    return
                
                for i, pdf in enumerate(self.pdf_files):
                    # 跳过已处理的 PDF
                    if i < start_pdf:
                        continue
                    
                    if not self.is_running:
                        # 保存当前进度
                        self.current_pdf_index = i
                        break
                    
                    name = Path(pdf).name
                    self.sig_log.emit(f"正在处理: {name} ({i+1}/{total})", "info")
                    
                    # 转换 PDF
                    try:
                        from src.pdf_converter import convert_pdf_to_images
                        images = convert_pdf_to_images(pdf)
                        if not images:
                            raise ValueError("未提取到图片")
                    except Exception as e:
                        self.sig_log.emit(f"转换失败: {e}", "error")
                        continue
                    
                    # 确定起始页
                    page_start = start_page if i == start_pdf else 0
                    
                    # 发送处理
                    for j, img in enumerate(images):
                        # 跳过已处理的页面
                        if j < page_start:
                            continue
                        
                        if not self.is_running:
                            # 保存当前进度
                            self.current_pdf_index = i
                            self.current_page_index = j
                            break
                        
                        pct = int((i/total + (j+1)/len(images)/total) * 100)
                        self.sig_progress.emit(pct, f"{name} - p.{j+1}/{len(images)}")
                        
                        try:
                            await self.bot.upload_image_and_send(img, prompt)
                            await self.bot.wait_for_response_complete()
                            # 记录已处理
                            self.current_pdf_index = i
                            self.current_page_index = j + 1
                        except Exception as e:
                            self.sig_log.emit(f"发送失败: {e}", "error")
                        
                        if j < len(images) - 1: 
                            await asyncio.sleep(delay)
                    
                    # 完成一个 PDF 后重置页面索引
                    if self.is_running:
                        self.current_page_index = 0
                        self.current_pdf_index = i + 1
                
                if self.is_running:
                    # 全部完成，重置进度
                    self.current_pdf_index = 0
                    self.current_page_index = 0
                    self.sig_progress.emit(100, "完成")
                    self.sig_log.emit("全部完成", "success")
                self.sig_reset_ui.emit()
                
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                self.sig_log.emit(f"处理异常: {e}", "error")
                self.sig_reset_ui.emit()
        
        self._run_async(process())
        
    def _upd_prog(self, val, txt):
        self.p_bar.setValue(val)
        self.p_lbl.setText(f"{val}%")
        self.p_status.setText(txt)
        
    def _stop(self):
        self.is_running = False
        self._log(f"已暂停 (PDF {self.current_pdf_index + 1}, 页 {self.current_page_index + 1})", "warning")
        self._reset_ui(keep_progress=True)
    
    def _clear_progress(self):
        """清除进度，下次从头开始"""
        self.current_pdf_index = 0
        self.current_page_index = 0
        self.p_bar.setValue(0)
        self.p_lbl.setText("0%")
        self.p_status.setText("就绪")
        self._log("进度已清除", "info")
        
    def _reset_ui(self, keep_progress=False):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.is_running = False
        if not keep_progress:
            # 任务完成时重置进度条
            self.p_bar.setValue(0)
            self.p_lbl.setText("0%")
            self.p_status.setText("就绪")
        else:
            # 暂停时保留进度显示
            self.p_status.setText("已暂停 - 点击开始继续")
        
    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.bg.resize(self.size())
        self.bg._noise_pixmap = None

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__": main()
