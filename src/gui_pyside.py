"""
PDF AI Analyzer - PySide6 Liquid Glass UI v3 Reference
Glassmorphism 极致精修版 - No Log Window

Design: Deep Space Background + High-End Glass + Noise Texture
"""

import sys
import os
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
    QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QPoint, QTimer, QRectF, QMimeData, QUrl
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QLinearGradient, QRadialGradient,
    QFont, QPainterPath, QPixmap, QDrag
)

sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from src.page_preview import PagePreviewPanel, PageGroupManager, PagePreviewDialog
from src.i18n import tr, set_language, get_language, toggle_language


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
        
        self.msg_label = QLabel(tr("msg_ready"))
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
    sig_process_next_pdf = Signal(int)  # next_pdf_idx - 处理下一个 PDF
    
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
        
        # 页面预览相关
        self.all_page_images = []     # 所有 PDF 切分后的图片路径
        self.page_enabled = []         # 每页是否启用
        self.page_groups = []          # 自定义分组 [[0,1,2], [3,4], ...]
        self.group_mode = "single"     # "single" | "fixed" | "custom"
        self.pages_per_batch = 1       # 固定模式下每批页数
        self.current_batch_index = 0   # 当前处理的批次索引
        
        # PDF 文件状态缓存 - 保存每个文件的处理状态
        # {pdf_path: {'images': [...], 'enabled': [...], 'groups': [...], 'mode': str, 'pages_per_batch': int}}
        self.pdf_cache = {}
        
        # 新建聊天设置
        self.new_chat_per_pdf = False      # 每PDF新建聊天 (默认关闭)
        self.new_chat_per_pages = False    # 每N页新建聊天 (默认关闭)
        self.new_chat_pages_threshold = 30  # 每N页阈值 (默认30页)
        self.pages_since_last_new_chat = 0  # 上次新建聊天后处理的页数
        
        # 自动暂停设置
        self.auto_pause_on_limit = False   # 检测到上限时自动暂停 (默认关闭)
        self.pause_duration_minutes = 30   # 暂停时长 (分钟), 0 表示无限暂停
        self._limit_pause_timer = None     # 自动恢复定时器
        self._limit_pause_remaining = 0    # 剩余暂停秒数
        
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
        self.sig_process_next_pdf.connect(self._do_process_next_pdf)
    
    def _do_log(self, msg, level):
        """接收信号并更新状态栏"""
        self.status.show_message(msg, level)
        print(f"[{level.upper()}] {msg}")
    
    def _do_process_next_pdf(self, next_pdf_idx):
        """处理下一个 PDF（在主线程中执行）"""
        print(f"[DEBUG] _do_process_next_pdf 被调用: idx={next_pdf_idx}")
        
        if not self.is_running:
            self._reset_ui()
            return
            
        if next_pdf_idx < 0 or next_pdf_idx >= len(self.pdf_files):
            self._reset_ui()
            return
            
        print(f"[DEBUG] 切换到 PDF {next_pdf_idx + 1}")
        self.file_list.setCurrentRow(next_pdf_idx)
        # 清除当前的 all_page_images
        self.all_page_images = []
        self.custom_batch_order = None
        self.page_enabled = []
        self.page_groups = []
        
        # 设置自动处理标志
        self._auto_process_next_pdf = True
        # 预览下一个 PDF（加载完成后会自动开始处理）
        self._preview_pages()
    
    def _run_loop(self):
        """在后台线程中运行事件循环"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
    
    def _run_async(self, coro):
        """在持久事件循环中运行协程"""
        return asyncio.run_coroutine_threadsafe(coro, self._loop)
    
    def closeEvent(self, event):
        """关闭应用时清理缓存和临时文件"""
        print("[DEBUG] 正在清理缓存...")
        
        # 停止暂停定时器（如果存在）
        if hasattr(self, '_limit_pause_timer') and self._limit_pause_timer is not None:
            self._limit_pause_timer.stop()
            self._limit_pause_timer = None
        
        # 清理缓存中的图片文件
        for pdf_path, cache in self.pdf_cache.items():
            if 'images' in cache:
                for img_path in cache['images']:
                    try:
                        if os.path.exists(img_path):
                            os.remove(img_path)
                    except Exception as e:
                        print(f"[WARNING] 无法删除缓存图片 {img_path}: {e}")
        
        # 清空缓存字典
        self.pdf_cache.clear()
        self.all_page_images.clear()
        self.page_enabled.clear()
        self.page_groups.clear()
        
        # 清理临时目录
        if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                print(f"[DEBUG] 已清理临时目录: {self.temp_dir}")
            except Exception as e:
                print(f"[WARNING] 无法删除临时目录: {e}")
        
        # 停止事件循环
        if hasattr(self, '_loop') and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        
        print("[DEBUG] 缓存清理完成")
        super().closeEvent(event)
        
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
        self.lbl_platform = QLabel(tr("label_platform"))
        platform_label = self.lbl_platform
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
        
        # 语言切换按钮
        self.btn_lang = QPushButton("🌐 EN")
        self.btn_lang.setFixedSize(70, 36)
        self.btn_lang.setCursor(Qt.PointingHandCursor)
        self.btn_lang.setStyleSheet(f"""
            QPushButton {{
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                color: {T.text_secondary};
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.1);
                color: {T.text_primary};
                border: 1px solid {T.accent};
            }}
        """)
        self.btn_lang.clicked.connect(self._toggle_language)
        l.addWidget(self.btn_lang)
        
        l.addSpacing(8)
        
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
        self.card_doc_queue = GlassCard(tr("card_doc_queue"))
        card = self.card_doc_queue
        card.setMinimumWidth(320)
        
        self.file_list = DraggableListWidget()
        self.file_list.filesDropped.connect(self._on_drop)
        self.file_list.orderChanged.connect(self._on_reorder)
        card.addWidget(self.file_list)
        
        # Tools
        tools = QHBoxLayout()
        for i, tip, func in [
            ("+", tr("btn_add"), self._add),
            ("↑", tr("btn_move_up"), self._up), ("↓", tr("btn_move_down"), self._down), ("×", tr("btn_clear"), self._clear)
        ]:
            b = IconButton(i, tip)
            b.clicked.connect(func)
            tools.addWidget(b)
        
        # 预览按钮
        self.btn_preview = GlassButton(tr("btn_preview"), "secondary")
        self.btn_preview.setFixedWidth(90)
        self.btn_preview.clicked.connect(self._preview_pages)
        tools.addWidget(self.btn_preview)
        
        card.addLayout(tools)
        
        # 50% 占比（原来是35%，现在去掉嵌入式预览区域后增加）
        layout.addWidget(card, 50)
        
        # 创建页面预览弹窗（但不显示）
        self._init_preview_dialog()

    def _init_preview_dialog(self):
        """初始化页面预览弹窗"""
        self.preview_dialog = PagePreviewDialog(self)
        self.preview_dialog.page_toggled.connect(self._on_page_toggled)
        self.preview_dialog.group_mode_changed.connect(self._on_group_mode_changed)
        self.preview_dialog.pages_per_batch_changed.connect(self._on_pages_per_batch_changed)
        self.preview_dialog.groups_changed.connect(self._on_groups_changed)
        self.preview_dialog.batch_order_changed.connect(self._on_batch_order_changed)
        
        # 弹窗关闭时保存状态
        self.preview_dialog.closing.connect(self._save_current_pdf_state)
        
        # 为了兼容性，保留这些属性的引用
        self.page_preview = self.preview_dialog.page_preview
        self.group_manager = self.preview_dialog.group_manager
        
    def _on_page_toggled(self, index: int, enabled: bool):
        """页面启用/禁用"""
        if 0 <= index < len(self.page_enabled):
            self.page_enabled[index] = enabled
            enabled_count = sum(self.page_enabled)
            self._log(tr("msg_enabled_pages", enabled_count, len(self.page_enabled)))
            
    def _on_selection_changed(self, indices: list):
        """选中项改变"""
        if indices:
            self._log(tr("msg_selected_pages", len(indices)), "info")
            
    def _on_group_mode_changed(self, mode: str):
        """分组模式改变"""
        self.group_mode = mode
        mode_names = {"single": tr("mode_single"), "fixed": tr("mode_fixed"), "custom": tr("mode_custom")}
        self._log(tr("msg_group_mode", mode_names.get(mode, mode)))
        
    def _on_pages_per_batch_changed(self, value: int):
        """固定页数改变"""
        self.pages_per_batch = value
        self._log(tr("msg_pages_per_batch", value))
        
    def _on_groups_changed(self, groups: list):
        """分组列表改变"""
        self.page_groups = groups
        self._log(tr("msg_groups_count", len(groups)))
        
    def _on_batch_order_changed(self, batch_order: list):
        """批次顺序改变"""
        self.custom_batch_order = batch_order
        print(f"[DEBUG] _on_batch_order_changed: 收到信号，batch_order = {len(batch_order)} 批次")
        print(f"[DEBUG] _on_batch_order_changed: self.custom_batch_order 已更新")
        
    def _create_group_from_selection(self):
        """从当前选中创建分组"""
        selected = self.page_preview.get_selected_indices()
        if not selected:
            self._log(tr("msg_select_pages_first"), "warning")
            return
        self.group_manager.add_group(selected)
        self._log(tr("msg_group_created", ', '.join([str(i+1) for i in selected])), "success")
        
    def _preview_pages(self):
        """预览当前 PDF 的所有页面"""
        if not self.pdf_files:
            self._log(tr("msg_add_pdf_first"), "warning")
            return
        
        # 重要：在切换到新PDF前，先保存当前PDF的状态
        # 这确保每个PDF的分组和顺序是独立的
        if hasattr(self, '_current_preview_pdf') and self._current_preview_pdf:
            self._save_current_pdf_state()
            print(f"[DEBUG] _preview_pages: 已保存 {self._current_preview_pdf} 的状态")
        
        # 获取当前选中的 PDF
        current_row = self.file_list.currentRow()
        if current_row < 0:
            current_row = 0
        current_pdf = self.pdf_files[current_row] if current_row < len(self.pdf_files) else None
        
        if not current_pdf:
            self._log("请选择要预览的 PDF 文件", "warning")
            return
        
        # 检查缓存中是否已有该 PDF 的切图结果
        if current_pdf in self.pdf_cache:
            cache = self.pdf_cache[current_pdf]
            self.all_page_images = cache['images']
            self.page_enabled = cache['enabled']
            self.page_groups = cache.get('groups', [])
            self.custom_batch_order = cache.get('batch_order', None)  # 恢复批次顺序
            self._current_preview_pdf = current_pdf  # 更新当前预览的 PDF
            self._log(tr("msg_from_cache", len(self.all_page_images)), "success")
            self._load_preview_from_cache()
            return
            
        self._log(tr("msg_splitting_pdf"), "info")
        self._current_preview_pdf = current_pdf  # 保存当前预览的 PDF
        
        # 在后台线程中转换 PDF
        async def convert():
            try:
                from src.pdf_converter import convert_pdf_to_images
                images = convert_pdf_to_images(current_pdf)
                        
                self.all_page_images = images if images else []
                self.page_enabled = [True] * len(self.all_page_images)
                self.page_groups = []
                self.custom_batch_order = None  # 新 PDF 没有自定义顺序
                
                # 保存到缓存
                self.pdf_cache[current_pdf] = {
                    'images': self.all_page_images.copy(),
                    'enabled': self.page_enabled.copy(),
                    'groups': [],
                    'batch_order': None
                }
                
                # 在主线程更新 UI
                from PySide6.QtCore import QMetaObject, Qt as QtCoreQt
                QMetaObject.invokeMethod(
                    self, "_load_preview_images", 
                    QtCoreQt.QueuedConnection
                )
                
            except Exception as e:
                self.sig_log.emit(tr("msg_preview_failed", str(e)), "error")
                
        self._run_async(convert())
    
    from PySide6.QtCore import Slot
    
    @Slot()
    def _load_preview_images(self):
        """加载预览图片到弹窗并显示（主线程）"""
        self.preview_dialog.load_pages(self.all_page_images)
        self.page_groups = []
        self.custom_batch_order = None  # 清除自定义顺序
        self.preview_dialog.custom_batch_order = None  # 同步清除弹窗中的顺序
        self._log(f"已加载 {len(self.all_page_images)} 页", "success")
        
        # 检查是否需要自动处理下一个 PDF
        if getattr(self, '_auto_process_next_pdf', False):
            self._auto_process_next_pdf = False
            self._is_auto_next_pdf = True  # 标记为自动处理下一个PDF，不是续传
            print(f"[DEBUG] _load_preview_images: 自动开始处理下一个 PDF")
            print(f"[DEBUG] 当前 PDF: {self._current_preview_pdf}")
            print(f"[DEBUG] all_page_images 数量: {len(self.all_page_images)}")
            print(f"[DEBUG] page_enabled 数量: {len(self.page_enabled)}, 启用: {sum(self.page_enabled)}")
            # 延迟一下再开始处理
            from PySide6.QtCore import QTimer
            QTimer.singleShot(500, self._start_processing)
            return
        
        # 显示预览弹窗
        self.preview_dialog.show()
        self.preview_dialog.raise_()
        self.preview_dialog.activateWindow()
        
    def _load_preview_from_cache(self):
        """从缓存加载预览（恢复之前的状态）"""
        # 保存当前预览的 PDF 路径
        current_row = self.file_list.currentRow()
        if current_row >= 0 and current_row < len(self.pdf_files):
            self._current_preview_pdf = self.pdf_files[current_row]
        
        print(f"[DEBUG] _load_preview_from_cache: 加载 {self._current_preview_pdf}")
        print(f"[DEBUG] _load_preview_from_cache: page_groups = {self.page_groups}")
        
        # 重要：先完全清空所有组件的状态，避免跨PDF状态污染
        # 清空 PagePreviewPanel 的分组状态
        self.preview_dialog.page_preview.custom_groups.clear()
        self.preview_dialog.page_preview.next_group_id = 0
        self.preview_dialog.page_preview.selected_indices.clear()
        
        # 清空 GroupManagerPanel 的分组状态
        self.preview_dialog.group_manager_panel.groups.clear()
        self.preview_dialog.group_manager_panel.next_group_id = 0
        
        # 清空自定义批次顺序
        self.preview_dialog.custom_batch_order = None
        
        # 加载页面缩略图
        self.preview_dialog.page_preview.load_pages(self.all_page_images)
        
        # 设置 GroupManagerPanel 的页面数据
        pages_dict = {i: path for i, path in enumerate(self.all_page_images)}
        self.preview_dialog.group_manager_panel.set_pages(pages_dict)
        
        # 恢复页面启用状态
        for i, enabled in enumerate(self.page_enabled):
            if i < len(self.preview_dialog.page_preview.thumbnails):
                self.preview_dialog.page_preview.thumbnails[i].set_checked(enabled)
        
        # 恢复分组状态
        print(f"[DEBUG] 恢复分组: {len(self.page_groups)} 个分组")
        
        # 清空并重建 PagePreviewPanel 的分组
        self.preview_dialog.page_preview.custom_groups.clear()
        self.preview_dialog.page_preview.next_group_id = 0
        
        # 清空并重建 GroupManagerPanel 的分组
        self.preview_dialog.group_manager_panel.groups.clear()
        self.preview_dialog.group_manager_panel.next_group_id = 0
        
        if self.page_groups:
            for group in self.page_groups:
                # 添加到 PagePreviewPanel
                group_id = self.preview_dialog.page_preview.next_group_id
                self.preview_dialog.page_preview.next_group_id += 1
                self.preview_dialog.page_preview.custom_groups.append(group.copy())
                
                # 设置缩略图的分组标记
                for idx in group:
                    thumb = self.preview_dialog.page_preview._get_thumbnail_by_index(idx)
                    if thumb:
                        thumb.set_group(group_id)
                
                # 添加到 GroupManagerPanel
                if len(group) >= 2:
                    self.preview_dialog.group_manager_panel.add_group(group)
        
        # 刷新显示
        self.preview_dialog.group_manager_panel._refresh_cards()
        self.preview_dialog.group_manager.update_preview(len(self.all_page_images))
        
        print(f"[DEBUG] GroupManagerPanel 分组数: {len(self.preview_dialog.group_manager_panel.groups)}")
        
        # 恢复批次顺序
        if hasattr(self, 'custom_batch_order') and self.custom_batch_order:
            self.preview_dialog.custom_batch_order = self.custom_batch_order
            print(f"[DEBUG] 恢复批次顺序: {len(self.custom_batch_order)} 批次")
        else:
            self.preview_dialog.custom_batch_order = None
        
        # 检查是否需要自动处理下一个 PDF（从缓存加载的情况）
        if getattr(self, '_auto_process_next_pdf', False):
            self._auto_process_next_pdf = False
            self._is_auto_next_pdf = True  # 标记为自动处理模式，防止 _start_processing 进入循环
            print(f"[DEBUG] _load_preview_from_cache: 自动开始处理下一个 PDF")
            print(f"[DEBUG] 当前 PDF: {self._current_preview_pdf}")
            print(f"[DEBUG] all_page_images 数量: {len(self.all_page_images)}")
            print(f"[DEBUG] page_enabled 数量: {len(self.page_enabled)}, 启用: {sum(self.page_enabled)}")
            print(f"[DEBUG] custom_batch_order: {self.custom_batch_order is not None}")
            # 延迟一下再开始处理
            from PySide6.QtCore import QTimer
            QTimer.singleShot(500, self._start_processing)
            return
        
        # 显示预览弹窗
        self.preview_dialog.show()
        self.preview_dialog.raise_()
        self.preview_dialog.activateWindow()
        
    def _save_current_pdf_state(self):
        """保存当前 PDF 的处理状态到缓存"""
        if not hasattr(self, '_current_preview_pdf') or not self._current_preview_pdf:
            print("[DEBUG] _save_current_pdf_state: 没有当前预览的PDF")
            return
            
        pdf_path = self._current_preview_pdf
        print(f"[DEBUG] _save_current_pdf_state: 保存 {pdf_path}")
        
        # 获取页面启用状态
        enabled = []
        for thumb in self.preview_dialog.page_preview.thumbnails:
            enabled.append(thumb.is_checked())
        
        # 获取分组状态 - 从 GroupManagerPanel 获取（因为删除等操作在这里）
        groups = self.preview_dialog.group_manager_panel.get_groups_list()
        print(f"[DEBUG] 保存分组状态: {len(groups)} 个分组")
        
        # 同步更新 page_groups
        self.page_groups = [g.copy() for g in groups]
        
        # 获取自定义批次顺序 - 优先使用 MainWindow 的值，因为信号更新的是这个
        batch_order = getattr(self, 'custom_batch_order', None)
        if batch_order is None:
            batch_order = getattr(self.preview_dialog, 'custom_batch_order', None)
        
        print(f"[DEBUG] _save_current_pdf_state: batch_order = {batch_order is not None}, length = {len(batch_order) if batch_order else 0}")
        
        # 更新或创建缓存
        if pdf_path not in self.pdf_cache:
            self.pdf_cache[pdf_path] = {
                'images': self.all_page_images.copy(),
                'enabled': enabled,
                'groups': [g.copy() for g in groups],
                'batch_order': batch_order
            }
        else:
            self.pdf_cache[pdf_path]['enabled'] = enabled
            self.pdf_cache[pdf_path]['groups'] = [g.copy() for g in groups]
            self.pdf_cache[pdf_path]['batch_order'] = batch_order
        
        print(f"[DEBUG] 缓存已更新，groups: {len(self.pdf_cache[pdf_path]['groups'])}, batch_order saved: {self.pdf_cache[pdf_path]['batch_order'] is not None}")
        
    def _get_page_batches(self) -> list:
        """
        根据当前设置生成页面批次
        
        Returns:
            list of lists: [[img1, img2], [img3], ...] 每个子列表是一批要一起发送的图片
        """
        # 获取启用的页面索引
        # 重要：在批量自动处理模式下，preview_dialog 的状态可能还没有同步到新 PDF
        # 因此优先使用 MainWindow 自身的 page_enabled 和 page_groups（这些在 _preview_pages 中已正确设置）
        is_auto_mode = getattr(self, '_is_auto_next_pdf', False) or getattr(self, '_auto_process_next_pdf', False)
        
        if is_auto_mode:
            # 自动批量处理模式：使用 MainWindow 的数据（已在 _preview_pages 或 _load_preview_from_cache 中设置）
            page_enabled = self.page_enabled
            page_groups = self.page_groups
            print(f"[DEBUG] _get_page_batches: 自动批量模式，使用 MainWindow 数据")
        elif hasattr(self, 'preview_dialog') and self.preview_dialog:
            # 手动模式：从预览弹窗获取实时数据
            page_enabled = self.preview_dialog.page_preview.get_page_enabled_list()
            page_groups = self.preview_dialog.group_manager_panel.get_groups_list()
            print(f"[DEBUG] _get_page_batches: 从预览弹窗获取实时数据")
        else:
            page_enabled = self.page_enabled
            page_groups = self.page_groups
            print(f"[DEBUG] _get_page_batches: 使用缓存数据")
        
        enabled_indices = [i for i, enabled in enumerate(page_enabled) if enabled]
        print(f"[DEBUG] _get_page_batches: enabled_indices = {enabled_indices}")
        
        if not enabled_indices:
            return []
            
        batches = []
        
        # 优先使用自定义批次顺序
        print(f"[DEBUG] _get_page_batches: custom_batch_order = {getattr(self, 'custom_batch_order', None) is not None}")
        print(f"[DEBUG] _get_page_batches: page_groups = {page_groups}")
        
        if hasattr(self, 'custom_batch_order') and self.custom_batch_order:
            # 使用用户自定义的排序
            print(f"[DEBUG] _get_page_batches: 使用自定义顺序，共 {len(self.custom_batch_order)} 批次")
            print(f"[DEBUG] custom_batch_order 内容: {self.custom_batch_order}")
            for i, batch_info in enumerate(self.custom_batch_order):
                pages = batch_info.get("pages", [])
                valid_indices = [idx for idx in pages if idx in enabled_indices]
                if valid_indices:
                    batch = [self.all_page_images[idx] for idx in valid_indices]
                    batches.append(batch)
                    print(f"[DEBUG] 批次 {i+1}: 页面 {valid_indices}, 共 {len(batch)} 张图片")
            print(f"[DEBUG] _get_page_batches: 生成 {len(batches)} 批次")
            return batches
        
        # 检查是否有自定义分组 - 如果有分组则使用分组模式
        if page_groups and len(page_groups) > 0:
            # 自定义分组模式 - 按页码顺序发送
            # 构建批次列表，每个批次记录 (最小页码, 批次内容)
            batch_with_order = []
            used_indices = set()
            
            # 处理分组
            for group in page_groups:
                valid_indices = [idx for idx in group if idx in enabled_indices]
                if valid_indices:
                    min_page = min(valid_indices)  # 分组按最小页码排序
                    batch = [self.all_page_images[idx] for idx in valid_indices]
                    batch_with_order.append((min_page, batch))
                    used_indices.update(valid_indices)
            
            # 处理未分组的页面
            for idx in enabled_indices:
                if idx not in used_indices:
                    batch_with_order.append((idx, [self.all_page_images[idx]]))
            
            # 按页码顺序排序
            batch_with_order.sort(key=lambda x: x[0])
            batches = [batch for _, batch in batch_with_order]
            
        elif self.group_mode == "fixed" and self.pages_per_batch > 1:
            # 固定N页模式
            n = self.pages_per_batch
            for i in range(0, len(enabled_indices), n):
                batch_indices = enabled_indices[i:i+n]
                batch = [self.all_page_images[idx] for idx in batch_indices]
                batches.append(batch)
                
        else:
            # 单页模式：每页单独发送
            for idx in enabled_indices:
                batches.append([self.all_page_images[idx]])
                
        return batches
        
    def _workspace(self, layout):

        space = QVBoxLayout()
        space.setSpacing(T.space_l)
        
        self.progress_card = GlassCard(tr("card_progress"))
        progress_card = self.progress_card
        progress_h = QHBoxLayout()
        self.p_bar = GlassProgressBar()
        progress_h.addWidget(self.p_bar, 1)
        self.p_lbl = QLabel("0%")
        self.p_lbl.setStyleSheet(f"color: {T.accent}; font-weight: bold; font-size: 18px; margin-left: 10px; background: transparent;")
        progress_h.addWidget(self.p_lbl)
        progress_card.addLayout(progress_h)
        self.p_status = QLabel(tr("msg_ready"))
        self.p_status.setStyleSheet(f"color: {T.text_tertiary}; font-size: 13px; margin-top: 5px; background: transparent;")
        progress_card.addWidget(self.p_status)
        space.addWidget(progress_card)
        
        self.settings_card = GlassCard(tr("card_settings"))
        settings_card = self.settings_card
        form = QVBoxLayout()
        form.setSpacing(T.space_m)
        self.lbl_prompt = QLabel(tr("label_prompt"))
        l1 = self.lbl_prompt
        l1.setStyleSheet(f"color: {T.text_secondary}; background: transparent;")
        form.addWidget(l1)
        self.in_prompt = GlassInput("输入自定义 Prompt...")
        self.in_prompt.setText(config.PROMPT_TEXT)
        form.addWidget(self.in_prompt)
        self.lbl_delay = QLabel(tr("label_delay"))
        l2 = self.lbl_delay
        l2.setStyleSheet(f"color: {T.text_secondary}; background: transparent;")
        form.addWidget(l2)
        self.in_delay = GlassInput()
        self.in_delay.setText(str(config.DELAY_BETWEEN_PAGES))
        self.in_delay.setFixedWidth(100)
        form.addWidget(self.in_delay)
        
        # 分割线
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background: {T.divider}; margin-top: 10px; margin-bottom: 5px;")
        divider.setFixedHeight(1)
        form.addWidget(divider)
        
        # 聊天窗口设置标题 (显眼的蓝色)
        self.lbl_new_chat_settings = QLabel(tr("label_new_chat_settings"))
        self.lbl_new_chat_settings.setStyleSheet(f"""
            color: {T.accent}; 
            font-weight: bold;
            font-size: 14px;
            background: transparent;
            padding-top: 8px;
        """)
        form.addWidget(self.lbl_new_chat_settings)
        
        # 每PDF新建聊天开关
        self.cb_new_chat_pdf = QCheckBox(tr("label_new_chat_per_pdf"))
        self.cb_new_chat_pdf.setChecked(False)  # 默认关闭
        self.cb_new_chat_pdf.setStyleSheet(f"""
            QCheckBox {{
                color: {T.text_primary};
                font-size: 13px;
                background: transparent;
                padding: 4px 0;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
        """)
        self.cb_new_chat_pdf.toggled.connect(self._on_new_chat_pdf_toggled)
        form.addWidget(self.cb_new_chat_pdf)
        
        # 每N页新建聊天开关 + 输入框
        pages_layout = QHBoxLayout()
        pages_layout.setContentsMargins(0, 0, 0, 0)
        
        self.cb_new_chat_pages = QCheckBox(tr("label_new_chat_per_pages"))
        self.cb_new_chat_pages.setChecked(False)  # 默认关闭
        self.cb_new_chat_pages.setStyleSheet(f"""
            QCheckBox {{
                color: {T.text_primary};
                font-size: 13px;
                background: transparent;
                padding: 4px 0;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
        """)
        self.cb_new_chat_pages.toggled.connect(self._on_new_chat_pages_toggled)
        pages_layout.addWidget(self.cb_new_chat_pages)
        
        self.in_pages_threshold = GlassInput()
        self.in_pages_threshold.setText("30")
        self.in_pages_threshold.setFixedWidth(60)
        self.in_pages_threshold.setEnabled(False)  # 初始禁用
        self.in_pages_threshold.textChanged.connect(self._on_pages_threshold_changed)
        pages_layout.addWidget(self.in_pages_threshold)
        
        self.lbl_pages_suffix = QLabel(tr("label_pages_suffix"))
        self.lbl_pages_suffix.setStyleSheet(f"color: {T.text_secondary}; background: transparent;")
        pages_layout.addWidget(self.lbl_pages_suffix)
        pages_layout.addStretch()
        
        form.addLayout(pages_layout)
        
        # 分割线
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setStyleSheet(f"background: {T.divider}; margin-top: 10px; margin-bottom: 5px;")
        divider2.setFixedHeight(1)
        form.addWidget(divider2)
        
        # 自动暂停设置标题
        self.lbl_auto_pause_settings = QLabel(tr("label_auto_pause_settings"))
        self.lbl_auto_pause_settings.setStyleSheet(f"""
            color: {T.accent}; 
            font-weight: bold;
            font-size: 14px;
            background: transparent;
            padding-top: 8px;
        """)
        form.addWidget(self.lbl_auto_pause_settings)
        
        # 自动暂停开关
        self.cb_auto_pause_on_limit = QCheckBox(tr("label_auto_pause_on_limit"))
        self.cb_auto_pause_on_limit.setChecked(False)  # 默认关闭
        self.cb_auto_pause_on_limit.setStyleSheet(f"""
            QCheckBox {{
                color: {T.text_primary};
                font-size: 13px;
                background: transparent;
                padding: 4px 0;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
        """)
        self.cb_auto_pause_on_limit.toggled.connect(self._on_auto_pause_toggled)
        form.addWidget(self.cb_auto_pause_on_limit)
        
        # 暂停时长选择
        pause_duration_layout = QHBoxLayout()
        pause_duration_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_pause_duration = QLabel(tr("label_pause_duration"))
        self.lbl_pause_duration.setStyleSheet(f"color: {T.text_secondary}; background: transparent;")
        pause_duration_layout.addWidget(self.lbl_pause_duration)
        
        self.combo_pause_duration = QComboBox()
        self.combo_pause_duration.addItem(tr("pause_30min"), 30)
        self.combo_pause_duration.addItem(tr("pause_1hour"), 60)
        self.combo_pause_duration.addItem(tr("pause_custom"), -1)
        self.combo_pause_duration.addItem(tr("pause_forever"), 0)
        self.combo_pause_duration.setFixedWidth(120)
        self.combo_pause_duration.setStyleSheet(f"""
            QComboBox {{
                background: rgba(255,255,255,0.05);
                border: 1px solid {T.divider};
                border-radius: 4px;
                color: {T.text_primary};
                padding: 4px 8px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background: {T.bg_mid};
                color: {T.text_primary};
                selection-background-color: {T.accent};
            }}
        """)
        self.combo_pause_duration.setEnabled(False)  # 初始禁用
        self.combo_pause_duration.currentIndexChanged.connect(self._on_pause_duration_changed)
        pause_duration_layout.addWidget(self.combo_pause_duration)
        
        # 自定义时长输入框
        self.in_custom_pause = GlassInput()
        self.in_custom_pause.setText("30")
        self.in_custom_pause.setFixedWidth(60)
        self.in_custom_pause.setEnabled(False)
        self.in_custom_pause.setVisible(False)  # 初始隐藏
        self.in_custom_pause.textChanged.connect(self._on_custom_pause_changed)
        pause_duration_layout.addWidget(self.in_custom_pause)
        
        self.lbl_custom_minutes = QLabel(tr("label_custom_minutes"))
        self.lbl_custom_minutes.setStyleSheet(f"color: {T.text_secondary}; background: transparent;")
        self.lbl_custom_minutes.setVisible(False)  # 初始隐藏
        pause_duration_layout.addWidget(self.lbl_custom_minutes)
        
        pause_duration_layout.addStretch()
        form.addLayout(pause_duration_layout)
        
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
            self._log(tr("msg_removed", Path(path).name))

    def _on_drop(self, files):
        new_cnt = 0
        for f in files:
            if f not in self.pdf_files:
                self.pdf_files.append(f)
                new_cnt += 1
        if new_cnt:
            self._render_list()
            self._log(tr("msg_added_files", new_cnt))
            
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
    
    # 新建聊天设置事件处理
    def _on_new_chat_pdf_toggled(self, checked: bool):
        """每PDF新建聊天开关变化"""
        self.new_chat_per_pdf = checked
        print(f"[DEBUG] new_chat_per_pdf = {checked}")
        
    def _on_new_chat_pages_toggled(self, checked: bool):
        """每N页新建聊天开关变化"""
        self.new_chat_per_pages = checked
        self.in_pages_threshold.setEnabled(checked)
        print(f"[DEBUG] new_chat_per_pages = {checked}")
        
    def _on_pages_threshold_changed(self, text: str):
        """页数阈值变化"""
        try:
            self.new_chat_pages_threshold = max(1, int(text))
            print(f"[DEBUG] new_chat_pages_threshold = {self.new_chat_pages_threshold}")
        except ValueError:
            pass
    
    # 自动暂停设置事件处理
    def _on_auto_pause_toggled(self, checked: bool):
        """自动暂停开关变化"""
        self.auto_pause_on_limit = checked
        self.combo_pause_duration.setEnabled(checked)
        is_custom = self.combo_pause_duration.currentData() == -1
        self.in_custom_pause.setEnabled(checked and is_custom)
        print(f"[DEBUG] auto_pause_on_limit = {checked}")
        
    def _on_pause_duration_changed(self, index: int):
        """暂停时长选择变化"""
        duration = self.combo_pause_duration.currentData()
        is_custom = (duration == -1)
        is_enabled = self.auto_pause_on_limit
        
        self.in_custom_pause.setVisible(is_custom)
        self.lbl_custom_minutes.setVisible(is_custom)
        self.in_custom_pause.setEnabled(is_custom and is_enabled)
        
        if is_custom:
            text = self.in_custom_pause.text().strip()
            if text and text.isdigit():
                value = int(text)
                # 限制范围：1-1440 分钟（最大24小时）
                self.pause_duration_minutes = max(1, min(1440, value))
            else:
                self.pause_duration_minutes = 30  # 默认值
                self.in_custom_pause.setText("30")
        else:
            self.pause_duration_minutes = duration  # 30, 60, 或 0(无限)
        print(f"[DEBUG] pause_duration_minutes = {self.pause_duration_minutes}")
        
    def _on_custom_pause_changed(self, text: str):
        """自定义暂停时长变化"""
        try:
            value = int(text)
            # 限制范围：1-1440 分钟（最大24小时）
            self.pause_duration_minutes = max(1, min(1440, value))
            if value > 1440:
                self.in_custom_pause.setText("1440")  # 自动修正为最大值
            print(f"[DEBUG] pause_duration_minutes = {self.pause_duration_minutes}")
        except ValueError:
            pass
    
    def _is_rate_limit_error(self, error: Exception) -> bool:
        """检测是否是 API 上限错误"""
        error_str = str(error).lower()
        
        # 精确匹配的上限关键词（来自各 AI 平台实际错误消息）
        limit_keywords = [
            # 通用
            "rate limit", "rate_limit", "ratelimit",
            "quota exceeded", "quota_exceeded",
            "too many requests", "too_many_requests",
            "limit reached", "reached your limit", "reached the limit",
            "usage limit", "usage_limit",
            "resource_exhausted", "resource exhausted",
            "429",  # HTTP 429 Too Many Requests
            
            # ChatGPT / OpenAI
            "message limit", "messages per hour",
            "exceeded your current quota",
            "you've reached your usage limit",
            
            # Claude
            "you've reached your usage limit for today",
            "claude usage limit reached",
            "limit will reset",
            "conversation budget",
            
            # Gemini
            "you've reached your limit for chats",
            "reached your rate limit",
            "please wait before sending",
            
            # 通用限制
            "daily limit", "hour limit", "hourly limit",
            "limit for the hour", "limit for today"
        ]
        
        return any(kw in error_str for kw in limit_keywords)
    
    @Slot()
    def _on_limit_detected(self):
        """检测到 AI 上限时调用"""
        # 如果已有定时器在运行，先停止
        if self._limit_pause_timer is not None:
            self._limit_pause_timer.stop()
            self._limit_pause_timer = None
        
        self.is_running = False
        self._batch_was_paused = True
        
        if self.pause_duration_minutes == 0:
            # 无限暂停
            self._log(tr("msg_paused_forever"), "warning")
            self._reset_ui(keep_progress=True)
            return
        
        # 计算暂停时间
        pause_seconds = self.pause_duration_minutes * 60
        self._limit_pause_remaining = pause_seconds
        
        # 格式化时间显示（使用国际化）
        from src.i18n import get_language
        lang = get_language()
        if self.pause_duration_minutes >= 60:
            hours = self.pause_duration_minutes // 60
            time_str = f"{hours} {'hour' if lang == 'en' else '小时'}"
        else:
            time_str = f"{self.pause_duration_minutes} {'min' if lang == 'en' else '分钟'}"
        
        self._log(tr("msg_limit_detected", time_str), "warning")
        self._log(tr("msg_auto_resume_in", time_str), "info")
        
        # 启动定时器（设置 self 为父对象，确保内存管理）
        from PySide6.QtCore import QTimer
        self._limit_pause_timer = QTimer(self)
        self._limit_pause_timer.timeout.connect(self._on_pause_tick)
        self._limit_pause_timer.start(1000)  # 每秒触发
        
        self._reset_ui(keep_progress=True)
        
    def _on_pause_tick(self):
        """暂停倒计时"""
        self._limit_pause_remaining -= 1
        
        # 每10秒更新一次显示
        if self._limit_pause_remaining % 10 == 0 and self._limit_pause_remaining > 0:
            self.p_status.setText(tr("msg_limit_pause_countdown", self._limit_pause_remaining))
        
        if self._limit_pause_remaining <= 0:
            # 停止定时器
            if self._limit_pause_timer:
                self._limit_pause_timer.stop()
                self._limit_pause_timer = None
            
            # 自动恢复
            self._log(tr("msg_auto_resumed"), "success")
            self._start_processing()
        
    def _start_browser(self):
        self.btn_browser.setEnabled(False)
        self.platform_combo.setEnabled(False)  # 禁用平台切换
        
        # 获取选中的平台
        platform_id = self.platform_combo.currentData()
        platform_name = self.platform_combo.currentText()
        
        self._log(tr("msg_launching_browser", platform_name), "info")
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
                        self.sig_log.emit(tr("msg_browser_closed_progress", self.current_pdf_index + 1, self.current_page_index + 1), "warning")
                    else:
                        self.sig_log.emit(tr("msg_browser_closed"), "warning")
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
                self.sig_log.emit(tr("msg_platform_ready", platform_name), "success")
                self.sig_enable_start.emit(True)
                print("[DEBUG] signals emitted")
            except Exception as e:
                import traceback
                print(f"[DEBUG] Exception in start(): {e}")
                print(traceback.format_exc())
                self.sig_log.emit(tr("msg_launch_failed", str(e)), "error")
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
        
        # 取消暂停定时器（如果存在），防止用户手动恢复后定时器仍触发
        if self._limit_pause_timer is not None:
            self._limit_pause_timer.stop()
            self._limit_pause_timer = None
        
        if not self.pdf_files:
            self._log(tr("msg_add_pdf_first"), "warning")
            return
            
        if self.bot is None:
            self._log(tr("msg_launch_browser_first"), "warning")
            return
        
        self.is_running = True
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        
        prompt = self.in_prompt.text()
        try: delay = float(self.in_delay.text())
        except: delay = 3.0
        
        # 检查是否是自动处理下一个PDF（批量处理中）
        is_auto_next = getattr(self, '_is_auto_next_pdf', False)
        if is_auto_next:
            self._is_auto_next_pdf = False  # 重置标志
            print(f"[DEBUG] 自动处理下一个 PDF: {self._current_preview_pdf}")
            # 直接进入批量模式处理，跳过续传检测
        else:
            # 检查是否是续传模式：只有用户明确暂停后才是续传
            is_resume = getattr(self, '_batch_was_paused', False) and len(self.all_page_images) > 0
            
            if is_resume:
                print(f"[DEBUG] 续传模式: 继续处理 {self._current_preview_pdf}")
                self._batch_was_paused = False  # 重置暂停标志
            else:
                # 非续传：始终从第一个 PDF 开始
                print(f"[DEBUG] 从第一个 PDF 开始批量处理")
                self._batch_was_paused = False
                # 清空之前的预览状态
                self.all_page_images = []
                self.page_enabled = []
                self.page_groups = []
                self.custom_batch_order = None
                self._current_preview_pdf = None
                self.current_batch_index = 0  # 重置批次索引
                
                # 选中第一个 PDF 并开始处理
                self.file_list.setCurrentRow(0)
                self._auto_process_next_pdf = True
                self._preview_pages()
                return
        
        # 续传模式：检查是否有预加载的页面
        use_batch_mode = len(self.all_page_images) > 0
        
        if use_batch_mode:
            # 多页批量模式
            batches = self._get_page_batches()
            if not batches:
                self._log(tr("msg_no_enabled_pages"), "warning")
                self._reset_ui()
                return
                
            # 检查是否是续传
            start_batch = self.current_batch_index
            is_resume = start_batch > 0
            if is_resume:
                self._log(tr("msg_resume_processing", start_batch + 1, len(batches)), "info")
            else:
                self.p_bar.setValue(0)
                self.p_lbl.setText("0%")
                self.p_status.setText(tr("msg_preparing"))
                self._log(tr("msg_batch_processing", len(batches)))
                
            # 在开始处理前保存当前 PDF 索引（避免拖拽排序后路径匹配问题）
            current_pdf_idx = self.file_list.currentRow()
            # 重要：捕获当前 PDF 的图片列表副本，避免异步处理过程中被其他 PDF 数据污染
            current_all_page_images = self.all_page_images.copy()
            current_page_enabled = self.page_enabled.copy()
            print(f"[DEBUG] 开始处理 PDF 索引: {current_pdf_idx}, 总数: {len(self.pdf_files)}")
            print(f"[DEBUG] 捕获的图片数: {len(current_all_page_images)}, 启用页数: {sum(current_page_enabled)}")
            
            async def process_batches():
                try:
                    total_batches = len(batches)
                    print(f"[DEBUG] process_batches: 开始处理，总批次 = {total_batches}")
                    
                    for batch_idx in range(start_batch, total_batches):
                        print(f"[DEBUG] process_batches: 处理批次 {batch_idx + 1}/{total_batches}, is_running = {self.is_running}")
                        if not self.is_running:
                            self.current_batch_index = batch_idx
                            print(f"[DEBUG] process_batches: is_running 为 False，退出循环")
                            break
                        
                        # 每PDF新建聊天：仅在第一个批次且不是第一个PDF时创建新聊天
                        if batch_idx == 0 and current_pdf_idx > 0 and self.new_chat_per_pdf:
                            self.sig_log.emit(tr("msg_creating_new_chat"), "info")
                            try:
                                await self.bot.create_new_chat()
                                self.sig_log.emit(tr("msg_new_chat_created"), "success")
                                self.pages_since_last_new_chat = 0  # 重置页数计数
                                await asyncio.sleep(0.5)  # 简短缓冲
                            except Exception as e:
                                self.sig_log.emit(tr("msg_new_chat_failed", str(e)), "warning")
                            
                        batch = batches[batch_idx]
                        batch_size = len(batch)
                        
                        # 实时检查：跳过已禁用的页面
                        # 注意：在自动批量处理模式下，跳过此检查，因为 preview_dialog 的状态可能已被更新为其他 PDF 的数据
                        is_auto_mode = getattr(self, '_is_auto_next_pdf', False)
                        if not is_auto_mode and hasattr(self, 'preview_dialog') and self.preview_dialog:
                            current_enabled = self.preview_dialog.page_preview.get_page_enabled_list()
                            # 验证数据一致性：确保页数匹配（使用闭包捕获的图片列表）
                            if len(current_enabled) == len(current_all_page_images):
                                # 过滤掉已禁用的页面
                                filtered_batch = []
                                for img_path in batch:
                                    # 查找图片对应的页面索引（使用闭包捕获的图片列表）
                                    if img_path in current_all_page_images:
                                        idx = current_all_page_images.index(img_path)
                                        if idx < len(current_enabled) and current_enabled[idx]:
                                            filtered_batch.append(img_path)
                                
                                if not filtered_batch:
                                    # 该批次所有页面都被禁用，跳过
                                    self.sig_log.emit(f"批次 {batch_idx+1} 中的页面已被禁用，跳过", "info")
                                    continue
                                batch = filtered_batch
                                batch_size = len(batch)
                            else:
                                print(f"[DEBUG] 跳过实时检查：页数不匹配 (dialog: {len(current_enabled)}, captured: {len(current_all_page_images)})")
                        
                        pct = int((batch_idx + 1) / total_batches * 100)
                        if batch_size > 1:
                            self.sig_progress.emit(pct, tr("msg_batch_progress", batch_idx+1, total_batches, batch_size))
                        else:
                            self.sig_progress.emit(pct, tr("msg_page_progress", batch_idx+1, total_batches))
                        
                        # 空白输出重试逻辑
                        max_retries = config.EMPTY_RESPONSE_MAX_RETRIES
                        retry_delay = config.EMPTY_RESPONSE_RETRY_DELAY
                        retry_count = 0
                        success = False
                        
                        while retry_count <= max_retries and not success:
                            if not self.is_running:
                                break
                            
                            try:
                                if retry_count > 0:
                                    self.sig_log.emit(tr("msg_retry", retry_count, max_retries, batch_idx+1), "warning")
                                
                                # 使用多图片上传方法
                                await self.bot.upload_images_and_send(batch, prompt)
                                response = await self.bot.wait_for_response_complete()
                                
                                # 检测空白输出 - 使用改进的检测方法
                                is_empty = False
                                if response is None or (isinstance(response, str) and response.strip() == ""):
                                    is_empty = True
                                
                                # 如果有 _detect_empty_response 方法（ChatGPT），使用更精确的检测
                                if hasattr(self.bot, '_detect_empty_response') and hasattr(self.bot, '_initial_message_count'):
                                    is_empty = await self.bot._detect_empty_response(self.bot._initial_message_count)
                                
                                if is_empty:
                                    retry_count += 1
                                    self.sig_log.emit(f"[空白检测] 检测到空白输出 (重试 {retry_count}/{max_retries})", "warning")
                                    if retry_count <= max_retries:
                                        self.sig_log.emit(tr("msg_empty_response_retry", retry_delay), "warning")
                                        await asyncio.sleep(retry_delay)
                                        continue
                                    else:
                                        self.sig_log.emit(tr("msg_retry_failed", max_retries), "error")
                                        success = True
                                else:
                                    success = True
                                    self.current_batch_index = batch_idx + 1
                                    
                            except Exception as e:
                                self.sig_log.emit(tr("msg_send_failed", str(e)), "error")
                                
                                # 检测是否是 API 上限错误
                                if self.auto_pause_on_limit and self._is_rate_limit_error(e):
                                    # 保存当前批次位置以便恢复
                                    self.current_batch_index = batch_idx
                                    # 使用信号在主线程触发暂停
                                    from PySide6.QtCore import QMetaObject, Qt as QtCoreQt
                                    QMetaObject.invokeMethod(
                                        self, "_on_limit_detected",
                                        QtCoreQt.QueuedConnection
                                    )
                                    return  # 退出处理循环
                                
                                retry_count += 1
                                if retry_count <= max_retries:
                                    self.sig_log.emit(tr("msg_wait_retry", retry_delay), "warning")
                                    await asyncio.sleep(retry_delay)
                                else:
                                    self.sig_log.emit(tr("msg_retry_failed", max_retries), "error")
                                    success = True
                        
                        # 每N页新建聊天：检查累计页数是否达到阈值
                        if success and self.new_chat_per_pages and self.is_running:
                            self.pages_since_last_new_chat += batch_size
                            if self.pages_since_last_new_chat >= self.new_chat_pages_threshold:
                                # 只有在不是最后一个批次时才创建新聊天
                                if batch_idx < total_batches - 1:
                                    self.sig_log.emit(tr("msg_creating_new_chat"), "info")
                                    try:
                                        await self.bot.create_new_chat()
                                        self.sig_log.emit(tr("msg_new_chat_created"), "success")
                                        self.pages_since_last_new_chat = 0  # 重置计数
                                        await asyncio.sleep(0.5)
                                    except Exception as e:
                                        self.sig_log.emit(tr("msg_new_chat_failed", str(e)), "warning")
                        
                        if batch_idx < total_batches - 1 and self.is_running:
                            await asyncio.sleep(delay)
                    
                    # 批次循环结束后的调试信息
                    print(f"[DEBUG] 批次循环结束: 共处理 {total_batches} 批次, is_running={self.is_running}")
                    
                    if self.is_running:
                        self.current_batch_index = 0
                        
                        # 使用保存的 current_pdf_idx（在闭包中捕获）
                        # 不再通过路径查找，避免拖拽排序后的索引问题
                        print(f"[DEBUG] 处理完成，当前 PDF 索引: {current_pdf_idx}, 总数: {len(self.pdf_files)}")
                        
                        next_pdf_idx = current_pdf_idx + 1
                        print(f"[DEBUG] 下一个 PDF 索引: {next_pdf_idx}")
                        if next_pdf_idx < len(self.pdf_files):
                            # 还有下一个 PDF，自动切换并处理
                            self.sig_log.emit(f"当前 PDF 处理完成，准备处理下一个 ({next_pdf_idx + 1}/{len(self.pdf_files)})", "success")
                            
                            # 使用信号在主线程中处理（而不是 QTimer，因为我们在异步线程中）
                            self.sig_process_next_pdf.emit(next_pdf_idx)
                            return  # 不重置 UI，继续处理
                        else:
                            self.sig_progress.emit(100, tr("msg_complete"))
                            self.sig_log.emit(tr("msg_all_complete"), "success")
                    self.sig_reset_ui.emit()
                    
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                    self.sig_log.emit(tr("msg_processing_error", str(e)), "error")
                    self.sig_reset_ui.emit()
            
            self._run_async(process_batches())
            
        else:
            # 传统模式：逐个 PDF 逐页处理
            # 检查是否是续传（有进度记录）
            is_resume = self.current_pdf_index > 0 or self.current_page_index > 0
            if is_resume:
                self._log(tr("msg_resume_legacy", self.current_pdf_index + 1, self.current_page_index + 1), "info")
            else:
                self.p_bar.setValue(0)
                self.p_lbl.setText("0%")
                self.p_status.setText(tr("msg_preparing"))
                self._log(tr("msg_starting"))
            
            # 保存起始位置
            start_pdf = self.current_pdf_index
            start_page = self.current_page_index
            
            async def process():
                try:
                    total = len(self.pdf_files)
                    print(f"[DEBUG] 开始处理，共 {total} 个 PDF 文件")
                    
                    if total == 0:
                        self.sig_log.emit(tr("msg_no_pdf_files"), "warning")
                        self.sig_reset_ui.emit()
                        return
                    
                    for i, pdf in enumerate(self.pdf_files):
                        # 跳过已处理的 PDF
                        if i < start_pdf:
                            continue
                        
                        if not self.is_running:
                            self.current_pdf_index = i
                            break
                        
                        name = Path(pdf).name
                        self.sig_log.emit(tr("msg_processing_pdf", name, i+1, total), "info")
                        
                        # 转换 PDF
                        try:
                            from src.pdf_converter import convert_pdf_to_images
                            images = convert_pdf_to_images(pdf)
                            if not images:
                                raise ValueError(tr("msg_no_images"))
                        except Exception as e:
                            self.sig_log.emit(tr("msg_convert_failed", str(e)), "error")
                            continue
                        
                        # 确定起始页
                        page_start = start_page if i == start_pdf else 0
                        
                        # 发送处理
                        for j, img in enumerate(images):
                            if j < page_start:
                                continue
                            
                            if not self.is_running:
                                self.current_pdf_index = i
                                self.current_page_index = j
                                break
                            
                            pct = int((i/total + (j+1)/len(images)/total) * 100)
                            self.sig_progress.emit(pct, f"{name} - p.{j+1}/{len(images)}")
                            
                            max_retries = config.EMPTY_RESPONSE_MAX_RETRIES
                            retry_delay = config.EMPTY_RESPONSE_RETRY_DELAY
                            retry_count = 0
                            success = False
                            
                            while retry_count <= max_retries and not success:
                                if not self.is_running:
                                    break
                                
                                try:
                                    if retry_count > 0:
                                        self.sig_log.emit(tr("msg_retry_page", retry_count, max_retries, name, j+1), "warning")
                                    
                                    await self.bot.upload_images_and_send([img], prompt)
                                    response = await self.bot.wait_for_response_complete()
                                    
                                    # 检测空白输出 - 使用改进的检测方法
                                    is_empty = False
                                    if response is None or (isinstance(response, str) and response.strip() == ""):
                                        is_empty = True
                                    
                                    # 如果有 _detect_empty_response 方法（ChatGPT），使用更精确的检测
                                    if hasattr(self.bot, '_detect_empty_response') and hasattr(self.bot, '_initial_message_count'):
                                        is_empty = await self.bot._detect_empty_response(self.bot._initial_message_count)
                                    
                                    if is_empty:
                                        retry_count += 1
                                        self.sig_log.emit(f"[空白检测] 检测到空白输出 (重试 {retry_count}/{max_retries})", "warning")
                                        if retry_count <= max_retries:
                                            self.sig_log.emit(tr("msg_empty_response_retry", retry_delay), "warning")
                                            await asyncio.sleep(retry_delay)
                                            continue
                                        else:
                                            self.sig_log.emit(tr("msg_retry_page_failed", max_retries), "error")
                                            success = True
                                    else:
                                        success = True
                                        self.current_pdf_index = i
                                        self.current_page_index = j + 1
                                        
                                except Exception as e:
                                    self.sig_log.emit(tr("msg_send_failed", str(e)), "error")
                                    
                                    # 检测是否是 API 上限错误
                                    if self.auto_pause_on_limit and self._is_rate_limit_error(e):
                                        self.current_pdf_index = i
                                        self.current_page_index = j
                                        from PySide6.QtCore import QMetaObject, Qt as QtCoreQt
                                        QMetaObject.invokeMethod(
                                            self, "_on_limit_detected",
                                            QtCoreQt.QueuedConnection
                                        )
                                        return
                                    
                                    retry_count += 1
                                    if retry_count <= max_retries:
                                        self.sig_log.emit(tr("msg_wait_retry", retry_delay), "warning")
                                        await asyncio.sleep(retry_delay)
                                    else:
                                        self.sig_log.emit(tr("msg_retry_page_failed", max_retries), "error")
                                        success = True
                            
                            if j < len(images) - 1 and self.is_running: 
                                await asyncio.sleep(delay)
                        
                        if self.is_running:
                            self.current_page_index = 0
                            self.current_pdf_index = i + 1
                    
                    if self.is_running:
                        self.current_pdf_index = 0
                        self.current_page_index = 0
                        self.sig_progress.emit(100, tr("msg_complete"))
                        self.sig_log.emit(tr("msg_all_complete"), "success")
                    self.sig_reset_ui.emit()
                    
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                    self.sig_log.emit(tr("msg_processing_error", str(e)), "error")
                    self.sig_reset_ui.emit()
            
            self._run_async(process())

        
    def _upd_prog(self, val, txt):
        self.p_bar.setValue(val)
        self.p_lbl.setText(f"{val}%")
        self.p_status.setText(txt)
        
    def _stop(self):
        self.is_running = False
        self._batch_was_paused = True  # 标记用户暂停，下次可以续传
        
        # 取消暂停定时器（如果存在）
        if self._limit_pause_timer is not None:
            self._limit_pause_timer.stop()
            self._limit_pause_timer = None
        
        self._log(tr("msg_paused", self.current_pdf_index + 1, self.current_page_index + 1), "warning")
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
            self.p_status.setText(tr("msg_ready"))
        else:
            # 暂停时保留进度显示
            self.p_status.setText(tr("msg_stopped"))
    
    def _toggle_language(self):
        """切换语言"""
        new_lang = toggle_language()
        self._update_language()
        
    def _update_language(self):
        """更新界面语言"""
        lang = get_language()
        # 更新语言按钮文本
        self.btn_lang.setText("🌐 中" if lang == "en" else "🌐 EN")
        
        # 更新按钮文本
        self.btn_browser.setText(tr("btn_launch_browser"))
        self.btn_start.setText(tr("btn_start"))
        self.btn_stop.setText(tr("btn_stop"))
        self.btn_preview.setText(tr("btn_preview"))
        
        # 更新卡片标题 (通过 title_label)
        if hasattr(self, 'card_doc_queue') and hasattr(self.card_doc_queue, 'title_label'):
            self.card_doc_queue.title_label.setText(tr("card_doc_queue"))
        if hasattr(self, 'progress_card') and hasattr(self.progress_card, 'title_label'):
            self.progress_card.title_label.setText(tr("card_progress"))
        if hasattr(self, 'settings_card') and hasattr(self.settings_card, 'title_label'):
            self.settings_card.title_label.setText(tr("card_settings"))
        
        # 更新标签
        if hasattr(self, 'lbl_prompt'):
            self.lbl_prompt.setText(tr("label_prompt"))
        if hasattr(self, 'lbl_delay'):
            self.lbl_delay.setText(tr("label_delay"))
        if hasattr(self, 'lbl_platform'):
            self.lbl_platform.setText(tr("label_platform"))
        
        # 更新新建聊天设置标签
        if hasattr(self, 'lbl_new_chat_settings'):
            self.lbl_new_chat_settings.setText(tr("label_new_chat_settings"))
        if hasattr(self, 'cb_new_chat_pdf'):
            self.cb_new_chat_pdf.setText(tr("label_new_chat_per_pdf"))
        if hasattr(self, 'cb_new_chat_pages'):
            self.cb_new_chat_pages.setText(tr("label_new_chat_per_pages"))
        if hasattr(self, 'lbl_pages_suffix'):
            self.lbl_pages_suffix.setText(tr("label_pages_suffix"))
        
        # 更新自动暂停设置标签
        if hasattr(self, 'lbl_auto_pause_settings'):
            self.lbl_auto_pause_settings.setText(tr("label_auto_pause_settings"))
        if hasattr(self, 'cb_auto_pause_on_limit'):
            self.cb_auto_pause_on_limit.setText(tr("label_auto_pause_on_limit"))
        if hasattr(self, 'lbl_pause_duration'):
            self.lbl_pause_duration.setText(tr("label_pause_duration"))
        if hasattr(self, 'lbl_custom_minutes'):
            self.lbl_custom_minutes.setText(tr("label_custom_minutes"))
        if hasattr(self, 'combo_pause_duration'):
            # 更新下拉框选项文本
            self.combo_pause_duration.setItemText(0, tr("pause_30min"))
            self.combo_pause_duration.setItemText(1, tr("pause_1hour"))
            self.combo_pause_duration.setItemText(2, tr("pause_custom"))
            self.combo_pause_duration.setItemText(3, tr("pause_forever"))
        
        # 更新状态
        if not self.is_running:
            self.p_status.setText(tr("msg_ready"))
        
        # 更新页面预览弹窗
        if hasattr(self, 'preview_dialog') and self.preview_dialog:
            self.preview_dialog.update_language()
        
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
