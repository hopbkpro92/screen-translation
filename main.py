"""
Main Application
"""
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QPushButton, QTextEdit, QLabel,
                              QTabWidget, QMessageBox, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from screen_capture import ScreenSelector
from ocr_engine import OCREngine
from translation_engine import TranslationEngine
from config_manager import ConfigManager
from settings_ui import SettingsWidget


class ProcessingThread(QThread):
    """Background thread for OCR and translation"""
    finished = pyqtSignal(str, str, str)  # original, translated, status
    
    def __init__(self, image, ocr_engine, translation_engine, target_lang):
        super().__init__()
        self.image = image
        self.ocr_engine = ocr_engine
        self.translation_engine = translation_engine
        self.target_lang = target_lang
    
    def run(self):
        """Process image in background"""
        # OCR
        status = "Extracting text..."
        original_text = self.ocr_engine.extract_text(self.image)
        
        if not original_text or original_text.startswith("OCR Error"):
            self.finished.emit(original_text, "", "OCR failed")
            return
        
        # Translation
        status = "Translating..."
        translated_text = self.translation_engine.translate(original_text, self.target_lang)
        
        self.finished.emit(original_text, translated_text, "Completed")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.ocr_engine = OCREngine()  # Auto-detect language
        self.translation_engine = TranslationEngine(self.config_manager.config)
        self.screen_selector = ScreenSelector()
        
        # Connect screen selector
        self.screen_selector.hide()
        
        self.processing_thread = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Screen Translation")
        self.setGeometry(100, 100, 900, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Main tab
        main_tab = self.create_main_tab()
        tabs.addTab(main_tab, "Capture & Translate")
        
        # Settings tab
        self.settings_widget = SettingsWidget(self.config_manager)
        tabs.addTab(self.settings_widget, "Settings")
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(tabs)
        central_widget.setLayout(layout)
        
    def create_main_tab(self):
        """Create main capture tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Screen Translation Tool")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Click 'Start Capture' and drag to select a screen area.\n"
            "Text will be extracted and translated automatically."
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: #666; margin: 10px;")
        layout.addWidget(instructions)
        
        # Capture button
        self.capture_btn = QPushButton("Start Capture")
        self.capture_btn.setMinimumHeight(50)
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.capture_btn.clicked.connect(self.start_capture)
        layout.addWidget(self.capture_btn)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; color: #4CAF50; margin: 10px;")
        layout.addWidget(self.status_label)
        
        # Results area
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Original text
        original_group = QWidget()
        original_layout = QVBoxLayout()
        original_layout.setContentsMargins(0, 0, 0, 0)
        
        original_label = QLabel("Original Text (OCR):")
        original_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        original_layout.addWidget(original_label)
        
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        self.original_text.setPlaceholderText("Original text will appear here...")
        original_layout.addWidget(self.original_text)
        
        original_group.setLayout(original_layout)
        splitter.addWidget(original_group)
        
        # Translated text
        translated_group = QWidget()
        translated_layout = QVBoxLayout()
        translated_layout.setContentsMargins(0, 0, 0, 0)
        
        translated_label = QLabel("Translated Text:")
        translated_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        translated_layout.addWidget(translated_label)
        
        self.translated_text = QTextEdit()
        self.translated_text.setReadOnly(True)
        self.translated_text.setPlaceholderText("Translation will appear here...")
        font = QFont()
        font.setPointSize(self.config_manager.get('result_font_size', 14))
        self.translated_text.setFont(font)
        translated_layout.addWidget(self.translated_text)
        
        translated_group.setLayout(translated_layout)
        splitter.addWidget(translated_group)
        
        layout.addWidget(splitter)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Copy Translation")
        copy_btn.clicked.connect(self.copy_translation)
        button_layout.addWidget(copy_btn)
        
        clear_btn = QPushButton("Clear Results")
        clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def start_capture(self):
        """Start screen capture"""
        self.status_label.setText("Select screen area...")
        self.status_label.setStyleSheet("font-weight: bold; color: #FF9800;")
        self.capture_btn.setEnabled(False)
        
        # Hide main window temporarily and wait for it to disappear
        self.hide()
        QApplication.processEvents()
        
        # Use a short delay to ensure window is fully hidden before capture
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(200, self._do_capture)
    
    def _do_capture(self):
        """Perform the actual screen capture after delay"""
        # Start capture
        self.screen_selector.start_capture()
        
        # Wait for capture (use timer to check)
        from PyQt6.QtCore import QTimer
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_capture_complete)
        self.check_timer.start(100)
    
    def check_capture_complete(self):
        """Check if capture is complete"""
        if not self.screen_selector.isVisible():
            self.check_timer.stop()
            self.show()
            self.raise_()
            self.activateWindow()
            
            # Get captured image
            image = self.screen_selector.get_selected_image()
            
            if image:
                self.process_image(image)
            else:
                self.status_label.setText("Capture cancelled")
                self.status_label.setStyleSheet("font-weight: bold; color: #F44336;")
                self.capture_btn.setEnabled(True)
    
    def process_image(self, image):
        """Process captured image"""
        self.status_label.setText("Processing...")
        self.status_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        
        # Update engines with latest config
        # OCR now uses auto-detection, no need to set language
        self.translation_engine.config = self.config_manager.config
        self.translation_engine.backend = self.config_manager.get('translation_backend', 'ollama')
        
        # Process in background thread
        self.processing_thread = ProcessingThread(
            image,
            self.ocr_engine,
            self.translation_engine,
            self.config_manager.get('target_language', 'es')
        )
        self.processing_thread.finished.connect(self.on_processing_complete)
        self.processing_thread.start()
    
    def on_processing_complete(self, original, translated, status):
        """Handle processing completion"""
        self.original_text.setText(original)
        self.translated_text.setText(translated)
        
        if status == "Completed":
            self.status_label.setText("✓ Translation completed!")
            self.status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        else:
            self.status_label.setText(f"✗ {status}")
            self.status_label.setStyleSheet("font-weight: bold; color: #F44336;")
        
        self.capture_btn.setEnabled(True)
        
        # Update font size
        font = QFont()
        font.setPointSize(self.config_manager.get('result_font_size', 14))
        self.translated_text.setFont(font)
    
    def copy_translation(self):
        """Copy translation to clipboard"""
        text = self.translated_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_label.setText("✓ Copied to clipboard!")
            self.status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
    
    def clear_results(self):
        """Clear result text areas"""
        self.original_text.clear()
        self.translated_text.clear()
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Screen Translation")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
