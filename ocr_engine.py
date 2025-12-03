"""
OCR module using Tesseract
"""
import pytesseract
from PIL import Image
import os


class OCREngine:
    """Text extraction using Tesseract OCR"""
    
    def __init__(self, language='eng'):
        self.language = language
        
        # Set Tesseract path for Windows (common installation path)
        if os.name == 'nt':  # Windows
            tesseract_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
    
    def set_language(self, language):
        """Set OCR language"""
        self.language = language
    
    def extract_text(self, image):
        """
        Extract text from image
        
        Args:
            image: PIL Image object
            
        Returns:
            str: Extracted text
        """
        if image is None:
            return ""
        
        try:
            # Perform OCR
            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config='--psm 6'  # Assume uniform block of text
            )
            return text.strip()
        except Exception as e:
            return f"OCR Error: {str(e)}"
    
    def get_available_languages(self):
        """Get list of installed Tesseract languages"""
        try:
            langs = pytesseract.get_languages()
            return langs
        except:
            return ['eng']  # Default fallback
