"""
OCR module using Tesseract
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os


class OCREngine:
    """Text extraction using Tesseract OCR with auto language detection"""
    
    def __init__(self, language=None):
        # Language is now optional and auto-detected if None
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
        """Set OCR language (None for auto-detect)"""
        self.language = language
    
    def preprocess_image(self, image):
        """
        Preprocess image for better OCR accuracy
        Handles different display qualities and GPU configurations
        
        Args:
            image: PIL Image object
            
        Returns:
            PIL Image: Preprocessed image
        """
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Upscale small images for better OCR
            min_dimension = 600
            if image.width < min_dimension or image.height < min_dimension:
                scale = max(min_dimension / image.width, min_dimension / image.height)
                new_size = (int(image.width * scale), int(image.height * scale))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Sharpen slightly for better text recognition
            image = image.filter(ImageFilter.SHARPEN)
            
            # Enhance contrast for better text visibility
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            return image
        except Exception as e:
            # Return original image if preprocessing fails
            return image
    
    def extract_text(self, image):
        """
        Extract text from image with auto language detection
        
        Args:
            image: PIL Image object
            
        Returns:
            str: Extracted text
        """
        if image is None:
            return ""
        
        try:
            # Preprocess image for better OCR results across different displays
            processed_image = self.preprocess_image(image)
            
            # Use auto language detection if no language specified
            # Try multiple common languages for better detection
            if self.language is None:
                # First try to detect with OSD (Orientation and Script Detection)
                try:
                    osd = pytesseract.image_to_osd(processed_image)
                    # Extract script info if available
                except:
                    pass
                
                # Use multiple languages for auto-detection
                # Common languages: English, Spanish, French, German, Chinese, Japanese, Korean, Arabic
                lang_string = 'eng+spa+fra+deu+chi_sim+jpn+kor+ara+rus+por+ita+hin'
                text = pytesseract.image_to_string(
                    processed_image,
                    lang=lang_string,
                    config='--psm 6'  # Assume uniform block of text
                )
            else:
                # Use specified language
                text = pytesseract.image_to_string(
                    processed_image,
                    lang=self.language,
                    config='--psm 6'
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
