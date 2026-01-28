"""
PDF 页面预览组件

提供 PDF 页面缩略图预览、多选、跳过、排序和分组功能
"""
import os
from pathlib import Path
from typing import List, Optional, Callable

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QLabel, QCheckBox, QPushButton, QFrame, QSpinBox, QButtonGroup,
    QRadioButton, QListWidget, QListWidgetItem, QSizePolicy, QComboBox,
    QGraphicsDropShadowEffect, QDialog, QApplication
)
from PySide6.QtCore import Qt, Signal, QSize, QMimeData
from PySide6.QtGui import QPixmap, QFont, QPainter, QColor, QDrag, QPen, QBrush

from src.i18n import tr, get_language


# ═══════════════════════════════════════════════════════════
# Design Tokens (与主界面保持一致)
# ═══════════════════════════════════════════════════════════

class Tokens:
    # 颜色
    text_primary = "#F8FAFC"
    text_secondary = "#94A3B8"
    text_tertiary = "#64748B"
    accent = "#3B82F6"
    accent_light = "#60A5FA"
    danger = "#EF4444"
    success = "#10B981"
    warning = "#FBBF24"
    
    # 背景
    bg_card = "rgba(255, 255, 255, 0.03)"
    bg_hover = "rgba(255, 255, 255, 0.08)"
    bg_selected = "rgba(59, 130, 246, 0.2)"
    border = "rgba(255, 255, 255, 0.1)"
    
    # 间距
    space_xs = 4
    space_s = 8
    space_m = 12
    space_l = 16
    space_xl = 24
    
    # 圆角
    radius_s = 6
    radius_m = 10
    radius_l = 14

T = Tokens()


def rgba(r, g, b, a):
    return QColor(r, g, b, a)


# ═══════════════════════════════════════════════════════════
# 图片查看器弹窗
# ═══════════════════════════════════════════════════════════

class ImageViewerDialog(QDialog):
    """图片查看器弹窗 - 查看清晰大图"""
    
    def __init__(self, image_path: str, page_index: int, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.page_index = page_index
        self.scale_factor = 1.0
        
        self.setWindowTitle(f"第 {page_index + 1} 页")
        self.setMinimumSize(800, 600)
        self.resize(1000, 750)
        self.setModal(True)
        
        self._setup_ui()
        
    def _setup_ui(self):
        self.setStyleSheet(f"""
            QDialog {{
                background: #0D0D18;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 工具栏
        toolbar = QWidget()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet(f"""
            background: rgba(255, 255, 255, 0.05);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        """)
        
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 0, 16, 0)
        
        # 页码显示
        title = QLabel(f"第 {self.page_index + 1} 页")
        title.setStyleSheet(f"color: {T.text_primary}; font-size: 14px; font-weight: bold;")
        toolbar_layout.addWidget(title)
        
        toolbar_layout.addStretch()
        
        # 缩放按钮
        btn_zoom_out = QPushButton("−")
        btn_zoom_out.setFixedSize(36, 36)
        btn_zoom_out.setCursor(Qt.PointingHandCursor)
        btn_zoom_out.setStyleSheet(self._button_style())
        btn_zoom_out.clicked.connect(self._zoom_out)
        toolbar_layout.addWidget(btn_zoom_out)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(60)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setStyleSheet(f"color: {T.text_secondary}; font-size: 13px;")
        toolbar_layout.addWidget(self.zoom_label)
        
        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setFixedSize(36, 36)
        btn_zoom_in.setCursor(Qt.PointingHandCursor)
        btn_zoom_in.setStyleSheet(self._button_style())
        btn_zoom_in.clicked.connect(self._zoom_in)
        toolbar_layout.addWidget(btn_zoom_in)
        
        toolbar_layout.addSpacing(16)
        
        btn_fit = QPushButton("适应窗口")
        btn_fit.setFixedHeight(36)
        btn_fit.setCursor(Qt.PointingHandCursor)
        btn_fit.setStyleSheet(self._button_style())
        btn_fit.clicked.connect(self._fit_to_window)
        toolbar_layout.addWidget(btn_fit)
        
        btn_actual = QPushButton("实际大小")
        btn_actual.setFixedHeight(36)
        btn_actual.setCursor(Qt.PointingHandCursor)
        btn_actual.setStyleSheet(self._button_style())
        btn_actual.clicked.connect(self._actual_size)
        toolbar_layout.addWidget(btn_actual)
        
        layout.addWidget(toolbar)
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # 关闭自动调整，手动控制尺寸
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: #0D0D18;
                border: none;
            }}
            QScrollBar:vertical, QScrollBar:horizontal {{
                background: rgba(0, 0, 0, 0.3);
                width: 10px;
                height: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle {{
                background: rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                min-height: 30px;
                min-width: 30px;
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                height: 0px;
                width: 0px;
            }}
        """)
        
        # 图片标签（直接放在滚动区域，不用额外容器）
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background: #0D0D18;")
        
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area, 1)
        
        # 加载图片
        self._load_image()
        
    def _button_style(self):
        return f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                color: {T.text_secondary};
                padding: 4px 12px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.15);
                border-color: {T.accent};
                color: {T.text_primary};
            }}
        """
        
    def _load_image(self):
        """加载原始图片"""
        import os
        if os.path.exists(self.image_path):
            self.original_pixmap = QPixmap(self.image_path)
            # 先显示原图，showEvent 会自动适配窗口
            self._update_image()
        else:
            self.image_label.setText("图片加载失败")
            self.image_label.setStyleSheet(f"color: {T.danger}; font-size: 14px;")
            
    def showEvent(self, event):
        """窗口显示时自动适配窗口大小"""
        super().showEvent(event)
        # 使用定时器延迟执行，确保窗口尺寸已经正确
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, self._fit_to_window)
            
    def _update_image(self):
        """根据缩放比例更新图片显示"""
        if hasattr(self, 'original_pixmap') and not self.original_pixmap.isNull():
            new_width = int(self.original_pixmap.width() * self.scale_factor)
            new_height = int(self.original_pixmap.height() * self.scale_factor)
            scaled = self.original_pixmap.scaled(
                new_width, new_height,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
            self.image_label.resize(scaled.size())  # 手动调整标签大小
            self.zoom_label.setText(f"{int(self.scale_factor * 100)}%")
            
    def _zoom_in(self):
        """放大"""
        if self.scale_factor < 5.0:
            self.scale_factor *= 1.25
            self._update_image()
            
    def _zoom_out(self):
        """缩小"""
        if self.scale_factor > 0.1:
            self.scale_factor /= 1.25
            self._update_image()
            
    def _fit_to_window(self):
        """适应窗口"""
        if hasattr(self, 'original_pixmap') and not self.original_pixmap.isNull():
            viewport = self.scroll_area.viewport()
            vw, vh = viewport.width() - 20, viewport.height() - 20
            pw, ph = self.original_pixmap.width(), self.original_pixmap.height()
            
            if pw > 0 and ph > 0:
                scale_w = vw / pw
                scale_h = vh / ph
                self.scale_factor = min(scale_w, scale_h, 1.0)  # 不超过原始大小
                self._update_image()
            
    def _actual_size(self):
        """实际大小"""
        self.scale_factor = 1.0
        self._update_image()
        
    def wheelEvent(self, event):
        """鼠标滚轮：Ctrl+滚轮缩放，普通滚轮滚动"""
        modifiers = QApplication.keyboardModifiers()
        
        if modifiers & Qt.ControlModifier:
            # Ctrl+滚轮：缩放
            delta = event.angleDelta().y()
            if delta > 0:
                self._zoom_in()
            else:
                self._zoom_out()
            event.accept()
        else:
            # 普通滚轮：传递给滚动区域处理滚动
            self.scroll_area.wheelEvent(event)


# ═══════════════════════════════════════════════════════════
# 分组内小缩略图
# ═══════════════════════════════════════════════════════════

class MiniThumbnail(QFrame):
    """分组内的小缩略图"""
    
    removed = Signal(int)  # 从分组移除信号
    
    MINI_SIZE = 50
    
    def __init__(self, index: int, image_path: str, parent=None):
        super().__init__(parent)
        self.index = index
        self.image_path = image_path
        
        self.setFixedSize(self.MINI_SIZE + 8, self.MINI_SIZE + 20)
        self.setCursor(Qt.PointingHandCursor)
        self.setAcceptDrops(False)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # 缩略图
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(self.MINI_SIZE, self.MINI_SIZE)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setStyleSheet(f"""
            background: rgba(0, 0, 0, 0.3);
            border-radius: 4px;
            border: 1px solid {T.border};
        """)
        
        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            scaled = pixmap.scaled(
                self.MINI_SIZE - 4, self.MINI_SIZE - 4,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.thumb_label.setPixmap(scaled)
        
        layout.addWidget(self.thumb_label)
        
        # 页码
        page_label = QLabel(f"P{self.index + 1}")
        page_label.setAlignment(Qt.AlignCenter)
        page_label.setStyleSheet(f"color: {T.text_tertiary}; font-size: 10px;")
        layout.addWidget(page_label)
        
        self.setStyleSheet(f"""
            MiniThumbnail {{
                background: transparent;
                border-radius: 4px;
            }}
            MiniThumbnail:hover {{
                background: {T.bg_hover};
            }}
        """)


# ═══════════════════════════════════════════════════════════
# 分组卡片
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 分组卡片
# ═══════════════════════════════════════════════════════════

class GroupCard(QFrame):
    """分组卡片 - 显示一个分组的所有页面"""
    
    deleted = Signal(int)           # 删除分组
    page_removed = Signal(int, int) # (group_id, page_index)
    order_changed = Signal(int, list)  # (group_id, new_order)
    move_up = Signal(int)           # 上移分组
    move_down = Signal(int)         # 下移分组
    
    def __init__(self, group_id: int, color: str, pages: List[dict], parent=None):
        super().__init__(parent)
        self.group_id = group_id
        self.color = color
        self.pages = pages  # [{'index': 0, 'path': '...'}, ...]
        
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)
        self._setup_ui()
        
    def _setup_ui(self):
        self.setStyleSheet(f"""
            GroupCard {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid {self.color};
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        
        # 标题栏
        header = QHBoxLayout()
        header.setSpacing(8)
        
        # 颜色标记
        color_dot = QLabel("●")
        color_dot.setStyleSheet(f"color: {self.color}; font-size: 14px; background: transparent; border: none;")
        header.addWidget(color_dot)
        
        title = QLabel(f"分组 {self.group_id + 1}")
        title.setStyleSheet(f"color: {T.text_primary}; font-size: 13px; font-weight: bold; background: transparent; border: none;")
        header.addWidget(title)
        
        page_count = QLabel(f"({len(self.pages)} 页)")
        page_count.setStyleSheet(f"color: {T.text_tertiary}; font-size: 12px; background: transparent; border: none;")
        header.addWidget(page_count)
        
        header.addStretch()
        
        # 删除按钮
        btn_delete = QPushButton("×")
        btn_delete.setFixedSize(24, 24)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 12px;
                color: {T.text_tertiary};
                font-size: 18px;
                line-height: 18px;
                padding-bottom: 2px;
            }}
            QPushButton:hover {{
                background: rgba(239, 68, 68, 0.2);
                color: {T.danger};
            }}
        """)
        btn_delete.clicked.connect(lambda: self.deleted.emit(self.group_id))
        header.addWidget(btn_delete)
        
        layout.addLayout(header)
        
        # 页面缩略图区域
        pages_widget = QWidget()
        pages_widget.setStyleSheet("background: transparent; border: none;")
        pages_layout = QHBoxLayout(pages_widget)
        pages_layout.setContentsMargins(0, 0, 0, 0)
        pages_layout.setSpacing(6)
        
        for page in self.pages:
            mini = MiniThumbnail(page['index'], page['path'])
            pages_layout.addWidget(mini)
        
        pages_layout.addStretch()
        layout.addWidget(pages_widget)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-page-index'):
            event.acceptProposedAction()
            self.setStyleSheet(f"""
                GroupCard {{
                    background: rgba(34, 197, 94, 0.1);
                    border: 2px dashed {self.color};
                    border-radius: 12px;
                }}
            """)
            
    def dragLeaveEvent(self, event):
        self.setStyleSheet(f"""
            GroupCard {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid {self.color};
                border-radius: 12px;
            }}
        """)
        
    def dropEvent(self, event):
        data = event.mimeData().data('application/x-page-index')
        page_index = int(bytes(data).decode())
        # 发出信号让父组件处理
        event.acceptProposedAction()
        self.dragLeaveEvent(event)


# ═══════════════════════════════════════════════════════════
# 分组管理面板
# ═══════════════════════════════════════════════════════════

class GroupManagerPanel(QWidget):
    """分组管理面板 - 管理所有分组"""
    
    groups_changed = Signal(list)  # 分组变化
    
    GROUP_COLORS = [
        "#FF6B6B", "#4ECDC4", "#FFE66D", "#95E1D3",
        "#F38181", "#AA96DA", "#81B1FF", "#FCBAD3",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.groups: List[dict] = []  # [{'id': 0, 'pages': [...], 'color': '#...'}, ...]
        self.next_group_id = 0
        self.all_pages = {}  # {index: path}
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 标题栏
        header = QHBoxLayout()
        header.setSpacing(12)
        
        icon = QLabel("📦")
        icon.setStyleSheet("font-size: 16px; background: transparent;")
        header.addWidget(icon)
        
        self.group_title_label = QLabel(tr("group_manager"))
        title = self.group_title_label
        title.setStyleSheet(f"color: {T.text_primary}; font-size: 15px; font-weight: bold; background: transparent;")
        header.addWidget(title)
        
        header.addStretch()
        
        layout.addLayout(header)
        
        # 分组卡片滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)
        scroll.setMaximumHeight(400)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: rgba(0, 0, 0, 0.2);
                border: 1px solid {T.border};
                border-radius: 12px;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(255, 255, 255, 0.2);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(12, 12, 12, 12)
        self.cards_layout.setSpacing(12)
        
        # 空状态提示
        self.empty_hint = QLabel(tr("empty_group_hint"))
        self.empty_hint.setAlignment(Qt.AlignCenter)
        self.empty_hint.setStyleSheet(f"color: {T.text_tertiary}; font-size: 12px; padding: 20px; background: transparent;")
        self.cards_layout.addWidget(self.empty_hint)
        
        self.cards_layout.addStretch()
        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)
        
    def set_pages(self, pages: dict):
        """设置所有页面 {index: path}"""
        self.all_pages = pages
        
    def add_group(self, page_indices: List[int]) -> int:
        """添加新分组，返回分组ID"""
        if len(page_indices) < 2:
            return -1
            
        group_id = self.next_group_id
        self.next_group_id += 1
        
        color = self.GROUP_COLORS[group_id % len(self.GROUP_COLORS)]
        pages = [{'index': idx, 'path': self.all_pages.get(idx, '')} for idx in page_indices]
        
        group = {'id': group_id, 'pages': pages, 'color': color}
        self.groups.append(group)
        
        self._refresh_cards()
        self.groups_changed.emit(self.get_groups_list())
        return group_id
        
    def remove_group(self, group_id: int):
        """删除分组"""
        self.groups = [g for g in self.groups if g['id'] != group_id]
        self._refresh_cards()
        self.groups_changed.emit(self.get_groups_list())
        
    def clear_groups(self):
        """清除所有分组"""
        self.groups.clear()
        self.next_group_id = 0
        self._refresh_cards()
        self.groups_changed.emit([])
        
    def get_groups_list(self) -> List[List[int]]:
        """获取分组列表 [[0,1,2], [3,4], ...]"""
        return [[p['index'] for p in g['pages']] for g in self.groups]
        
    def get_group_color(self, group_id: int) -> str:
        """获取分组颜色"""
        for g in self.groups:
            if g['id'] == group_id:
                return g['color']
        return None
        
    def _refresh_cards(self):
        """刷新分组卡片显示"""
        # 清除旧卡片
        while self.cards_layout.count() > 0:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.groups:
            self.empty_hint = QLabel(tr("empty_group_hint"))
            self.empty_hint.setAlignment(Qt.AlignCenter)
            self.empty_hint.setStyleSheet(f"color: {T.text_tertiary}; font-size: 12px; padding: 20px;")
            self.cards_layout.addWidget(self.empty_hint)
        else:
            for group in self.groups:
                card = GroupCard(group['id'], group['color'], group['pages'])
                card.deleted.connect(self.remove_group)
                card.move_up.connect(self._move_group_up)
                card.move_down.connect(self._move_group_down)
                self.cards_layout.addWidget(card)
        
        self.cards_layout.addStretch()
    
    def _move_group_up(self, group_id: int):
        """上移分组"""
        for i, g in enumerate(self.groups):
            if g['id'] == group_id:
                if i > 0:
                    self.groups[i], self.groups[i-1] = self.groups[i-1], self.groups[i]
                    self._refresh_cards()
                    self.groups_changed.emit(self.get_groups_list())
                break
    
    def _move_group_down(self, group_id: int):
        """下移分组"""
        for i, g in enumerate(self.groups):
            if g['id'] == group_id:
                if i < len(self.groups) - 1:
                    self.groups[i], self.groups[i+1] = self.groups[i+1], self.groups[i]
                    self._refresh_cards()
                    self.groups_changed.emit(self.get_groups_list())
                break
    
    def update_language(self):
        """更新界面语言"""
        # 更新标题
        if hasattr(self, 'group_title_label'):
            self.group_title_label.setText(tr("group_manager"))
        
        # 更新空状态提示
        if hasattr(self, 'empty_hint'):
            self.empty_hint.setText(tr("empty_group_hint"))
        
        # 刷新卡片
        self._refresh_cards()


# ═══════════════════════════════════════════════════════════
# 页面缩略图组件
# ═══════════════════════════════════════════════════════════

class PageThumbnail(QFrame):
    """单个页面缩略图组件"""
    
    toggled = Signal(int, bool)  # (page_index, checked)
    clicked = Signal(int)        # (page_index)
    double_clicked = Signal(int, str)  # (page_index, image_path) 双击打开大图
    
    THUMB_SIZE = 100
    
    # 分组颜色列表
    GROUP_COLORS = [
        "#FF6B6B",  # 红
        "#4ECDC4",  # 青
        "#FFE66D",  # 黄
        "#95E1D3",  # 绿
        "#F38181",  # 粉
        "#AA96DA",  # 紫
        "#81B1FF",  # 蓝
        "#FCBAD3",  # 浅粉
    ]
    
    def __init__(self, index: int, image_path: str, parent=None):
        super().__init__(parent)
        self.index = index
        self.image_path = image_path
        self._checked = True
        self._selected = False
        self._hover = False
        self._group_id = -1  # -1 表示未分组
        
        self.setFixedSize(self.THUMB_SIZE + 20, self.THUMB_SIZE + 40)
        self.setCursor(Qt.PointingHandCursor)
        self.setAcceptDrops(True)
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)
        
        # 缩略图
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(self.THUMB_SIZE, self.THUMB_SIZE)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setStyleSheet(f"""
            background: rgba(0, 0, 0, 0.3);
            border-radius: {T.radius_s}px;
            border: 1px solid {T.border};
        """)
        
        # 加载缩略图
        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            scaled = pixmap.scaled(
                self.THUMB_SIZE - 4, self.THUMB_SIZE - 4,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.thumb_label.setPixmap(scaled)
        
        layout.addWidget(self.thumb_label)
        
        # 底部：复选框 + 页码
        bottom = QHBoxLayout()
        bottom.setSpacing(4)
        
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)
        self.checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid {T.border};
                background: rgba(0, 0, 0, 0.2);
            }}
            QCheckBox::indicator:checked {{
                background: {T.accent};
                border-color: {T.accent};
            }}
        """)
        self.checkbox.toggled.connect(self._on_toggle)
        bottom.addWidget(self.checkbox)
        
        self.page_label = QLabel(tr("page_n", self.index + 1))
        self.page_label.setStyleSheet(f"""
            color: {T.text_secondary};
            font-size: 11px;
            background: transparent;
        """)
        bottom.addWidget(self.page_label)
        bottom.addStretch()
        
        layout.addLayout(bottom)
        
    def _on_toggle(self, checked: bool):
        self._checked = checked
        self._update_style()
        self.toggled.emit(self.index, checked)
        
    def set_checked(self, checked: bool):
        self.checkbox.setChecked(checked)
        
    def is_checked(self) -> bool:
        return self._checked
    
    def set_selected(self, selected: bool):
        self._selected = selected
        self._update_style()
        
    def is_selected(self) -> bool:
        return self._selected
    
    def set_group(self, group_id: int):
        """设置分组ID"""
        self._group_id = group_id
        self._update_style()
        
    def get_group(self) -> int:
        """获取分组ID，-1表示未分组"""
        return self._group_id
    
    def get_group_color(self) -> str:
        """获取分组颜色"""
        if self._group_id >= 0:
            return self.GROUP_COLORS[self._group_id % len(self.GROUP_COLORS)]
        return None
        
    def _update_style(self):
        # 确定边框颜色：分组 > 选中 > 悬停 > 默认
        if self._group_id >= 0:
            border_color = self.GROUP_COLORS[self._group_id % len(self.GROUP_COLORS)]
            border_width = 3
        elif self._selected:
            border_color = T.accent
            border_width = 2
        elif self._hover:
            border_color = T.border
            border_width = 2
        else:
            border_color = T.border
            border_width = 1
            
        # 背景色
        if self._selected:
            bg = T.bg_selected
        elif self._hover:
            bg = T.bg_hover
        else:
            bg = "transparent"
            
        opacity = "1.0" if self._checked else "0.4"
        
        self.setStyleSheet(f"""
            PageThumbnail {{
                background: {bg};
                border: {border_width}px solid {border_color};
                border-radius: {T.radius_m}px;
            }}
        """)
        self.thumb_label.setStyleSheet(f"""
            background: rgba(0, 0, 0, 0.3);
            border-radius: {T.radius_s}px;
            border: 1px solid {T.border};
            opacity: {opacity};
        """)
        
    def enterEvent(self, event):
        self._hover = True
        self._update_style()
        
    def leaveEvent(self, event):
        self._hover = False
        self._update_style()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        """双击打开大图"""
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.index, self.image_path)
        super().mouseDoubleClickEvent(event)


# ═══════════════════════════════════════════════════════════
# 页面预览面板
# ═══════════════════════════════════════════════════════════

class PagePreviewPanel(QWidget):
    """页面预览面板 - 显示所有页面缩略图"""
    
    # 信号
    page_toggled = Signal(int, bool)           # 页面启用/禁用
    page_order_changed = Signal(list)          # 页面顺序改变
    selection_changed = Signal(list)           # 选中项改变
    groups_changed = Signal(list)              # 分组改变
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thumbnails: List[PageThumbnail] = []
        self.page_order: List[int] = []        # 原始索引的顺序
        self.selected_indices: List[int] = []  # 当前选中的索引
        self.custom_groups: List[List[int]] = []  # 自定义分组列表
        self.next_group_id = 0                 # 下一个分组ID
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(T.space_m)
        
        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.setSpacing(T.space_s)
        
        self.btn_select_all = QPushButton(tr("btn_select_all"))
        self.btn_select_all.setFixedHeight(28)
        self.btn_select_all.setCursor(Qt.PointingHandCursor)
        self.btn_select_all.setStyleSheet(self._button_style())
        self.btn_select_all.clicked.connect(self._select_all)
        toolbar.addWidget(self.btn_select_all)
        
        self.btn_deselect_all = QPushButton(tr("btn_deselect_all"))
        self.btn_deselect_all.setFixedHeight(28)
        self.btn_deselect_all.setCursor(Qt.PointingHandCursor)
        self.btn_deselect_all.setStyleSheet(self._button_style())
        self.btn_deselect_all.clicked.connect(self._deselect_all)
        toolbar.addWidget(self.btn_deselect_all)
        
        # 分组操作按钮
        toolbar.addSpacing(20)
        
        self.btn_create_group = QPushButton("🔗 " + tr("btn_create_group"))
        self.btn_create_group.setFixedHeight(28)
        self.btn_create_group.setCursor(Qt.PointingHandCursor)
        self.btn_create_group.setStyleSheet(self._group_button_style())
        self.btn_create_group.clicked.connect(self._create_group_from_selection)
        self.btn_create_group.setToolTip("将选中的页面创建为一个分组 (Ctrl+点击多选)")
        toolbar.addWidget(self.btn_create_group)
        
        self.btn_clear_groups = QPushButton("🗑️ " + tr("btn_clear_groups"))
        self.btn_clear_groups.setFixedHeight(28)
        self.btn_clear_groups.setCursor(Qt.PointingHandCursor)
        self.btn_clear_groups.setStyleSheet(self._button_style())
        self.btn_clear_groups.clicked.connect(self._clear_all_groups)
        toolbar.addWidget(self.btn_clear_groups)
        
        toolbar.addStretch()
        
        self.count_label = QLabel(tr("total_pages", 0))
        self.count_label.setStyleSheet(f"color: {T.text_tertiary}; font-size: 12px;")
        toolbar.addWidget(self.count_label)
        
        layout.addLayout(toolbar)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: rgba(0, 0, 0, 0.2);
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255, 255, 255, 0.15);
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(T.space_s, T.space_s, T.space_s, T.space_s)
        self.grid_layout.setSpacing(T.space_m)
        
        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll, 1)
        
    def _button_style(self):
        return f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid {T.border};
                border-radius: 6px;
                color: {T.text_secondary};
                padding: 4px 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.1);
                border-color: {T.accent};
                color: {T.text_primary};
            }}
            QPushButton:pressed {{
                background: {T.bg_selected};
            }}
        """
        
    def _group_button_style(self):
        return f"""
            QPushButton {{
                background: rgba(34, 197, 94, 0.1);
                border: 1px solid #22C55E;
                border-radius: 6px;
                color: #22C55E;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(34, 197, 94, 0.2);
            }}
            QPushButton:pressed {{
                background: rgba(34, 197, 94, 0.3);
            }}
        """

        
    def _create_group_from_selection(self):
        """从当前选中的页面创建分组"""
        if len(self.selected_indices) < 2:
            return  # 至少需要2个页面才能创建分组
            
        # 检查是否有已分组的页面
        for idx in self.selected_indices:
            thumb = self._get_thumbnail_by_index(idx)
            if thumb and thumb.get_group() >= 0:
                # 先从旧分组移除
                self._remove_from_group(idx)
        
        # 创建新分组
        group_id = self.next_group_id
        self.next_group_id += 1
        
        # 将选中的页面加入分组
        group_pages = sorted(self.selected_indices)
        self.custom_groups.append(group_pages.copy())
        
        for idx in group_pages:
            thumb = self._get_thumbnail_by_index(idx)
            if thumb:
                thumb.set_group(group_id)
        
        # 清除选中状态
        self.selected_indices.clear()
        for thumb in self.thumbnails:
            thumb.set_selected(False)
        
        self.groups_changed.emit(self.get_custom_groups())
        
    def _remove_from_group(self, page_index: int):
        """从分组中移除页面"""
        thumb = self._get_thumbnail_by_index(page_index)
        if not thumb:
            return
            
        group_id = thumb.get_group()
        if group_id < 0:
            return
            
        thumb.set_group(-1)
        
        # 更新分组列表
        for i, group in enumerate(self.custom_groups):
            if page_index in group:
                group.remove(page_index)
                if len(group) < 2:
                    # 分组少于2个页面，解散
                    for idx in group:
                        t = self._get_thumbnail_by_index(idx)
                        if t:
                            t.set_group(-1)
                    self.custom_groups.pop(i)
                break
                
        self.groups_changed.emit(self.get_custom_groups())
        
    def _clear_all_groups(self):
        """清除所有分组"""
        for thumb in self.thumbnails:
            thumb.set_group(-1)
        self.custom_groups.clear()
        self.next_group_id = 0
        self.groups_changed.emit([])
        
    def _get_thumbnail_by_index(self, index: int) -> PageThumbnail:
        """根据页面索引获取缩略图"""
        for thumb in self.thumbnails:
            if thumb.index == index:
                return thumb
        return None
        
    def get_custom_groups(self) -> List[List[int]]:
        """获取所有自定义分组"""
        return [g.copy() for g in self.custom_groups if len(g) >= 2]
        
    def load_pages(self, image_paths: List[str]):
        """加载页面图片"""
        # 清除旧的缩略图
        self.clear()
        
        self.page_order = list(range(len(image_paths)))
        
        cols = 4  # 每行4个
        for i, path in enumerate(image_paths):
            thumb = PageThumbnail(i, path)
            thumb.toggled.connect(self._on_page_toggled)
            thumb.clicked.connect(self._on_page_clicked)
            thumb.double_clicked.connect(self._on_page_double_clicked)
            
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(thumb, row, col)
            self.thumbnails.append(thumb)
            
        self.count_label.setText(f"共 {len(image_paths)} 页")
        
    def clear(self):
        """清除所有缩略图"""
        for thumb in self.thumbnails:
            thumb.deleteLater()
        self.thumbnails.clear()
        self.page_order.clear()
        self.selected_indices.clear()
        
        # 重要：同时清除分组状态，确保每个PDF的分组独立
        self.custom_groups.clear()
        self.next_group_id = 0
        
        # 清除布局中的所有项
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self.count_label.setText("共 0 页")
        
    def _on_page_toggled(self, index: int, checked: bool):
        self.page_toggled.emit(index, checked)
        
    def _on_page_clicked(self, index: int):
        """处理页面点击 - 支持多选"""
        modifiers = QApplication.keyboardModifiers()
        
        if modifiers & Qt.ControlModifier:
            # Ctrl+点击：切换选中状态
            if index in self.selected_indices:
                self.selected_indices.remove(index)
            else:
                self.selected_indices.append(index)
        elif modifiers & Qt.ShiftModifier:
            # Shift+点击：范围选择
            if self.selected_indices:
                start = self.selected_indices[-1]
                end = index
                if start > end:
                    start, end = end, start
                for i in range(start, end + 1):
                    if i not in self.selected_indices:
                        self.selected_indices.append(i)
            else:
                self.selected_indices = [index]
        else:
            # 普通点击：单选
            self.selected_indices = [index]
            
        # 更新视觉状态
        for thumb in self.thumbnails:
            thumb.set_selected(thumb.index in self.selected_indices)
            
        self.selection_changed.emit(self.selected_indices.copy())
        
    def _select_all(self):
        """全选所有页面（启用）"""
        for thumb in self.thumbnails:
            thumb.set_checked(True)
            
    def _deselect_all(self):
        """取消全选（禁用所有）"""
        for thumb in self.thumbnails:
            thumb.set_checked(False)
            
    def get_enabled_pages(self) -> List[int]:
        """获取所有启用的页面索引"""
        return [thumb.index for thumb in self.thumbnails if thumb.is_checked()]
    
    def get_page_enabled_list(self) -> List[bool]:
        """获取所有页面的启用状态列表"""
        return [thumb.is_checked() for thumb in self.thumbnails]
    
    def get_page_order(self) -> List[int]:
        """获取当前页面顺序"""
        return self.page_order.copy()
    
    def get_selected_indices(self) -> List[int]:
        """获取当前选中的页面索引"""
        return self.selected_indices.copy()
        
    def _on_page_double_clicked(self, index: int, image_path: str):
        """双击打开大图查看器"""
        dialog = ImageViewerDialog(image_path, index, self)
        dialog.exec()
    
    def update_language(self):
        """更新界面语言"""
        # 更新按钮
        if hasattr(self, 'btn_select_all'):
            self.btn_select_all.setText(tr("btn_select_all"))
        if hasattr(self, 'btn_deselect_all'):
            self.btn_deselect_all.setText(tr("btn_deselect_all"))
        if hasattr(self, 'btn_create_group'):
            self.btn_create_group.setText("🔗 " + tr("btn_create_group"))
        if hasattr(self, 'btn_clear_groups'):
            self.btn_clear_groups.setText("🗑️ " + tr("btn_clear_groups"))
        
        # 更新页数标签
        if hasattr(self, 'count_label'):
            count = len(self.thumbnails)
            self.count_label.setText(tr("total_pages", count))
        
        # 更新缩略图页码
        for thumb in self.thumbnails:
            if hasattr(thumb, 'page_label'):
                thumb.page_label.setText(tr("page_n", thumb.index + 1))


# ═══════════════════════════════════════════════════════════
# 批次顺序管理弹窗
# ═══════════════════════════════════════════════════════════

class BatchOrderItem(QFrame):
    """批次项目 - 显示一个批次（分组或单页）"""
    
    def __init__(self, batch_type: str, pages: list, page_images: dict, parent=None):
        """
        Args:
            batch_type: "group" 或 "page"
            pages: 页面索引列表
            page_images: {index: image_path} 映射
        """
        super().__init__(parent)
        self.batch_type = batch_type
        self.pages = pages
        self.page_images = page_images
        
        self.setFixedHeight(60)
        self._setup_ui()
        
    def _setup_ui(self):
        self.setStyleSheet(f"""
            BatchOrderItem {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }}
            BatchOrderItem:hover {{
                background: rgba(255, 255, 255, 0.08);
                border-color: {T.accent};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # 图标
        icon = QLabel("📁" if self.batch_type == "group" else "📄")
        icon.setStyleSheet("font-size: 20px; background: transparent;")
        layout.addWidget(icon)
        
        # 文本描述
        if self.batch_type == "group":
            page_nums = ", ".join([str(p + 1) for p in sorted(self.pages)])
            text = tr("batch_group", len(self.pages), page_nums)
        else:
            text = tr("batch_page", self.pages[0] + 1)
        
        label = QLabel(text)
        label.setStyleSheet(f"color: {T.text_primary}; font-size: 14px; background: transparent;")
        layout.addWidget(label)
        
        layout.addStretch()
        
        # 缩略图预览
        for idx in self.pages[:3]:  # 最多显示3个缩略图
            if idx in self.page_images:
                thumb = QLabel()
                thumb.setFixedSize(40, 40)
                pixmap = QPixmap(self.page_images[idx])
                if not pixmap.isNull():
                    scaled = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    thumb.setPixmap(scaled)
                thumb.setStyleSheet("border: 1px solid rgba(255,255,255,0.2); border-radius: 4px;")
                layout.addWidget(thumb)
        
        if len(self.pages) > 3:
            more = QLabel(f"+{len(self.pages) - 3}")
            more.setStyleSheet(f"color: {T.text_secondary}; font-size: 12px; background: transparent;")
            layout.addWidget(more)


class BatchOrderDialog(QDialog):
    """批次顺序管理弹窗 - 调整分组和页面的输入顺序"""
    
    order_confirmed = Signal(list)  # 确认后发出新顺序
    
    def __init__(self, page_groups: list, page_enabled: list, page_images: dict, parent=None):
        """
        Args:
            page_groups: [[0, 1, 2], [5, 6]] 分组列表
            page_enabled: [True, True, False, ...] 页面启用状态
            page_images: {0: "path/to/img0.png", ...} 页面图片路径
        """
        super().__init__(parent)
        self.page_groups = [g.copy() for g in page_groups]
        self.page_enabled = page_enabled.copy()
        self.page_images = page_images.copy()
        
        # 构建批次列表
        self.batches = []  # [{"type": "group"/"page", "pages": [...]}]
        self._build_batches()
        
        self.setWindowTitle(tr("batch_order_title"))
        self.setMinimumSize(500, 400)
        self.resize(600, 500)
        self.setModal(True)
        
        self._setup_ui()
        self._refresh_list()
        
    def _build_batches(self):
        """根据分组和启用状态构建批次列表"""
        self.batches.clear()
        
        enabled_indices = [i for i, enabled in enumerate(self.page_enabled) if enabled]
        used_indices = set()
        
        # 添加分组批次
        batch_with_order = []
        for group in self.page_groups:
            valid_indices = [idx for idx in group if idx in enabled_indices]
            if valid_indices:
                min_page = min(valid_indices)
                batch_with_order.append((min_page, {"type": "group", "pages": valid_indices}))
                used_indices.update(valid_indices)
        
        # 添加未分组页面
        for idx in enabled_indices:
            if idx not in used_indices:
                batch_with_order.append((idx, {"type": "page", "pages": [idx]}))
        
        # 按默认页码顺序排序
        batch_with_order.sort(key=lambda x: x[0])
        self.batches = [batch for _, batch in batch_with_order]
        
    def _setup_ui(self):
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0D0D18, stop:0.6 #1A1A2E, stop:1 #16213E);
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 标题
        self.title_label = QLabel("⇅ " + tr("batch_order_title"))
        title = self.title_label
        title.setStyleSheet(f"color: {T.text_primary}; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # 说明文字
        self.hint_label = QLabel(tr("batch_order_hint"))
        hint = self.hint_label
        hint.setStyleSheet(f"color: {T.text_secondary}; font-size: 13px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        
        # 主内容区
        content = QHBoxLayout()
        content.setSpacing(16)
        
        # 左侧列表
        self.batch_list = QListWidget()
        self.batch_list.setStyleSheet(f"""
            QListWidget {{
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 8px;
            }}
            QListWidget::item {{
                background: transparent;
                border: none;
                padding: 4px;
            }}
            QListWidget::item:selected {{
                background: rgba(59, 130, 246, 0.3);
                border-radius: 8px;
            }}
        """)
        self.batch_list.setDragDropMode(QListWidget.InternalMove)
        # 监听拖拽完成后同步 batches 数据
        self.batch_list.model().rowsMoved.connect(self._on_rows_moved)
        content.addWidget(self.batch_list, 1)
        
        # 右侧按钮
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)
        
        btn_style = f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                color: {T.text_primary};
                padding: 10px 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.15);
                border-color: {T.accent};
            }}
            QPushButton:pressed {{
                background: rgba(59, 130, 246, 0.3);
            }}
        """
        
        self.btn_top = QPushButton("⬆ " + tr("btn_to_top"))
        self.btn_top.setStyleSheet(btn_style)
        self.btn_top.clicked.connect(self._move_to_top)
        btn_layout.addWidget(self.btn_top)
        
        self.btn_up = QPushButton("↑ " + tr("btn_move_up"))
        self.btn_up.setStyleSheet(btn_style)
        self.btn_up.clicked.connect(self._move_up)
        btn_layout.addWidget(self.btn_up)
        
        self.btn_down = QPushButton("↓ " + tr("btn_move_down"))
        self.btn_down.setStyleSheet(btn_style)
        self.btn_down.clicked.connect(self._move_down)
        btn_layout.addWidget(self.btn_down)
        
        self.btn_bottom = QPushButton("⬇ " + tr("btn_to_bottom"))
        self.btn_bottom.setStyleSheet(btn_style)
        self.btn_bottom.clicked.connect(self._move_to_bottom)
        btn_layout.addWidget(self.btn_bottom)
        
        btn_layout.addStretch()
        
        self.btn_reset = QPushButton("🔄 " + tr("btn_reset"))
        self.btn_reset.setStyleSheet(btn_style)
        self.btn_reset.clicked.connect(self._reset_order)
        btn_layout.addWidget(self.btn_reset)
        
        content.addLayout(btn_layout)
        layout.addLayout(content, 1)
        
        # 底部按钮
        footer = QHBoxLayout()
        footer.addStretch()
        
        self.btn_cancel = QPushButton(tr("btn_cancel"))
        self.btn_cancel.setStyleSheet(btn_style)
        self.btn_cancel.clicked.connect(self.reject)
        footer.addWidget(self.btn_cancel)
        
        self.btn_confirm = QPushButton(tr("btn_confirm"))
        self.btn_confirm.setStyleSheet(f"""
            QPushButton {{
                background: {T.accent};
                border: none;
                border-radius: 8px;
                color: white;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {T.accent_light};
            }}
        """)
        self.btn_confirm.clicked.connect(self._confirm)
        footer.addWidget(self.btn_confirm)
        
        layout.addLayout(footer)
        
    def _refresh_list(self):
        """刷新列表显示"""
        print(f"[DEBUG] BatchOrderDialog._refresh_list: batches count = {len(self.batches)}")
        self.batch_list.clear()
        
        for batch in self.batches:
            item = QListWidgetItem()
            widget = BatchOrderItem(batch["type"], batch["pages"], self.page_images)
            item.setSizeHint(widget.sizeHint())
            self.batch_list.addItem(item)
            self.batch_list.setItemWidget(item, widget)
        print(f"[DEBUG] BatchOrderDialog._refresh_list: list items = {self.batch_list.count()}")
            
    def _on_rows_moved(self, parent, start, end, destination, row):
        """拖拽完成后同步 batches 数据"""
        print(f"[DEBUG] _on_rows_moved: start={start}, end={end}, row={row}")
        # 从列表 UI 中获取新顺序
        new_batches = []
        for i in range(self.batch_list.count()):
            widget = self.batch_list.itemWidget(self.batch_list.item(i))
            if widget:
                # 根据 widget 的数据重建 batch
                new_batches.append({
                    "type": widget.batch_type,
                    "pages": widget.pages
                })
        self.batches = new_batches
        print(f"[DEBUG] _on_rows_moved: batches 已同步，count = {len(self.batches)}")
            
    def _get_current_row(self) -> int:
        return self.batch_list.currentRow()
        
    def _move_up(self):
        row = self._get_current_row()
        if row > 0:
            self.batches[row], self.batches[row-1] = self.batches[row-1], self.batches[row]
            self._refresh_list()
            self.batch_list.setCurrentRow(row - 1)
            
    def _move_down(self):
        row = self._get_current_row()
        if row >= 0 and row < len(self.batches) - 1:
            self.batches[row], self.batches[row+1] = self.batches[row+1], self.batches[row]
            self._refresh_list()
            self.batch_list.setCurrentRow(row + 1)
            
    def _move_to_top(self):
        row = self._get_current_row()
        if row > 0:
            batch = self.batches.pop(row)
            self.batches.insert(0, batch)
            self._refresh_list()
            self.batch_list.setCurrentRow(0)
            
    def _move_to_bottom(self):
        row = self._get_current_row()
        if row >= 0 and row < len(self.batches) - 1:
            batch = self.batches.pop(row)
            self.batches.append(batch)
            self._refresh_list()
            self.batch_list.setCurrentRow(len(self.batches) - 1)
            
    def _reset_order(self):
        """重置为默认顺序"""
        self._build_batches()
        self._refresh_list()
        
    def _confirm(self):
        """确认顺序"""
        self.order_confirmed.emit(self.batches)
        self.accept()
        
    def get_batches(self) -> list:
        """获取当前批次顺序"""
        return self.batches
        
    def update_language(self):
        """更新界面语言"""
        self.setWindowTitle(tr("batch_order_title"))
        if hasattr(self, 'title_label'):
            self.title_label.setText("⇅ " + tr("batch_order_title"))
        if hasattr(self, 'hint_label'):
            self.hint_label.setText(tr("batch_order_hint"))
        if hasattr(self, 'btn_top'):
            self.btn_top.setText("⬆ " + tr("btn_to_top"))
        if hasattr(self, 'btn_up'):
            self.btn_up.setText("↑ " + tr("btn_move_up"))
        if hasattr(self, 'btn_down'):
            self.btn_down.setText("↓ " + tr("btn_move_down"))
        if hasattr(self, 'btn_bottom'):
            self.btn_bottom.setText("⬇ " + tr("btn_to_bottom"))
        if hasattr(self, 'btn_reset'):
            self.btn_reset.setText("🔄 " + tr("btn_reset"))
        if hasattr(self, 'btn_cancel'):
            self.btn_cancel.setText(tr("btn_cancel"))
        if hasattr(self, 'btn_confirm'):
            self.btn_confirm.setText(tr("btn_confirm"))


# ═══════════════════════════════════════════════════════════
# 页面预览弹窗
# ═══════════════════════════════════════════════════════════

class PagePreviewDialog(QDialog):
    """页面预览弹窗 - 在弹窗中显示页面预览和分组管理"""
    
    # 信号 - 转发内部组件的信号
    page_toggled = Signal(int, bool)
    group_mode_changed = Signal(str)
    pages_per_batch_changed = Signal(int)
    groups_changed = Signal(list)
    closing = Signal()  # 窗口关闭信号
    batch_order_changed = Signal(list)  # 批次顺序变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("page_preview_title"))
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        self.setModal(False)  # 非模态，允许与主窗口交互
        
        self._setup_ui()
        
    def closeEvent(self, event):
        """窗口关闭时触发保存"""
        self.closing.emit()
        super().closeEvent(event)
        
    def _setup_ui(self):
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0D0D18, stop:0.6 #1A1A2E, stop:1 #16213E);
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.space_l, T.space_l, T.space_l, T.space_l)
        layout.setSpacing(T.space_l)
        
        # 标题栏
        header = QHBoxLayout()
        self.dialog_title_label = QLabel("📄 " + tr("page_preview_title"))
        title = self.dialog_title_label
        title.setStyleSheet(f"""
            color: {T.text_primary};
            font-size: 18px;
            font-weight: bold;
        """)
        header.addWidget(title)
        header.addStretch()
        
        self.hint_label = QLabel(tr("tip_ctrl_click"))
        hint = self.hint_label
        hint.setStyleSheet(f"color: {T.text_tertiary}; font-size: 12px;")
        header.addWidget(hint)
        
        layout.addLayout(header)
        
        # 页面预览面板
        self.page_preview = PagePreviewPanel()
        self.page_preview.page_toggled.connect(self.page_toggled.emit)
        self.page_preview.groups_changed.connect(self._on_preview_groups_changed)
        self.page_preview.setMinimumHeight(350)
        layout.addWidget(self.page_preview, 1)
        
        # 分隔线
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: rgba(255, 255, 255, 0.1);")
        layout.addWidget(divider)
        
        # 分组管理面板
        self.group_manager_panel = GroupManagerPanel()
        self.group_manager_panel.groups_changed.connect(self.groups_changed.emit)
        layout.addWidget(self.group_manager_panel)
        
        # 旧版分组管理器（保持兼容性）
        self.group_manager = PageGroupManager()
        self.group_manager.group_mode_changed.connect(self.group_mode_changed.emit)
        self.group_manager.pages_per_batch_changed.connect(self.pages_per_batch_changed.emit)
        layout.addWidget(self.group_manager)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        
        # 输入顺序按钮
        self.btn_batch_order = QPushButton("⇅ " + tr("btn_batch_order"))
        btn_batch_order = self.btn_batch_order
        btn_batch_order.setFixedHeight(40)
        btn_batch_order.setCursor(Qt.PointingHandCursor)
        btn_batch_order.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 10px;
                color: {T.text_primary};
                font-size: 14px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.15);
                border-color: {T.accent};
            }}
        """)
        btn_batch_order.clicked.connect(self._open_batch_order)
        btn_layout.addWidget(btn_batch_order)
        
        btn_layout.addStretch()
        
        self.btn_close = QPushButton(tr("btn_close"))
        btn_close = self.btn_close
        btn_close.setFixedSize(100, 40)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: {T.accent};
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {T.accent_light};
            }}
        """)
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        
    def load_pages(self, image_paths: List[str]):
        """加载页面图片"""
        self.page_preview.load_pages(image_paths)
        self.group_manager.clear()
        self.group_manager.update_preview(len(image_paths))
        
        # 设置 GroupManagerPanel 的页面数据
        pages_dict = {i: path for i, path in enumerate(image_paths)}
        self.group_manager_panel.set_pages(pages_dict)
        self.group_manager_panel.clear_groups()
        
        # 重要：清除自定义批次顺序，确保每个PDF的顺序独立
        self.custom_batch_order = None
        
        # 注意：不重复连接信号（避免重复触发）
        # 页数变化时更新预览已在 __init__ 或首次加载时连接
        
    def _on_preview_groups_changed(self, groups: list):
        """当页面预览面板的分组变化时，同步到分组管理面板"""
        # 清除现有分组并重新添加
        self.group_manager_panel.clear_groups()
        
        # 从 page_preview 获取所有分组并添加到管理面板
        for group_indices in groups:
            if len(group_indices) >= 2:
                self.group_manager_panel.add_group(group_indices)
        
    def clear(self):
        """清除预览"""
        self.page_preview.clear()
        self.group_manager.clear()
        self.group_manager_panel.clear_groups()
        
    def get_enabled_pages(self) -> List[int]:
        """获取启用的页面"""
        return self.page_preview.get_enabled_pages()
        
    def get_selected_indices(self) -> List[int]:
        """获取选中的页面"""
        return self.page_preview.get_selected_indices()
        
    def add_group(self, page_indices: List[int]):
        """添加分组"""
        self.group_manager.add_group(page_indices)
        
    def get_groups(self) -> List[List[int]]:
        """获取所有分组"""
        return self.group_manager.get_groups()
        
    def get_mode(self) -> str:
        """获取分组模式"""
        return self.group_manager.get_mode()
        
    def get_pages_per_batch(self) -> int:
        """获取固定模式下的页数"""
        return self.group_manager.get_pages_per_batch()
    
    def update_language(self):
        """更新界面语言"""
        # 更新窗口标题
        self.setWindowTitle(tr("page_preview_title"))
        
        # 更新对话框标题
        if hasattr(self, 'dialog_title_label'):
            self.dialog_title_label.setText("📄 " + tr("page_preview_title"))
        
        # 更新提示
        if hasattr(self, 'hint_label'):
            self.hint_label.setText(tr("tip_ctrl_click"))
        
        # 更新关闭按钮
        if hasattr(self, 'btn_close'):
            self.btn_close.setText(tr("btn_close"))
        
        # 更新输入顺序按钮
        if hasattr(self, 'btn_batch_order'):
            self.btn_batch_order.setText("⇅ " + tr("btn_batch_order"))
        
        # 更新页面预览面板
        if hasattr(self, 'page_preview'):
            self.page_preview.update_language()
        
        # 更新分组管理面板
        if hasattr(self, 'group_manager_panel'):
            self.group_manager_panel.update_language()
        
        # 更新分组管理器
        if hasattr(self, 'group_manager'):
            self.group_manager.update_language()
            
    def _open_batch_order(self):
        """打开批次排序弹窗"""
        # 获取当前分组
        groups = self.group_manager_panel.get_groups_list()
        print(f"[DEBUG] _open_batch_order: groups = {groups}")
        
        # 获取页面启用状态
        enabled = self.page_preview.get_page_enabled_list()
        print(f"[DEBUG] _open_batch_order: enabled count = {sum(enabled)}")
        
        # 获取页面图片路径
        page_images = {i: thumb.image_path for i, thumb in enumerate(self.page_preview.thumbnails)}
        
        # 如果有已保存的批次顺序，传递给弹窗
        existing_order = getattr(self, 'custom_batch_order', None)
        print(f"[DEBUG] _open_batch_order: existing_order 有 {len(existing_order) if existing_order else 0} 批次")
        
        # 验证保存的顺序是否与当前分组结构匹配（只检查分组，不检查启用状态）
        if existing_order:
            # 检查保存的分组是否与当前分组一致
            saved_groups = [tuple(sorted(b['pages'])) for b in existing_order if b['type'] == 'group']
            current_groups = [tuple(sorted(g)) for g in groups]
            
            # 如果分组结构变化了，清除旧顺序
            groups_changed = sorted(saved_groups) != sorted(current_groups)
            
            if groups_changed:
                print(f"[DEBUG] _open_batch_order: 分组结构已变化，清除旧顺序")
                print(f"[DEBUG] saved_groups = {saved_groups}, current_groups = {current_groups}")
                existing_order = None
                self.custom_batch_order = None
        
        # 显示弹窗
        dialog = BatchOrderDialog(groups, enabled, page_images, self)
        
        # 如果有已保存的顺序且与当前分组匹配，恢复到弹窗中（过滤禁用页面）
        if existing_order:
            # 获取当前启用的页面索引
            enabled_indices = set(i for i, e in enumerate(enabled) if e)
            
            # 过滤掉禁用的页面
            filtered_order = []
            for b in existing_order:
                valid_pages = [p for p in b['pages'] if p in enabled_indices]
                if valid_pages:
                    filtered_order.append({
                        'type': b['type'] if len(valid_pages) > 1 else 'page',
                        'pages': valid_pages
                    })
            
            if filtered_order:
                dialog.batches = filtered_order
                dialog._refresh_list()
                print(f"[DEBUG] _open_batch_order: 已恢复保存的顺序到弹窗 (过滤后 {len(filtered_order)} 批次)")
        
        if dialog.exec() == QDialog.Accepted:
            # 保存自定义顺序
            self.custom_batch_order = dialog.get_batches()
            print(f"[DEBUG] _open_batch_order: 保存 custom_batch_order = {len(self.custom_batch_order)} 批次")
            # 发出顺序变化信号
            self.batch_order_changed.emit(self.custom_batch_order)


# ═══════════════════════════════════════════════════════════
# 页面分组管理器 (简化版)
# ═══════════════════════════════════════════════════════════

class PageGroupManager(QWidget):
    """页面分组管理器 - 简化版"""
    
    # 信号
    group_mode_changed = Signal(str)           # "auto" (自动分组)
    pages_per_batch_changed = Signal(int)      # 每批页数
    groups_changed = Signal(list)              # 分组列表（兼容旧接口）
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.groups: List[List[int]] = []
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(T.space_m)
        
        # 简化的分组设置
        setting_layout = QHBoxLayout()
        setting_layout.setSpacing(T.space_m)
        
        self.lbl_group_settings = QLabel("📦 " + tr("group_settings"))
        label = self.lbl_group_settings
        label.setStyleSheet(f"color: {T.text_primary}; font-size: 13px; font-weight: bold;")
        setting_layout.addWidget(label)
        
        setting_layout.addSpacing(8)
        
        self.lbl_prefix = QLabel(tr("pages_per_batch_prefix"))
        label2 = self.lbl_prefix
        label2.setStyleSheet(f"color: {T.text_secondary}; font-size: 13px;")
        setting_layout.addWidget(label2)
        
        self.pages_spin = QSpinBox()
        self.pages_spin.setRange(1, 20)
        self.pages_spin.setValue(1)
        self.pages_spin.setFixedWidth(60)
        self.pages_spin.setStyleSheet(f"""
            QSpinBox {{
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid {T.border};
                border-radius: 6px;
                color: {T.text_primary};
                padding: 4px 8px;
                font-size: 13px;
            }}
            QSpinBox:hover {{
                border-color: {T.accent};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 16px;
                border: none;
            }}
        """)
        self.pages_spin.valueChanged.connect(self._on_pages_changed)
        setting_layout.addWidget(self.pages_spin)
        
        self.lbl_suffix = QLabel(tr("pages_per_batch_suffix"))
        label3 = self.lbl_suffix
        label3.setStyleSheet(f"color: {T.text_secondary}; font-size: 13px;")
        setting_layout.addWidget(label3)
        
        setting_layout.addStretch()
        
        # 预览提示
        self.preview_label = QLabel("📋 " + tr("will_split_to", 1))
        self.preview_label.setStyleSheet(f"color: {T.text_tertiary}; font-size: 12px;")
        setting_layout.addWidget(self.preview_label)
        
        layout.addLayout(setting_layout)
        
    def _on_pages_changed(self, value: int):
        self.pages_per_batch_changed.emit(value)
        self.group_mode_changed.emit("fixed" if value > 1 else "single")
        
    def update_preview(self, total_pages: int):
        """更新预览信息"""
        if total_pages == 0:
            self.preview_label.setText("📋 " + tr("no_pages"))
            return
            
        n = self.pages_spin.value()
        num_groups = (total_pages + n - 1) // n  # 向上取整
        self.preview_label.setText("📋 " + tr("will_split_to", num_groups))
        
    # ===== 兼容旧接口 =====
    def add_group(self, page_indices: List[int]):
        """添加分组（保留兼容性）"""
        if page_indices:
            self.groups.append(page_indices.copy())
            self.groups_changed.emit(self.groups.copy())
        
    def get_groups(self) -> List[List[int]]:
        """获取所有分组"""
        return [g.copy() for g in self.groups]
    
    def get_mode(self) -> str:
        """获取当前模式"""
        return "fixed" if self.pages_spin.value() > 1 else "single"
    
    def get_pages_per_batch(self) -> int:
        """获取每批页数"""
        return self.pages_spin.value()
    
    def clear(self):
        """清除分组"""
        self.groups.clear()
        self.preview_label.setText("📋 " + tr("will_split_to", 1))
    
    def update_language(self):
        """更新界面语言"""
        # 更新分组设置标签
        if hasattr(self, 'lbl_group_settings'):
            self.lbl_group_settings.setText("📦 " + tr("group_settings"))
        if hasattr(self, 'lbl_prefix'):
            self.lbl_prefix.setText(tr("pages_per_batch_prefix"))
        if hasattr(self, 'lbl_suffix'):
            self.lbl_suffix.setText(tr("pages_per_batch_suffix"))
        
        # 更新预览标签
        n = self.pages_spin.value() if hasattr(self, 'pages_spin') else 1
        if hasattr(self, 'preview_label'):
            self.preview_label.setText("📋 " + tr("will_split_to", n))
