"""
Settings UI - Modern Dark Theme Design
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QComboBox, QPushButton,
                              QSpinBox, QMessageBox, QApplication,
                              QSizePolicy, QFrame, QSlider)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class OllamaTestThread(QThread):
    """Background thread for testing Ollama connection"""
    finished = pyqtSignal(bool, str, list)
    
    def __init__(self, url, model):
        super().__init__()
        self.url = url
        self.model = model
    
    def run(self):
        import requests
        try:
            response = requests.get(f"{self.url}/api/tags", timeout=5)
            if response.status_code != 200:
                self.finished.emit(False, f"HTTP {response.status_code}", [])
                return
            
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            model_exists = any(self.model in name or name in self.model for name in model_names)
            
            if not model_exists:
                self.finished.emit(False, f"Model '{self.model}' not found", model_names)
                return
            
            test_response = requests.post(
                f"{self.url}/api/generate",
                json={"model": self.model, "prompt": "Hi", "stream": False},
                timeout=30
            )
            
            if test_response.status_code == 200:
                self.finished.emit(True, "OK", model_names)
            else:
                self.finished.emit(False, f"HTTP {test_response.status_code}", model_names)
        except Exception as e:
            self.finished.emit(False, str(e)[:50], [])


class SettingCard(QFrame):
    """A modern card container for settings"""
    
    def __init__(self, title="", description="", parent=None):
        super().__init__(parent)
        self.setObjectName("settingCard")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(8)
        self.main_layout.setContentsMargins(16, 12, 16, 12)
        
        if title:
            # Header with title only (description in tooltip)
            title_label = QLabel(title)
            title_label.setObjectName("cardTitle")
            
            # Set description as tooltip if provided
            if description:
                title_label.setToolTip(description)
                # Make it clear there's a tooltip with cursor change
                title_label.setCursor(Qt.CursorShape.WhatsThisCursor)
            
            self.main_layout.addWidget(title_label)
            
            # Separator line
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setObjectName("separator")
            self.main_layout.addWidget(separator)
    
    def addRow(self, label_text, widget, hint_text=None):
        """Add a setting row with label and widget"""
        row = QHBoxLayout()
        row.setSpacing(16)
        
        # Label
        label = QLabel(label_text)
        label.setObjectName("settingLabel")
        
        # Set hint as tooltip if provided
        if hint_text:
            label.setToolTip(hint_text)
            label.setCursor(Qt.CursorShape.WhatsThisCursor)
        
        row.addWidget(label)
        row.addStretch()
        
        # Widget
        if isinstance(widget, QComboBox):
            widget.setMinimumWidth(180)
            widget.setMaximumWidth(220)
        elif isinstance(widget, QSpinBox):
            widget.setMinimumWidth(100)
        elif isinstance(widget, QLineEdit):
            widget.setMinimumWidth(220)
        
        # Also set tooltip on widget
        if hint_text:
            widget.setToolTip(hint_text)
        
        row.addWidget(widget)
        
        self.main_layout.addLayout(row)
    
    def addWidget(self, widget):
        """Add any widget to the card"""
        self.main_layout.addWidget(widget)
    
    def addLayout(self, layout):
        """Add any layout to the card"""
        self.main_layout.addLayout(layout)


class SettingsWidget(QWidget):
    """Modern Settings Panel - Dark Theme Only"""
    
    # Keep signal for compatibility but won't change theme
    theme_changed = pyqtSignal(str)
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.test_thread = None
        self._setup_styles()
        self.init_ui()
        self.load_settings()
    
    def _setup_styles(self):
        """Setup modern dark theme styles"""
        self.setStyleSheet("""
            /* Card Styling */
            #settingCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 30, 35, 0.95),
                    stop:1 rgba(25, 25, 30, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
            
            #cardTitle {
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                letter-spacing: 0.3px;
            }
            
            #separator {
                background-color: rgba(255, 255, 255, 0.06);
                max-height: 1px;
                margin: 4px 0;
            }
            
            #settingLabel {
                font-size: 14px;
                font-weight: 500;
                color: rgba(255, 255, 255, 0.9);
            }
            
            #hintLabel {
                font-size: 12px;
                color: rgba(255, 255, 255, 0.4);
                line-height: 1.3;
            }
            
            /* Input Controls */
            QComboBox {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px 14px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
            }
            
            QComboBox:hover {
                background-color: rgba(255, 255, 255, 0.08);
                border-color: rgba(255, 255, 255, 0.15);
            }
            
            QComboBox:focus {
                border-color: #6366f1;
                background-color: rgba(99, 102, 241, 0.1);
            }
            
            QComboBox::drop-down {
                border: none;
                width: 28px;
                padding-right: 8px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid rgba(255, 255, 255, 0.5);
                margin-right: 8px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #1a1a1f;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 6px;
                selection-background-color: #6366f1;
                selection-color: white;
                outline: none;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px 4px;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: rgba(99, 102, 241, 0.2);
            }
            
            QSpinBox, QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px 14px;
                color: #ffffff;
                font-size: 13px;
            }
            
            QSpinBox:hover, QLineEdit:hover {
                background-color: rgba(255, 255, 255, 0.08);
                border-color: rgba(255, 255, 255, 0.15);
            }
            
            QSpinBox:focus, QLineEdit:focus {
                border-color: #6366f1;
                background-color: rgba(99, 102, 241, 0.1);
            }
            
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: transparent;
                border: none;
                width: 20px;
            }
            
            QSpinBox::up-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid rgba(255, 255, 255, 0.5);
            }
            
            QSpinBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid rgba(255, 255, 255, 0.5);
            }
            
            /* Buttons */
            QPushButton {
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px 20px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.2);
            }
            
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.05);
            }
            
            QPushButton#primaryBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1,
                    stop:1 #8b5cf6);
                border: none;
                font-weight: 600;
            }
            
            QPushButton#primaryBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4f46e5,
                    stop:1 #7c3aed);
            }
            
            QPushButton#successBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981,
                    stop:1 #059669);
                border: none;
            }
            
            QPushButton#iconBtn {
                padding: 8px;
                min-width: 36px;
                max-width: 36px;
                min-height: 36px;
                max-height: 36px;
                border-radius: 10px;
                font-size: 16px;
            }
            
            /* Status Labels */
            #statusSuccess {
                color: #10b981;
                font-weight: 500;
            }
            
            #statusError {
                color: #ef4444;
                font-weight: 500;
            }
            
            #statusWarning {
                color: #f59e0b;
                font-weight: 500;
            }
            
            /* Scrollbar */
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.02);
                width: 8px;
                border-radius: 4px;
                margin: 4px 2px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 4px;
                min-height: 40px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.25);
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            
            /* Tooltips */
            QToolTip {
                background-color: #1a1a1f;
                color: #ffffff;
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
    
    def init_ui(self):
        """Initialize the modern UI with scrollable content"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area for settings
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # ══════════ OCR Card ══════════
        ocr_card = SettingCard(
            "🔍 Text Recognition (OCR)",
            "How text is extracted from captured images"
        )
        
        self.ocr_backend_combo = QComboBox()
        self.ocr_backend_combo.addItems(['Tesseract', 'Windows OCR'])
        ocr_card.addRow("OCR Engine", self.ocr_backend_combo,
                       "Tesseract is more accurate, Windows OCR is faster")
        
        layout.addWidget(ocr_card)
        
        # ══════════ Translation Card ══════════
        trans_card = SettingCard(
            "🌐 Translation",
            "Source language auto-detected"
        )
        
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems([
            '🇬🇧 English', '🇻🇳 Vietnamese', '🇯🇵 Japanese', '🇰🇷 Korean',
            '🇨🇳 Chinese', '🇪🇸 Spanish', '🇫🇷 French', '🇩🇪 German',
            '🇷🇺 Russian', '🇵🇹 Portuguese', '🇮🇹 Italian', '🇹🇭 Thai'
        ])
        trans_card.addRow("Target Language", self.target_lang_combo,
                         "Language to translate into")
        
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(['Ollama (Offline)', 'Google Translate'])
        self.backend_combo.currentTextChanged.connect(self.on_backend_changed)
        trans_card.addRow("Translation Backend", self.backend_combo,
                         "Ollama runs locally, Google requires internet")
        
        layout.addWidget(trans_card)
        
        # ══════════ Ollama Card ══════════
        self.ollama_card = SettingCard(
            "🤖 Ollama Configuration",
            "Local Ollama server settings"
        )
        
        # URL
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("http://localhost:11434")
        self.ollama_card.addRow("Server URL", self.ollama_url_input,
                               "Usually http://localhost:11434")
        
        # Model row with refresh button
        model_row = QHBoxLayout()
        model_row.setSpacing(16)
        
        # Label
        model_label = QLabel("Model")
        model_label.setObjectName("settingLabel")
        model_label.setToolTip("Example: llama3:8b, mistral, gemma")
        model_label.setCursor(Qt.CursorShape.WhatsThisCursor)
        model_row.addWidget(model_label)
        model_row.addStretch()
        
        # Right side container for model input and refresh button
        right_container = QHBoxLayout()
        right_container.setSpacing(8)
        right_container.setContentsMargins(0, 0, 0, 0)
        
        # Model combo
        self.ollama_model_combo = QComboBox()
        self.ollama_model_combo.setEditable(True)
        self.ollama_model_combo.setPlaceholderText("Select or type model name...")
        self.ollama_model_combo.setMinimumWidth(180)
        self.ollama_model_combo.setMaximumWidth(220)
        self.ollama_model_combo.setToolTip("Example: llama3:8b, mistral, gemma")
        right_container.addWidget(self.ollama_model_combo)
        
        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setObjectName("iconBtn")
        refresh_btn.setToolTip("Refresh model list from server")
        refresh_btn.clicked.connect(self.refresh_ollama_models)
        right_container.addWidget(refresh_btn)
        
        model_row.addLayout(right_container)
        self.ollama_card.addLayout(model_row)
        
        # Test button row
        test_row = QHBoxLayout()
        test_row.setSpacing(10)
        test_row.setContentsMargins(0, 8, 0, 0)
        
        self.test_btn = QPushButton("🧪  Test Connection")
        self.test_btn.setToolTip("Test if Ollama server is running and model is available")
        self.test_btn.setMinimumHeight(38)
        self.test_btn.clicked.connect(self.test_ollama_connection)
        test_row.addWidget(self.test_btn)
        
        test_row.addStretch()
        self.ollama_card.addLayout(test_row)
        
        # Status label with icon
        status_container = QHBoxLayout()
        status_container.setSpacing(8)
        status_container.setContentsMargins(0, 4, 0, 0)
        
        self.test_status = QLabel("ℹ️  Click 'Test Connection' to verify Ollama setup")
        self.test_status.setObjectName("hintLabel")
        self.test_status.setWordWrap(True)
        status_container.addWidget(self.test_status)
        status_container.addStretch()
        
        self.ollama_card.addLayout(status_container)
        
        layout.addWidget(self.ollama_card)
        
        # ══════════ Display Card ══════════
        display_card = SettingCard(
            "🎨 Display",
            "Appearance settings"
        )
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 28)
        self.font_size_spin.setValue(14)
        self.font_size_spin.setSuffix(" px")
        display_card.addRow("Result Font Size", self.font_size_spin,
                           "Size of translated text display")
        
        layout.addWidget(display_card)
        
        # ══════════ Spacer ══════════
        layout.addStretch()
        
        # ══════════ Action Buttons ══════════
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        
        save_btn = QPushButton("💾  Save Settings")
        save_btn.setObjectName("primaryBtn")
        save_btn.setMinimumHeight(38)
        save_btn.setMinimumWidth(140)
        save_btn.clicked.connect(self.save_settings)
        btn_row.addWidget(save_btn)
        
        reset_btn = QPushButton("↺  Reset")
        reset_btn.setMinimumHeight(38)
        reset_btn.clicked.connect(self.reset_settings)
        btn_row.addWidget(reset_btn)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        # Set the scroll area content and add to main layout
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def on_backend_changed(self, backend):
        """Show/hide Ollama settings"""
        is_ollama = 'Ollama' in backend
        self.ollama_card.setVisible(is_ollama)
        if is_ollama:
            self.refresh_ollama_models()
    
    def load_settings(self):
        """Load settings from config"""
        config = self.config_manager.config
        
        # OCR
        ocr = config.get('ocr_backend', 'tesseract')
        self.ocr_backend_combo.setCurrentText('Windows OCR' if ocr == 'windows' else 'Tesseract')
        
        # Target language - map code to display text
        lang_map = {
            'en': '🇬🇧 English', 'vi': '🇻🇳 Vietnamese', 'ja': '🇯🇵 Japanese',
            'ko': '🇰🇷 Korean', 'zh': '🇨🇳 Chinese', 'es': '🇪🇸 Spanish',
            'fr': '🇫🇷 French', 'de': '🇩🇪 German', 'ru': '🇷🇺 Russian',
            'pt': '🇵🇹 Portuguese', 'it': '🇮🇹 Italian', 'th': '🇹🇭 Thai'
        }
        tgt_lang = config.get('target_language', 'en')
        display_lang = lang_map.get(tgt_lang, '🇬🇧 English')
        self.target_lang_combo.setCurrentText(display_lang)
        
        # Translation backend
        backend = config.get('translation_backend', 'ollama')
        self.backend_combo.setCurrentText('Google Translate' if backend == 'google' else 'Ollama (Offline)')
        
        # Ollama
        self.ollama_url_input.setText(config.get('ollama_url', 'http://localhost:11434'))
        self.refresh_ollama_models()
        self.ollama_model_combo.setCurrentText(config.get('ollama_model', 'llama3'))
        
        # Font
        self.font_size_spin.setValue(config.get('result_font_size', 14))
        
        # Show/hide Ollama
        self.on_backend_changed(self.backend_combo.currentText())
    
    def save_settings(self):
        """Save settings to config"""
        # Parse target language from display text (e.g., "🇬🇧 English" -> "en")
        lang_reverse_map = {
            '🇬🇧 English': 'en', '🇻🇳 Vietnamese': 'vi', '🇯🇵 Japanese': 'ja',
            '🇰🇷 Korean': 'ko', '🇨🇳 Chinese': 'zh', '🇪🇸 Spanish': 'es',
            '🇫🇷 French': 'fr', '🇩🇪 German': 'de', '🇷🇺 Russian': 'ru',
            '🇵🇹 Portuguese': 'pt', '🇮🇹 Italian': 'it', '🇹🇭 Thai': 'th'
        }
        
        tgt_lang = lang_reverse_map.get(self.target_lang_combo.currentText(), 'en')
        trans_backend = 'ollama' if 'Ollama' in self.backend_combo.currentText() else 'google'
        ocr_backend = 'windows' if 'Windows' in self.ocr_backend_combo.currentText() else 'tesseract'
        
        self.config_manager.update({
            'ocr_backend': ocr_backend,
            'target_language': tgt_lang,
            'translation_backend': trans_backend,
            'ollama_url': self.ollama_url_input.text(),
            'ollama_model': self.ollama_model_combo.currentText(),
            'result_font_size': self.font_size_spin.value()
        })
        
        # Show success message
        msg = QMessageBox(self)
        msg.setWindowTitle("Success")
        msg.setText("✓ Settings saved successfully!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a1f;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #6366f1;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                color: white;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        msg.exec()
    
    def reset_settings(self):
        """Reset to default settings"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Reset Settings")
        msg.setText("Are you sure you want to reset all settings to defaults?")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a1f;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 20px;
                color: white;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.config_manager.config = self.config_manager.get_defaults()
            self.config_manager.save_config()
            self.load_settings()
            
            success_msg = QMessageBox(self)
            success_msg.setWindowTitle("Success")
            success_msg.setText("✓ Settings reset to defaults!")
            success_msg.setIcon(QMessageBox.Icon.Information)
            success_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1a1a1f;
                }
                QMessageBox QLabel {
                    color: #ffffff;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #6366f1;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 24px;
                    color: white;
                    font-weight: 500;
                }
            """)
            success_msg.exec()

    def refresh_ollama_models(self):
        """Refresh available Ollama models"""
        import requests
        
        url = self.ollama_url_input.text() or "http://localhost:11434"
        current = self.ollama_model_combo.currentText()
        self.ollama_model_combo.clear()
        
        try:
            response = requests.get(f"{url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    names = [m['name'] for m in models]
                    self.ollama_model_combo.addItems(names)
                    if current:
                        idx = self.ollama_model_combo.findText(current)
                        if idx >= 0:
                            self.ollama_model_combo.setCurrentIndex(idx)
                        else:
                            self.ollama_model_combo.setCurrentText(current)
        except:
            pass
    
    def test_ollama_connection(self):
        """Test Ollama connection"""
        url = self.ollama_url_input.text() or "http://localhost:11434"
        model = self.ollama_model_combo.currentText()
        
        if not model:
            QMessageBox.warning(self, "Error", "Please select or enter a model name")
            return
        
        self.test_btn.setEnabled(False)
        self.test_btn.setText("⏳  Testing...")
        self.test_status.setText("⏳  Connecting to Ollama server...")
        self.test_status.setStyleSheet("color: #f59e0b; font-weight: 500; font-size: 13px;")
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        self.test_thread = OllamaTestThread(url, model)
        self.test_thread.finished.connect(self._on_test_complete)
        self.test_thread.start()
    
    def _on_test_complete(self, success, message, model_names):
        """Handle test completion"""
        QApplication.restoreOverrideCursor()
        self.test_btn.setEnabled(True)
        self.test_btn.setText("🧪  Test Connection")
        
        if success:
            self.test_status.setText("✅  Connected! Ollama is ready to use")
            self.test_status.setStyleSheet("color: #10b981; font-weight: 500; font-size: 13px;")
        else:
            error_hints = {
                "Connection": "❌  Cannot connect. Is Ollama running? Start with: ollama serve",
                "not found": f"⚠️  Model not found. Available: {', '.join(model_names[:3]) if model_names else 'none'}",
                "HTTP": f"❌  Server error: {message}"
            }
            
            error_msg = next((hint for key, hint in error_hints.items() if key.lower() in message.lower()), 
                           f"❌  Error: {message[:50]}")
            
            self.test_status.setText(error_msg)
            self.test_status.setStyleSheet("color: #ef4444; font-weight: 500; font-size: 13px;")

