"""
Main Application with Modern UI
"""
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QPushButton, QTextEdit, QLabel,
                              QTabWidget, QMessageBox, QSplitter, QFrame,
                              QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QImage

from screen_capture import ScreenSelector
from ocr_engine import OCREngine
from translation_engine import TranslationEngine
from config_manager import ConfigManager
from settings_ui import SettingsWidget
from styles import ThemeManager


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
    """Main application window with modern design"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.ocr_engine = OCREngine(self.config_manager.get('ocr_backend', 'tesseract'))
        self.translation_engine = TranslationEngine(self.config_manager.config)
        self.screen_selector = ScreenSelector()
        
        # Store captured image
        self.captured_image = None
        
        # Current theme
        self.current_theme = self.config_manager.get('theme', 'dark')
        
        # Connect screen selector
        self.screen_selector.hide()
        
        self.processing_thread = None
        
        self.init_ui()
        self.apply_theme(self.current_theme)
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("📸 Screen Translation")
        self.setGeometry(100, 100, 1000, 800)
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # Main tab
        main_tab = self.create_main_tab()
        self.tabs.addTab(main_tab, "📸 Capture")
        
        # Settings tab
        self.settings_widget = SettingsWidget(self.config_manager)
        self.settings_widget.theme_changed.connect(self.apply_theme)
        self.tabs.addTab(self.settings_widget, "⚙️ Settings")
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
    
    def apply_theme(self, theme):
        """Apply the selected theme"""
        self.current_theme = theme
        stylesheet = ThemeManager.get_stylesheet(theme)
        self.setStyleSheet(stylesheet)
        
        # Update capture button style
        if hasattr(self, 'capture_btn'):
            self.capture_btn.setStyleSheet(ThemeManager.get_capture_button_style(theme))
        
    def create_main_tab(self):
        """Create main capture tab with modern design"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📸 Screen Translation")
        title.setProperty("class", "title")
        title.setStyleSheet("font-size: 28px; font-weight: 700;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Capture button
        self.capture_btn = QPushButton("📷  Start Capture")
        self.capture_btn.setMinimumHeight(56)
        self.capture_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.capture_btn.setStyleSheet(ThemeManager.get_capture_button_style(self.current_theme))
        self.capture_btn.clicked.connect(self.start_capture)
        layout.addWidget(self.capture_btn)
        
        # Status label
        self.status_label = QLabel("✓ Ready to capture")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setProperty("class", "status-ready")
        self.status_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #10b981; margin: 8px 0;")
        layout.addWidget(self.status_label)
        
        # Main content splitter (horizontal)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ===== Left side: Image Preview =====
        image_container = QFrame()
        image_container.setProperty("class", "image-frame")
        image_layout = QVBoxLayout()
        image_layout.setContentsMargins(16, 16, 16, 16)
        
        image_header = QLabel("🖼️ Captured Image")
        image_header.setStyleSheet("font-weight: 600; font-size: 15px; margin-bottom: 8px;")
        image_layout.addWidget(image_header)
        
        # Image display area
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setMinimumSize(300, 200)
        self.image_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px dashed #4a5568;
                border-radius: 12px;
                background-color: rgba(0, 0, 0, 0.2);
            }
        """)
        
        self.image_label = QLabel("No image captured yet\n\nClick 'Start Capture' to begin")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("color: #718096; font-size: 14px; padding: 40px;")
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_scroll.setWidget(self.image_label)
        
        image_layout.addWidget(self.image_scroll)
        image_container.setLayout(image_layout)
        main_splitter.addWidget(image_container)
        
        # ===== Right side: Text Results =====
        text_container = QWidget()
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(12)
        
        # Text results splitter (vertical)
        text_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Original text
        original_group = QFrame()
        original_layout = QVBoxLayout()
        original_layout.setContentsMargins(16, 16, 16, 16)
        
        original_label = QLabel("📝 Original Text (OCR)")
        original_label.setStyleSheet("font-weight: 600; font-size: 15px; margin-bottom: 8px;")
        original_layout.addWidget(original_label)
        
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        self.original_text.setPlaceholderText("Original text will appear here after capture...")
        self.original_text.setMinimumHeight(120)
        original_layout.addWidget(self.original_text)
        
        original_group.setLayout(original_layout)
        text_splitter.addWidget(original_group)
        
        # Translated text
        translated_group = QFrame()
        translated_layout = QVBoxLayout()
        translated_layout.setContentsMargins(16, 16, 16, 16)
        
        translated_label = QLabel("🌐 Translated Text")
        translated_label.setStyleSheet("font-weight: 600; font-size: 15px; margin-bottom: 8px;")
        translated_layout.addWidget(translated_label)
        
        self.translated_text = QTextEdit()
        self.translated_text.setReadOnly(True)
        self.translated_text.setPlaceholderText("Translation will appear here...")
        self.translated_text.setMinimumHeight(120)
        font = QFont()
        font.setPointSize(self.config_manager.get('result_font_size', 14))
        self.translated_text.setFont(font)
        translated_layout.addWidget(self.translated_text)
        
        translated_group.setLayout(translated_layout)
        text_splitter.addWidget(translated_group)
        
        text_layout.addWidget(text_splitter)
        text_container.setLayout(text_layout)
        main_splitter.addWidget(text_container)
        
        # Set splitter proportions
        main_splitter.setSizes([400, 500])
        
        layout.addWidget(main_splitter, 1)  # Give splitter stretch factor
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        copy_btn = QPushButton("📋 Copy Translation")
        copy_btn.setMinimumHeight(40)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.clicked.connect(self.copy_translation)
        button_layout.addWidget(copy_btn)
        
        copy_original_btn = QPushButton("📄 Copy Original")
        copy_original_btn.setMinimumHeight(40)
        copy_original_btn.setProperty("class", "secondary")
        copy_original_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_original_btn.clicked.connect(self.copy_original)
        button_layout.addWidget(copy_original_btn)
        
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setMinimumHeight(40)
        clear_btn.setProperty("class", "secondary")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def update_image_display(self, pil_image):
        """Update the image preview with captured image"""
        if pil_image is None:
            return
        
        self.captured_image = pil_image
        
        # Convert PIL image to QPixmap
        if pil_image.mode == 'RGB':
            data = pil_image.tobytes("raw", "RGB")
            qimage = QImage(data, pil_image.width, pil_image.height, 
                           pil_image.width * 3, QImage.Format.Format_RGB888)
        else:
            # Convert to RGB first
            rgb_image = pil_image.convert('RGB')
            data = rgb_image.tobytes("raw", "RGB")
            qimage = QImage(data, rgb_image.width, rgb_image.height, 
                           rgb_image.width * 3, QImage.Format.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qimage)
        
        # Scale to fit while maintaining aspect ratio
        max_width = self.image_scroll.width() - 40
        max_height = self.image_scroll.height() - 40
        
        if pixmap.width() > max_width or pixmap.height() > max_height:
            pixmap = pixmap.scaled(max_width, max_height, 
                                   Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
        
        self.image_label.setPixmap(pixmap)
        self.image_label.setStyleSheet("padding: 10px;")
        
        # Update frame style to show active state
        self.image_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #4f46e5;
                border-radius: 12px;
                background-color: rgba(0, 0, 0, 0.2);
            }
        """)
    
    def start_capture(self):
        """Start screen capture"""
        self.status_label.setText("⏳ Select screen area...")
        self.status_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #f59e0b;")
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
                # Update image preview
                self.update_image_display(image)
                self.process_image(image)
            else:
                self.status_label.setText("✗ Capture cancelled")
                self.status_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #ef4444;")
                self.capture_btn.setEnabled(True)
    
    def process_image(self, image):
        """Process captured image"""
        self.status_label.setText("⚙️ Processing...")
        self.status_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #3b82f6;")
        
        # Update OCR engine with current backend (auto-detect language)
        ocr_backend = self.config_manager.get('ocr_backend', 'tesseract')
        self.ocr_engine.set_backend(ocr_backend)
        self.ocr_engine.set_language('auto')  # Always auto-detect
        
        # Update engines with latest config
        self.translation_engine.config = self.config_manager.config
        self.translation_engine.backend = self.config_manager.get('translation_backend', 'ollama')
        
        # Process in background thread
        self.processing_thread = ProcessingThread(
            image,
            self.ocr_engine,
            self.translation_engine,
            self.config_manager.get('target_language', 'en')
        )
        self.processing_thread.finished.connect(self.on_processing_complete)
        self.processing_thread.start()
    
    def on_processing_complete(self, original, translated, status):
        """Handle processing completion"""
        self.original_text.setText(original)
        self.translated_text.setText(translated)
        
        if status == "Completed":
            self.status_label.setText("✓ Translation completed!")
            self.status_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #10b981;")
        else:
            self.status_label.setText(f"✗ {status}")
            self.status_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #ef4444;")
        
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
            self.status_label.setText("✓ Translation copied to clipboard!")
            self.status_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #10b981;")
        else:
            self.status_label.setText("⚠️ No translation to copy")
            self.status_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #f59e0b;")
    
    def copy_original(self):
        """Copy original text to clipboard"""
        text = self.original_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_label.setText("✓ Original text copied to clipboard!")
            self.status_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #10b981;")
        else:
            self.status_label.setText("⚠️ No text to copy")
            self.status_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #f59e0b;")
    
    def clear_results(self):
        """Clear result text areas and image"""
        self.original_text.clear()
        self.translated_text.clear()
        self.captured_image = None
        
        # Reset image preview
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText("No image captured yet\n\nClick 'Start Capture' to begin")
        self.image_label.setStyleSheet("color: #718096; font-size: 14px; padding: 40px;")
        self.image_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px dashed #4a5568;
                border-radius: 12px;
                background-color: rgba(0, 0, 0, 0.2);
            }
        """)
        
        self.status_label.setText("✓ Ready to capture")
        self.status_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #10b981;")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Screen Translation")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
