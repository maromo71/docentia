import os
import sys
from PyQt6.QtCore import Qt, QByteArray, QRectF
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def resource_path(relative_path: str) -> str:
    """Resolve bundled asset paths in both source and frozen (PyInstaller) builds."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(BASE_DIR, relative_path)


def load_svg_icon(relative_path: str, color: str | None = None, size: int = 18) -> QIcon:
    """Render an SVG file into a crisp QIcon, optionally tinting currentColor."""
    full_path = resource_path(relative_path)
    if not os.path.exists(full_path):
        return QIcon()

    with open(full_path, "r", encoding="utf-8") as f:
        svg_text = f.read()

    if color:
        svg_text = svg_text.replace("currentColor", color)

    renderer = QSvgRenderer(QByteArray(svg_text.encode("utf-8")))
    pixmap = QPixmap(size * 2, size * 2)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter, QRectF(0, 0, size * 2, size * 2))
    painter.end()
    pixmap.setDevicePixelRatio(2.0)
    return QIcon(pixmap)


def load_svg_pixmap(relative_path: str, width: int, height: int) -> QPixmap:
    """Render an SVG illustration into a crisp high-DPI QPixmap."""
    full_path = resource_path(relative_path)
    if not os.path.exists(full_path):
        return QPixmap()

    renderer = QSvgRenderer(full_path)
    pixmap = QPixmap(width * 2, height * 2)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter, QRectF(0, 0, width * 2, height * 2))
    painter.end()
    pixmap.setDevicePixelRatio(2.0)
    return pixmap


THEME_TOKENS = {
    "dark": {
        "scene_bg": "#0f172a",
        "neutral_icon": "#e2e8f0",
        "muted_icon": "#94a3b8",
        "subtitle_color": "#94a3b8",
        "tab_text": "#ffffff",
        "tab_bgs": [
            "rgba(239, 68, 68, 0.22)",
            "rgba(234, 179, 8, 0.22)",
            "rgba(59, 130, 246, 0.22)",
        ],
        "tab_borders": [
            "rgba(239, 68, 68, 0.8)",
            "rgba(234, 179, 8, 0.8)",
            "rgba(59, 130, 246, 0.8)",
        ],
    },
    "light": {
        "scene_bg": "#e2e8f0",
        "neutral_icon": "#1e293b",
        "muted_icon": "#64748b",
        "subtitle_color": "#64748b",
        "tab_text": "#0f172a",
        "tab_bgs": [
            "rgba(239, 68, 68, 0.14)",
            "rgba(234, 179, 8, 0.18)",
            "rgba(59, 130, 246, 0.14)",
        ],
        "tab_borders": [
            "#ef4444",
            "#eab308",
            "#3b82f6",
        ],
    },
}


DARK_GLASS_QSS = """
QWidget {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}

QDialog, QMainWindow {
    background-color: #0b0f19;
}

QLabel {
    background: transparent;
}

QLabel#lbl_subtitle {
    color: #94a3b8;
    font-size: 12px;
}

QLabel#lbl_metric_value {
    font-size: 22px;
    font-weight: bold;
    color: #f8fafc;
}

QLabel#lbl_metric_title {
    font-size: 12px;
    color: #94a3b8;
}

/* Cards */
QFrame#header_card, QFrame#metric_card, QFrame#glass_card, QFrame#empty_state_card, QFrame#upload_card {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
}

QFrame#upload_card {
    border: 1px dashed rgba(59, 130, 246, 0.45);
    background-color: rgba(59, 130, 246, 0.06);
}

/* Simulated Frosted Glass Panels */
QTableWidget, QScrollArea, QTabWidget::pane {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
}

/* Table Specifics */
QTableWidget {
    gridline-color: rgba(255, 255, 255, 0.05);
    alternate-background-color: rgba(255, 255, 255, 0.02);
    selection-background-color: rgba(59, 130, 246, 0.3);
    selection-color: #ffffff;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background-color: rgba(0, 0, 0, 0.35);
    color: #94a3b8;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding: 8px 6px;
    font-weight: bold;
}
QTableCornerButton::section {
    background-color: rgba(0, 0, 0, 0.35);
}

/* Inputs */
QLineEdit, QTextEdit, QPlainTextEdit, QDateEdit, QComboBox {
    background-color: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    padding: 8px;
    color: #e2e8f0;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QDateEdit:focus, QComboBox:focus {
    border: 1px solid rgba(59, 130, 246, 0.7);
    background-color: rgba(0, 0, 0, 0.45);
}
QComboBox QAbstractItemView {
    background-color: #111827;
    color: #e2e8f0;
    selection-background-color: rgba(59, 130, 246, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.14);
}

/* Radio Buttons & Checkboxes */
QRadioButton, QCheckBox {
    spacing: 8px;
    color: #e2e8f0;
    background: transparent;
}

/* Buttons */
QPushButton {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    color: #ffffff;
    padding: 8px 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.3);
}
QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.05);
}

QPushButton#btn_theme_toggle, QPushButton#btn_ghost {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.14);
    color: #e2e8f0;
    padding: 7px 12px;
}
QPushButton#btn_theme_toggle:hover, QPushButton#btn_ghost:hover {
    background-color: rgba(255, 255, 255, 0.14);
}

/* Colored Buttons */
QPushButton#btn_green {
    background-color: rgba(16, 185, 129, 0.85);
    border: 1px solid #10b981;
    color: #ffffff;
}
QPushButton#btn_green:hover { background-color: rgba(16, 185, 129, 1.0); }

QPushButton#btn_blue {
    background-color: rgba(59, 130, 246, 0.85);
    border: 1px solid #3b82f6;
    color: #ffffff;
}
QPushButton#btn_blue:hover { background-color: rgba(59, 130, 246, 1.0); }

QPushButton#btn_red {
    background-color: rgba(239, 68, 68, 0.85);
    border: 1px solid #ef4444;
    color: #ffffff;
}
QPushButton#btn_red:hover { background-color: rgba(239, 68, 68, 1.0); }

QPushButton#btn_orange {
    background-color: rgba(249, 115, 22, 0.85);
    border: 1px solid #f97316;
    color: #ffffff;
}
QPushButton#btn_orange:hover { background-color: rgba(249, 115, 22, 1.0); }

/* Icon Buttons */
QPushButton#btn_icon_blue, QPushButton#btn_icon_orange {
    padding: 0px;
    font-size: 14px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    border-radius: 6px;
    color: #ffffff;
}
QPushButton#btn_icon_blue {
    background-color: rgba(59, 130, 246, 0.85);
    border: 1px solid #3b82f6;
}
QPushButton#btn_icon_blue:hover { background-color: rgba(59, 130, 246, 1.0); }
QPushButton#btn_icon_orange {
    background-color: rgba(249, 115, 22, 0.85);
    border: 1px solid #f97316;
}
QPushButton#btn_icon_orange:hover { background-color: rgba(249, 115, 22, 1.0); }

/* Tabs */
QTabBar::tab {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 14px;
    margin-right: 3px;
    color: #94a3b8;
}
QTabBar::tab:selected {
    color: #ffffff;
}

/* Splitter */
QSplitter::handle {
    background: rgba(255, 255, 255, 0.1);
    width: 3px;
}

/* Scrollbars */
QScrollBar:vertical, QScrollBar:horizontal {
    background: transparent;
    width: 10px;
    height: 10px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: rgba(148, 163, 184, 0.3);
    border-radius: 5px;
    min-height: 24px;
    min-width: 24px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background: rgba(148, 163, 184, 0.5);
}
QScrollBar::add-line, QScrollBar::sub-line {
    width: 0px;
    height: 0px;
}
"""


LIGHT_PAPER_QSS = """
QWidget {
    background-color: #f4f6fa;
    color: #0f172a;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}

QDialog, QMainWindow {
    background-color: #f4f6fa;
}

QLabel {
    background: transparent;
    color: #0f172a;
}

QLabel#lbl_subtitle {
    color: #64748b;
    font-size: 12px;
}

QLabel#lbl_metric_value {
    font-size: 22px;
    font-weight: bold;
    color: #0f172a;
}

QLabel#lbl_metric_title {
    font-size: 12px;
    color: #64748b;
}

/* Cards */
QFrame#header_card, QFrame#metric_card, QFrame#glass_card, QFrame#empty_state_card, QFrame#upload_card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}

QFrame#upload_card {
    border: 1px dashed #3b82f6;
    background-color: #eff6ff;
}

/* Clean Paper Panels */
QTableWidget, QScrollArea, QTabWidget::pane {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

/* Table Specifics */
QTableWidget {
    gridline-color: #f1f5f9;
    alternate-background-color: #f8fafc;
    selection-background-color: rgba(59, 130, 246, 0.16);
    selection-color: #0f172a;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    padding: 8px 6px;
    font-weight: bold;
}
QTableCornerButton::section {
    background-color: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
}

/* Inputs */
QLineEdit, QTextEdit, QPlainTextEdit, QDateEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px;
    color: #0f172a;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QDateEdit:focus, QComboBox:focus {
    border: 1px solid #3b82f6;
    background-color: #ffffff;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #0f172a;
    selection-background-color: #dbeafe;
    border: 1px solid #cbd5e1;
}

/* Radio Buttons & Checkboxes */
QRadioButton, QCheckBox {
    spacing: 8px;
    color: #0f172a;
    background: transparent;
}

/* Buttons */
QPushButton {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    color: #1e293b;
    padding: 8px 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #f1f5f9;
    border: 1px solid #94a3b8;
}
QPushButton:pressed {
    background-color: #e2e8f0;
}

QPushButton#btn_theme_toggle, QPushButton#btn_ghost {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    color: #1e293b;
    padding: 7px 12px;
}
QPushButton#btn_theme_toggle:hover, QPushButton#btn_ghost:hover {
    background-color: #f1f5f9;
    border: 1px solid #94a3b8;
}

/* Colored Buttons */
QPushButton#btn_green {
    background-color: #10b981;
    border: 1px solid #059669;
    color: #ffffff;
}
QPushButton#btn_green:hover { background-color: #059669; }

QPushButton#btn_blue {
    background-color: #3b82f6;
    border: 1px solid #2563eb;
    color: #ffffff;
}
QPushButton#btn_blue:hover { background-color: #2563eb; }

QPushButton#btn_red {
    background-color: #ef4444;
    border: 1px solid #dc2626;
    color: #ffffff;
}
QPushButton#btn_red:hover { background-color: #dc2626; }

QPushButton#btn_orange {
    background-color: #f97316;
    border: 1px solid #ea580c;
    color: #ffffff;
}
QPushButton#btn_orange:hover { background-color: #ea580c; }

/* Icon Buttons */
QPushButton#btn_icon_blue, QPushButton#btn_icon_orange {
    padding: 0px;
    font-size: 14px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    border-radius: 6px;
    color: #ffffff;
}
QPushButton#btn_icon_blue {
    background-color: #3b82f6;
    border: 1px solid #2563eb;
}
QPushButton#btn_icon_blue:hover { background-color: #2563eb; }
QPushButton#btn_icon_orange {
    background-color: #f97316;
    border: 1px solid #ea580c;
}
QPushButton#btn_icon_orange:hover { background-color: #ea580c; }

/* Tabs */
QTabBar::tab {
    background: #e2e8f0;
    border: 1px solid #cbd5e1;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 14px;
    margin-right: 3px;
    color: #475569;
}
QTabBar::tab:selected {
    color: #0f172a;
}

/* Splitter */
QSplitter::handle {
    background: #cbd5e1;
    width: 3px;
}

/* Scrollbars */
QScrollBar:vertical, QScrollBar:horizontal {
    background: transparent;
    width: 10px;
    height: 10px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: rgba(100, 116, 139, 0.35);
    border-radius: 5px;
    min-height: 24px;
    min-width: 24px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background: rgba(100, 116, 139, 0.55);
}
QScrollBar::add-line, QScrollBar::sub-line {
    width: 0px;
    height: 0px;
}
"""
