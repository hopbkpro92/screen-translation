"""
Settings UI for configuration
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QComboBox, QPushButton, QGroupBox,
                              QSpinBox, QMessageBox, QFormLayout)
from PyQt6.QtCore import Qt


class SettingsWidget(QWidget):
    """Settings configuration UI"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # OCR Settings
        ocr_group = QGroupBox("OCR Settings")
        ocr_layout = QFormLayout()
        
        self.ocr_lang_combo = QComboBox()
        self.ocr_lang_combo.addItems([
            'eng (English)',
            'spa (Spanish)',
            'fra (French)',
            'deu (German)',
            'ita (Italian)',
            'por (Portuguese)',
            'rus (Russian)',
            'jpn (Japanese)',
            'kor (Korean)',
            'chi_sim (Chinese Simplified)',
            'chi_tra (Chinese Traditional)',
            'ara (Arabic)',
            'hin (Hindi)'
        ])
        ocr_layout.addRow("OCR Language:", self.ocr_lang_combo)
        
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)
        
        # Translation Settings
        trans_group = QGroupBox("Translation Settings")
        trans_layout = QFormLayout()
        
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems([
            'en (English)',
            'es (Spanish)',
            'fr (French)',
            'de (German)',
            'it (Italian)',
            'pt (Portuguese)',
            'ru (Russian)',
            'ja (Japanese)',
            'ko (Korean)',
            'zh (Chinese)',
            'ar (Arabic)',
            'hi (Hindi)'
        ])
        trans_layout.addRow("Target Language:", self.target_lang_combo)
        
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(['ollama', 'google'])
        self.backend_combo.currentTextChanged.connect(self.on_backend_changed)
        trans_layout.addRow("Translation Backend:", self.backend_combo)
        
        trans_group.setLayout(trans_layout)
        layout.addWidget(trans_group)
        
        # Ollama Settings
        self.ollama_group = QGroupBox("Ollama Settings (Offline)")
        ollama_layout = QFormLayout()
        
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("http://localhost:11434")
        self.ollama_url_input.textChanged.connect(self.on_ollama_url_changed)
        ollama_layout.addRow("Ollama URL:", self.ollama_url_input)
        
        # Model selection with refresh button
        model_layout = QHBoxLayout()
        self.ollama_model_combo = QComboBox()
        self.ollama_model_combo.setEditable(True)
        self.ollama_model_combo.setPlaceholderText("Select or enter model name")
        model_layout.addWidget(self.ollama_model_combo, 1)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setMaximumWidth(80)
        refresh_btn.clicked.connect(self.refresh_ollama_models)
        model_layout.addWidget(refresh_btn)
        
        ollama_layout.addRow("Model:", model_layout)
        
        # Test connection button
        test_btn = QPushButton("Test Connection & Model")
        test_btn.clicked.connect(self.test_ollama_connection)
        ollama_layout.addRow("", test_btn)
        
        self.ollama_group.setLayout(ollama_layout)
        layout.addWidget(self.ollama_group)
        
        # Display Settings
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout()
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 32)
        self.font_size_spin.setValue(14)
        display_layout.addRow("Result Font Size:", self.font_size_spin)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def on_backend_changed(self, backend):
        """Show/hide backend-specific settings"""
        self.ollama_group.setVisible(backend == 'ollama')
        
        # Load Ollama models when backend is selected
        if backend == 'ollama':
            self.refresh_ollama_models()
    
    def load_settings(self):
        """Load settings from config"""
        config = self.config_manager.config
        
        # OCR
        ocr_lang = config.get('ocr_language', 'eng')
        for i in range(self.ocr_lang_combo.count()):
            if self.ocr_lang_combo.itemText(i).startswith(ocr_lang):
                self.ocr_lang_combo.setCurrentIndex(i)
                break
        
        # Target language
        target_lang = config.get('target_language', 'es')
        for i in range(self.target_lang_combo.count()):
            if self.target_lang_combo.itemText(i).startswith(target_lang):
                self.target_lang_combo.setCurrentIndex(i)
                break
        
        # Backend
        backend = config.get('translation_backend', 'ollama')
        self.backend_combo.setCurrentText(backend)
        
        # Ollama
        self.ollama_url_input.setText(config.get('ollama_url', 'http://localhost:11434'))
        
        # Load available models first
        self.refresh_ollama_models()
        
        # Set saved model
        saved_model = config.get('ollama_model', 'gemma')
        self.ollama_model_combo.setCurrentText(saved_model)
        
        # Display
        self.font_size_spin.setValue(config.get('result_font_size', 14))
        
        # Show/hide groups
        self.on_backend_changed(backend)
    
    def save_settings(self):
        """Save settings to config"""
        # Extract language codes from combo box text
        ocr_lang = self.ocr_lang_combo.currentText().split(' ')[0]
        target_lang = self.target_lang_combo.currentText().split(' ')[0]
        
        updates = {
            'ocr_language': ocr_lang,
            'target_language': target_lang,
            'translation_backend': self.backend_combo.currentText(),
            'ollama_url': self.ollama_url_input.text(),
            'ollama_model': self.ollama_model_combo.currentText(),
            'result_font_size': self.font_size_spin.value()
        }
        
        self.config_manager.update(updates)
        
        QMessageBox.information(self, "Success", "Settings saved successfully!")
    
    def reset_settings(self):
        """Reset to default settings"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.config = self.config_manager.load_config()
            self.config_manager.save_config()
            self.load_settings()
            QMessageBox.information(self, "Success", "Settings reset to defaults!")
    
    def refresh_ollama_models(self):
        """Refresh available Ollama models"""
        import requests
        
        url = self.ollama_url_input.text() or "http://localhost:11434"
        current_text = self.ollama_model_combo.currentText()
        
        self.ollama_model_combo.clear()
        
        try:
            response = requests.get(f"{url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    # Get the exact model names from Ollama
                    model_names = [m['name'] for m in models]
                    self.ollama_model_combo.addItems(model_names)
                    
                    # Restore previous selection if it exists
                    if current_text:
                        index = self.ollama_model_combo.findText(current_text)
                        if index >= 0:
                            self.ollama_model_combo.setCurrentIndex(index)
                        else:
                            self.ollama_model_combo.setCurrentText(current_text)
                    elif model_names:
                        # Select first model as default if nothing was selected
                        self.ollama_model_combo.setCurrentIndex(0)
                else:
                    self.ollama_model_combo.setPlaceholderText("No models found - run 'ollama pull <model>'")
        except Exception as e:
            # Silent fail - user can still enter model name manually
            self.ollama_model_combo.setPlaceholderText(f"Cannot connect - {str(e)[:30]}")
    
    def on_ollama_url_changed(self):
        """Called when Ollama URL changes"""
        # Could auto-refresh here, but might be too aggressive
        pass
    
    def test_ollama_connection(self):
        """Test Ollama connection and model availability"""
        import requests
        
        url = self.ollama_url_input.text() or "http://localhost:11434"
        model = self.ollama_model_combo.currentText()
        
        if not model:
            QMessageBox.warning(
                self,
                "No Model Selected",
                "Please select or enter a model name to test."
            )
            return
        
        try:
            # Test connection
            response = requests.get(f"{url}/api/tags", timeout=5)
            if response.status_code != 200:
                QMessageBox.warning(self, "Connection Failed", f"HTTP {response.status_code}")
                return
            
            # Check if model exists
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            model_exists = any(model in name or name in model for name in model_names)
            
            if model_exists:
                # Test the model with a simple query
                test_response = requests.post(
                    f"{url}/api/generate",
                    json={
                        "model": model,
                        "prompt": "Hello",
                        "stream": False
                    },
                    timeout=30
                )
                
                if test_response.status_code == 200:
                    QMessageBox.information(
                        self,
                        "Test Successful",
                        f"✓ Connection to Ollama: OK\n✓ Model '{model}': Available and Working\n\nAll models:\n" + "\n".join(model_names)
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Model Test Failed",
                        f"Model '{model}' exists but failed to respond.\nHTTP {test_response.status_code}"
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Model Not Found",
                    f"Model '{model}' is not installed.\n\nAvailable models:\n" + "\n".join(model_names) + "\n\nTo install:\nollama pull {model}"
                )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Connection Failed",
                f"Cannot connect to Ollama at {url}\n\nError: {str(e)}\n\nMake sure Ollama is running."
            )
