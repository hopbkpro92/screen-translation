"""
OCR module supporting Tesseract and Windows OCR (via winocr)
With improved text preprocessing and auto language detection
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import os
import sys
import re


class WindowsOCR:
    """Windows 10/11 OCR using winocr package with enhanced text cleaning"""
    
    # Windows OCR language tags (BCP-47 format)
    LANG_MAP = {
        'en': 'en-US',
        'ja': 'ja-JP',      # Japanese
        'ko': 'ko-KR',      # Korean
        'zh': 'zh-CN',      # Chinese Simplified
        'zh-tw': 'zh-TW',   # Chinese Traditional
        'es': 'es-ES',
        'fr': 'fr-FR',
        'de': 'de-DE',
        'it': 'it-IT',
        'pt': 'pt-BR',
        'ru': 'ru-RU',
        'ar': 'ar-SA',
        'hi': 'hi-IN',
        'th': 'th-TH',
        'vi': 'vi-VN',
        'nl': 'nl-NL',
        'pl': 'pl-PL',
        'tr': 'tr-TR',
    }
    
    def __init__(self):
        self.winocr = None
        self.available = self._check_availability()
    
    def _check_availability(self):
        """Check if Windows OCR (winocr) is available"""
        if sys.platform != 'win32':
            return False
        try:
            import winocr
            self.winocr = winocr
            return True
        except ImportError:
            return False
    
    def get_installed_languages(self):
        """Get list of installed OCR languages on Windows"""
        if not self.available:
            return ['en-US']
        try:
            import asyncio
            
            async def get_langs():
                return await self.winocr.list_langs()
            
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    future = asyncio.run_coroutine_threadsafe(get_langs(), loop)
                    return future.result(timeout=5)
                else:
                    return loop.run_until_complete(get_langs())
            except RuntimeError:
                return asyncio.run(get_langs())
        except:
            return ['en-US']
    
    def _clean_ocr_text(self, text):
        """
        Clean OCR text by removing common artifacts and noise
        
        Args:
            text: Raw OCR text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove common OCR artifacts and noise characters
        # These are often misrecognized characters
        noise_patterns = [
            r'[│┃┆┇┊┋╎╏║]',  # Box drawing characters often misrecognized
            r'[◆◇○●□■△▲▽▼◎★☆]',  # Shapes that appear as noise
            r'[「」『』【】〔〕〈〉《》]',  # CJK brackets (keep if meaningful)
            r'[\x00-\x08\x0b\x0c\x0e-\x1f]',  # Control characters
            r'[­​‌‍‎‏]',  # Zero-width and soft hyphen characters
        ]
        
        cleaned = text
        for pattern in noise_patterns:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Remove repeated punctuation (like "..." becoming "......")
        cleaned = re.sub(r'\.{4,}', '...', cleaned)
        cleaned = re.sub(r'\!{3,}', '!!', cleaned)
        cleaned = re.sub(r'\?{3,}', '??', cleaned)
        
        # Remove lines that are mostly noise (less than 2 alphanumeric chars)
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            # Count meaningful characters (letters, numbers, CJK)
            meaningful = len(re.findall(r'[\w\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff\uac00-\ud7af]', line))
            total = len(line.strip())
            
            # Keep line if it has meaningful content
            if total == 0:
                continue
            if meaningful >= 2 or (meaningful / total) > 0.3:
                cleaned_lines.append(line)
        
        cleaned = '\n'.join(cleaned_lines)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'[ \t]{3,}', '  ', cleaned)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned.strip()
    
    def _preprocess_for_windows_ocr(self, image):
        """
        Preprocess image specifically for Windows OCR to improve accuracy
        
        Args:
            image: PIL Image object
            
        Returns:
            PIL Image: Preprocessed image
        """
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get image dimensions
            width, height = image.size
            
            # Limit maximum dimensions to prevent 'image too large' errors
            max_dimension = 4000
            if width > max_dimension or height > max_dimension:
                scale = min(max_dimension / width, max_dimension / height)
                new_size = (int(width * scale), int(height * scale))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                width, height = new_size
            
            # Upscale small images for better OCR
            # Windows OCR works better with larger images
            min_dimension = 800
            if width < min_dimension or height < min_dimension:
                scale = min(min_dimension / width, min_dimension / height, 2.5)
                new_size = (int(width * scale), int(height * scale))
                # Double-check we don't exceed max after upscaling
                if new_size[0] <= max_dimension and new_size[1] <= max_dimension:
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Increase contrast significantly
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.8)
            
            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Slightly increase brightness if image is dark
            # Calculate average brightness
            grayscale = image.convert('L')
            avg_brightness = sum(grayscale.getdata()) / len(list(grayscale.getdata()))
            
            if avg_brightness < 100:  # Dark image
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.3)
            
            return image
        except Exception:
            return image
    
    def extract_text(self, image, lang='en'):
        """Extract text using Windows OCR via winocr with enhanced processing and multi-language support"""
        if not self.available or self.winocr is None:
            return """Windows OCR Error: winocr not installed.

To install:
  pip install winocr

For Japanese support, also install Windows language pack:
1. Settings → Time & Language → Language
2. Add Japanese language
3. Download language pack (includes OCR)

Alternatively, use Tesseract OCR instead."""
        
        try:
            import asyncio
            
            # Preprocess image for better results
            processed_image = self._preprocess_for_windows_ocr(image)
            
            # Run async OCR with multiple fallback strategies
            async def do_ocr():
                last_error = None
                best_result = None
                best_score = 0
                
                # Strategy 1: Try multiple languages and pick the best result
                # Order by most common use cases
                common_langs = ['ja-JP', 'en-US', 'ko-KR', 'zh-CN', 'zh-TW']
                
                for try_lang in common_langs:
                    try:
                        result = await self.winocr.recognize_pil(processed_image, lang=try_lang)
                        
                        # Check if we got meaningful text
                        if hasattr(result, 'text') and result.text:
                            text_length = len(result.text.strip())
                            
                            # Score based on text length and character distribution
                            # Longer text usually means better detection
                            if text_length > 0:
                                # Calculate confidence score
                                score = text_length
                                
                                # Bonus for having alphanumeric or CJK characters
                                meaningful_chars = len(re.findall(r'[\w\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff\uac00-\ud7af]', result.text))
                                score += meaningful_chars * 2
                                
                                # If this is the best result so far, keep it
                                if score > best_score:
                                    best_score = score
                                    best_result = result
                    except Exception as e:
                        last_error = e
                        continue
                
                # If we found a good result, return it
                if best_result and best_score > 5:  # Threshold for meaningful text
                    return best_result
                
                # Strategy 3: If specific language was requested, try it
                if lang != 'auto' and lang != 'en':
                    ocr_lang = self.LANG_MAP.get(lang, 'en-US')
                    try:
                        result = await self.winocr.recognize_pil(processed_image, lang=ocr_lang)
                        return result
                    except Exception as e:
                        last_error = e
                
                # If all strategies fail, check if it's a language pack issue
                if last_error:
                    error_msg = str(last_error).lower()
                    if 'language' in error_msg or 'not installed' in error_msg or 'not available' in error_msg:
                        # Return helpful message about installing language packs
                        class ErrorResult:
                            text = """No text detected. For Japanese/Korean/Chinese:

1. Install Windows language pack:
   Settings → Time & Language → Language & Region
   → Add language → Select Japanese/Korean/Chinese
   → Download & install

2. Or switch to Tesseract OCR in Settings"""
                        return ErrorResult()
                    raise last_error
                
                # Return empty result if nothing worked
                class EmptyResult:
                    text = "No text detected"
                return EmptyResult()
            
            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    future = asyncio.run_coroutine_threadsafe(do_ocr(), loop)
                    result = future.result(timeout=30)
                else:
                    result = loop.run_until_complete(do_ocr())
            except RuntimeError:
                result = asyncio.run(do_ocr())
            
            # Extract text from result
            raw_text = ""
            if hasattr(result, 'text'):
                raw_text = result.text if result.text else ""
            elif isinstance(result, dict) and 'text' in result:
                raw_text = result['text']
            elif isinstance(result, str):
                raw_text = result
            else:
                # Try to get text from lines
                text_parts = []
                if hasattr(result, 'lines'):
                    for line in result.lines:
                        if hasattr(line, 'text'):
                            text_parts.append(line.text)
                raw_text = '\n'.join(text_parts) if text_parts else str(result)
            
            # Clean the extracted text
            cleaned_text = self._clean_ocr_text(raw_text)
            return cleaned_text
                
        except Exception as e:
            return f"Windows OCR Error: {str(e)}"


class OCREngine:
    """Text extraction using Tesseract OCR or Windows OCR with auto language detection"""
    
    def __init__(self, backend='tesseract', language=None):
        # Backend: 'tesseract' or 'windows'
        self.backend = backend
        self.language = language  # None means auto-detect
        
        # Initialize Windows OCR
        self.windows_ocr = WindowsOCR()
        
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
    
    def set_backend(self, backend):
        """Set OCR backend ('tesseract' or 'windows')"""
        self.backend = backend
    
    def set_language(self, language):
        """Set OCR language (None or 'auto' for auto-detect)"""
        if language == 'auto':
            self.language = None
        else:
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
    
    def _clean_ocr_text(self, text):
        """
        Clean OCR text by removing common artifacts
        
        Args:
            text: Raw OCR text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove common noise characters
        noise_patterns = [
            r'[│┃┆┇┊┋╎╏║]',
            r'[\x00-\x08\x0b\x0c\x0e-\x1f]',
            r'[­​‌‍‎‏]',
        ]
        
        cleaned = text
        for pattern in noise_patterns:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Remove excessive punctuation
        cleaned = re.sub(r'\.{4,}', '...', cleaned)
        cleaned = re.sub(r'\!{3,}', '!!', cleaned)
        cleaned = re.sub(r'\?{3,}', '??', cleaned)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'[ \t]{3,}', '  ', cleaned)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned.strip()
    
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
        
        # Use Windows OCR if selected and available
        if self.backend == 'windows':
            if self.windows_ocr.available:
                processed_image = self.preprocess_image(image)
                # Use 'auto' for auto language detection
                # Windows OCR will detect language automatically without lang parameter
                lang = self.language if self.language else 'auto'
                return self.windows_ocr.extract_text(processed_image, lang=lang)
            else:
                return "Windows OCR Error: winocr not installed. Run: pip install winocr"
        
        # Use Tesseract OCR
        return self._extract_with_tesseract(image)
    
    def _extract_with_tesseract(self, image):
        """Extract text using Tesseract OCR with auto language detection"""
        try:
            # Preprocess image for better OCR results across different displays
            processed_image = self.preprocess_image(image)
            
            # If no language specified, use multi-language detection
            if self.language is None or self.language == 'auto':
                # Use multiple languages for better auto-detection
                # Common languages: English, Japanese, Korean, Chinese, Vietnamese, etc.
                lang_string = 'eng+jpn+kor+chi_sim+vie+tha+rus+deu+fra+spa+por+ita'
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
            
            # Clean the text
            cleaned_text = self._clean_ocr_text(text)
            return cleaned_text
        except Exception as e:
            return f"OCR Error: {str(e)}"
    
    def get_available_languages(self):
        """Get list of installed Tesseract languages"""
        try:
            langs = pytesseract.get_languages()
            return langs
        except:
            return ['eng']  # Default fallback
    
    def is_windows_ocr_available(self):
        """Check if Windows OCR is available"""
        return self.windows_ocr.available
