"""
Modern styling and theme management for the application
Dark theme only for consistent, modern appearance
"""

class ThemeManager:
    """Manages application theme (dark mode only)"""
    
    # Color palette - Modern dark theme
    COLORS = {
        'dark': {
            'bg_primary': '#0f0f0f',
            'bg_secondary': '#1a1a1a',
            'bg_tertiary': '#252525',
            'bg_card': '#1e1e1e',
            'text_primary': '#f5f5f5',
            'text_secondary': '#a3a3a3',
            'text_muted': '#737373',
            'accent': '#6366f1',
            'accent_hover': '#818cf8',
            'accent_light': '#a5b4fc',
            'success': '#22c55e',
            'success_hover': '#4ade80',
            'warning': '#eab308',
            'error': '#ef4444',
            'border': '#333333',
            'border_light': '#404040',
            'input_bg': '#262626',
            'scrollbar_bg': '#1a1a1a',
            'scrollbar_handle': '#404040',
        }
    }
    
    @classmethod
    def get_stylesheet(cls, theme='dark'):
        """Generate complete stylesheet for the application (always dark)"""
        c = cls.COLORS['dark']  # Always use dark theme
        
        return f"""
        /* Main Window */
        QMainWindow, QWidget {{
            background-color: {c['bg_primary']};
            color: {c['text_primary']};
            font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
            font-size: 13px;
        }}
        
        /* Tab Widget */
        QTabWidget::pane {{
            border: none;
            background-color: {c['bg_secondary']};
            border-radius: 0px;
        }}
        
        QTabBar::tab {{
            background-color: transparent;
            color: {c['text_muted']};
            padding: 12px 28px;
            margin: 0px;
            border: none;
            border-bottom: 2px solid transparent;
            font-weight: 500;
        }}
        
        QTabBar::tab:selected {{
            color: {c['accent']};
            border-bottom: 2px solid {c['accent']};
            font-weight: 600;
        }}
        
        QTabBar::tab:hover:!selected {{
            color: {c['text_primary']};
        }}
        
        /* Group Box - Minimal style */
        QGroupBox {{
            font-weight: 600;
            font-size: 13px;
            color: {c['text_secondary']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            margin-top: 8px;
            padding: 16px 12px 12px 12px;
            background-color: {c['bg_card']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            top: -4px;
            padding: 0 8px;
            background-color: {c['bg_card']};
            color: {c['text_secondary']};
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* Labels */
        QLabel {{
            color: {c['text_primary']};
            font-size: 13px;
            background: transparent;
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {c['accent']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            font-size: 13px;
        }}
        
        QPushButton:hover {{
            background-color: {c['accent_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {c['accent']};
        }}
        
        QPushButton:disabled {{
            background-color: {c['border']};
            color: {c['text_muted']};
        }}
        
        QPushButton[class="success"] {{
            background-color: {c['success']};
        }}
        
        QPushButton[class="success"]:hover {{
            background-color: {c['success_hover']};
        }}
        
        QPushButton[class="secondary"] {{
            background-color: transparent;
            border: 1px solid {c['border']};
            color: {c['text_primary']};
        }}
        
        QPushButton[class="secondary"]:hover {{
            background-color: {c['bg_tertiary']};
            border-color: {c['accent']};
        }}
        
        /* Input fields */
        QLineEdit, QSpinBox {{
            background-color: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px 10px;
            color: {c['text_primary']};
            font-size: 13px;
            selection-background-color: {c['accent']};
        }}
        
        QLineEdit:focus, QSpinBox:focus {{
            border-color: {c['accent']};
        }}
        
        QLineEdit:hover, QSpinBox:hover {{
            border-color: {c['border_light']};
        }}
        
        /* Combo Box */
        QComboBox {{
            background-color: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px 10px;
            color: {c['text_primary']};
            font-size: 13px;
            min-width: 120px;
        }}
        
        QComboBox:hover {{
            border-color: {c['border_light']};
        }}
        
        QComboBox:focus {{
            border-color: {c['accent']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {c['text_muted']};
            margin-right: 8px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            color: {c['text_primary']};
            selection-background-color: {c['accent']};
            padding: 4px;
        }}
        
        /* Text Edit */
        QTextEdit, QPlainTextEdit {{
            background-color: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 10px;
            color: {c['text_primary']};
            font-size: 14px;
            selection-background-color: {c['accent']};
        }}
        
        QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {c['accent']};
        }}
        
        /* Scroll Bar */
        QScrollBar:vertical {{
            background-color: transparent;
            width: 8px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {c['scrollbar_handle']};
            border-radius: 4px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {c['border_light']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        QScrollBar:horizontal {{
            background-color: transparent;
            height: 8px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {c['scrollbar_handle']};
            border-radius: 4px;
            min-width: 30px;
        }}
        
        /* Splitter */
        QSplitter::handle {{
            background-color: {c['border']};
        }}
        
        QSplitter::handle:horizontal {{
            width: 1px;
        }}
        
        QSplitter::handle:vertical {{
            height: 1px;
        }}
        
        /* Spin Box specific */
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {c['bg_tertiary']};
            border: none;
            width: 18px;
        }}
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {c['accent']};
        }}
        
        /* Scroll Area */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        /* Frame */
        QFrame {{
            background-color: transparent;
        }}
        
        /* Message Box */
        QMessageBox {{
            background-color: {c['bg_card']};
        }}
        """
    
    @classmethod
    def get_capture_button_style(cls, theme='dark'):
        """Special style for the capture button (always dark)"""
        c = cls.COLORS['dark']
        return f"""
            QPushButton {{
                background-color: {c['success']};
                color: white;
                font-size: 15px;
                font-weight: 600;
                border-radius: 8px;
                padding: 14px 28px;
            }}
            QPushButton:hover {{
                background-color: {c['success_hover']};
            }}
            QPushButton:disabled {{
                background-color: {c['border']};
                color: {c['text_muted']};
            }}
        """


def get_icon_svg(icon_name, color="#ffffff"):
    """Get SVG icon as string"""
    icons = {
        'sun': f'''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>''',
        'moon': f'''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>''',
        'capture': f'''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
            <circle cx="12" cy="13" r="4"></circle>
        </svg>''',
        'copy': f'''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>''',
        'trash': f'''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        </svg>''',
        'refresh': f'''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
        </svg>''',
        'check': f'''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
        </svg>''',
        'image': f'''<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
        </svg>''',
    }
    return icons.get(icon_name, '')
