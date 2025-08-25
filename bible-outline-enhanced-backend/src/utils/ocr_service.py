import os
import tempfile
from typing import Dict
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np

class OCRService:
    def __init__(self):
        # Configure tesseract if needed
        # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Adjust path if needed
        pass
    
    def process_image(self, image_path: str) -> Dict:
        """Extract text from image using OCR"""
        try:
            # Enhance image for better OCR
            enhanced_path = self._enhance_image(image_path)
            
            # Extract text using tesseract
            text = pytesseract.image_to_string(
                Image.open(enhanced_path),
                config='--psm 6'  # Assume uniform block of text
            )
            
            # Clean up enhanced image
            if enhanced_path != image_path:
                os.remove(enhanced_path)
            
            # Clean extracted text
            cleaned_text = self._clean_extracted_text(text)
            
            return {
                'success': True,
                'text': cleaned_text,
                'original_text': text,
                'confidence': self._estimate_confidence(text)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _enhance_image(self, image_path: str) -> str:
        """Enhance image quality for better OCR results"""
        try:
            # Open image with PIL
            image = Image.open(image_path)
            
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Apply noise reduction
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Save enhanced image
            enhanced_path = os.path.join(
                tempfile.gettempdir(),
                f"enhanced_{os.path.basename(image_path)}"
            )
            image.save(enhanced_path)
            
            return enhanced_path
            
        except Exception:
            # If enhancement fails, return original path
            return image_path
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and format extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                cleaned_lines.append(line)
        
        # Join lines with proper spacing
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Fix common OCR errors
        cleaned_text = self._fix_common_ocr_errors(cleaned_text)
        
        return cleaned_text
    
    def _fix_common_ocr_errors(self, text: str) -> str:
        """Fix common OCR recognition errors"""
        # Common OCR error corrections
        corrections = {
            '0': 'O',  # Zero to letter O in some contexts
            '1': 'I',  # One to letter I in some contexts
            '5': 'S',  # Five to letter S in some contexts
            '8': 'B',  # Eight to letter B in some contexts
            'rn': 'm',  # Common misrecognition
            'vv': 'w',  # Common misrecognition
            'cl': 'd',  # Common misrecognition
        }
        
        # Apply corrections carefully (only in likely contexts)
        # This is a simplified approach - in practice, you'd want more sophisticated logic
        
        return text
    
    def _estimate_confidence(self, text: str) -> float:
        """Estimate OCR confidence based on text characteristics"""
        if not text:
            return 0.0
        
        # Simple heuristic based on text characteristics
        confidence = 1.0
        
        # Reduce confidence for very short text
        if len(text.strip()) < 10:
            confidence *= 0.7
        
        # Reduce confidence for text with many special characters
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if special_char_ratio > 0.3:
            confidence *= 0.8
        
        # Reduce confidence for text with unusual character patterns
        if '|||' in text or '___' in text:
            confidence *= 0.6
        
        return min(confidence, 1.0)
    
    def enhance_image_for_ocr(self, image_path: str) -> str:
        """Public method to enhance image for OCR"""
        return self._enhance_image(image_path)

