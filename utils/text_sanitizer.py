"""
Unicode Text Sanitization Service for Phase 10

This module provides comprehensive Unicode text sanitization to fix character encoding
issues in generated posts across all LLM providers.

Components:
- TextSanitizer: Main orchestrator for text sanitization pipeline
- UnicodeNormalizer: Handles Unicode normalization and encoding artifact fixes
- CharacterMapper: Maps problematic characters to safe equivalents
- EncodingValidator: Validates text encoding and detects issues
- SanitizationConfig: Configuration management for character mappings
"""

import unicodedata
import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SanitizationConfig:
    """Configuration for text sanitization operations."""
    
    def __init__(self):
        """Initialize with default character mappings."""
        self.mappings = {
            # Common corruption patterns (specific cases from user report)
            '窶覇': '—',    # Em dash corruption
            '竊会': '"',    # Quote corruption  
            '窶忤': '"',    # Left quote corruption
            '窶': '"',     # Right quote corruption
            
            # Em dashes and hyphens
            '\u2014': '—',  # em dash
            '\u2013': '–',  # en dash
            '\u2012': '–',  # figure dash
            '\u2015': '—',  # horizontal bar
            
            # Smart quotes normalization
            '\u201c': '"',  # left double quotation mark
            '\u201d': '"',  # right double quotation mark
            '\u2018': "'",  # left single quotation mark
            '\u2019': "'",  # right single quotation mark
            '\u201a': "'",  # single low-9 quotation mark
            '\u201e': '"',  # double low-9 quotation mark
            
            # Spaces and separators
            '\u00a0': ' ',  # non-breaking space
            '\u2009': ' ',  # thin space
            '\u200a': ' ',  # hair space
            '\u200b': '',   # zero-width space
            '\u200c': '',   # zero-width non-joiner
            '\u200d': '',   # zero-width joiner
            '\u2060': '',   # word joiner
            '\ufeff': '',   # zero-width no-break space (BOM)
            
            # Mathematical and special characters
            '\u2026': '...',  # horizontal ellipsis
            '\u00b7': '·',    # middle dot
            '\u2022': '•',    # bullet
            '\u2023': '▸',    # triangular bullet
            
            # Currency and symbols that might get corrupted
            '\u00a2': '¢',    # cent sign
            '\u00a3': '£',    # pound sign
            '\u00a5': '¥',    # yen sign
            '\u20ac': '€',    # euro sign
        }


class UnicodeNormalizer:
    """Handles Unicode normalization using NFKC form and fixes encoding artifacts."""
    
    def normalize(self, text: str) -> str:
        """
        Apply NFKC Unicode normalization to ensure consistent character representation.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text string
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
            
        # Apply NFKC normalization for canonical decomposition and recomposition
        normalized = unicodedata.normalize('NFKC', text)
        
        return normalized
    
    def fix_encoding_artifacts(self, text: str) -> str:
        """
        Fix common encoding corruption patterns that appear in LLM responses.
        
        Args:
            text: Input text with potential encoding issues
            
        Returns:
            Text with encoding artifacts fixed
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        
        # Common encoding corruption patterns observed in real usage
        corruption_fixes = {
            # Em dash corruptions
            '窶覇': '—',
            '窶懊': '—',
            '窶暖': '—',
            '窶兤': '—',
            
            # Quote corruptions  
            '竊会': ' "',  # space + quote
            '竊曇': '"',
            '竊': '"',
            '窶忤': '"',
            '窶': '"',
            '窶懊': '"',
            
            # Additional common patterns
            '窶歛': "'",
            '窶戮': "'",
            'Ã¢Â€Â™': "'",
            'Ã¢Â€Âœ': '"',
            'Ã¢Â€Â': '"',
            'Ã¢Â€Â"': '—',
            
            # Windows-1252 to UTF-8 corruption patterns
            'â€™': "'",
            'â€œ': '"',
            'â€': '"',
            'â€"': '—',
            'â€¦': '...',
        }
        
        # Apply fixes for known corruption patterns
        for corrupted, fixed in corruption_fixes.items():
            text = text.replace(corrupted, fixed)
        
        return text


class CharacterMapper:
    """Maps problematic Unicode characters to safe equivalents."""
    
    def __init__(self, config: Optional[SanitizationConfig] = None):
        """
        Initialize character mapper with configuration.
        
        Args:
            config: Optional configuration object, defaults to new config
        """
        self.config = config or SanitizationConfig()
        self._custom_mappings = {}
    
    def map_characters(self, text: str) -> str:
        """
        Apply character replacement mappings to text.
        
        Args:
            text: Input text to process
            
        Returns:
            Text with character mappings applied
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        
        # Apply configuration mappings
        for source, target in self.config.mappings.items():
            text = text.replace(source, target)
        
        # Apply custom mappings (these override config mappings)
        for source, target in self._custom_mappings.items():
            text = text.replace(source, target)
        
        return text
    
    def add_mapping(self, source: str, target: str) -> None:
        """
        Add a custom character mapping.
        
        Args:
            source: Source character/string to replace
            target: Target character/string to replace with
        """
        if not isinstance(source, str) or not isinstance(target, str):
            raise TypeError("Both source and target must be strings")
        
        self._custom_mappings[source] = target


class EncodingValidator:
    """Validates text encoding and detects problematic characters."""
    
    def validate_encoding(self, text: str) -> bool:
        """
        Validate that text can be safely encoded/decoded.
        
        Args:
            text: Text to validate
            
        Returns:
            True if text is safe, False if issues detected
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        
        try:
            # Test encoding/decoding roundtrip
            encoded = text.encode('utf-8')
            decoded = encoded.decode('utf-8')
            
            # Check for control characters (except whitespace)
            for char in text:
                code = ord(char)
                # Allow normal whitespace but reject other control characters
                if code < 32 and char not in '\n\t\r':
                    return False
                # Reject delete character and other problematic codes
                if code == 127 or (code >= 128 and code <= 159):
                    return False
            
            # Check for known problematic patterns
            problematic_patterns = ['窶', '竊', 'Ã¢Â€', 'â€']
            for pattern in problematic_patterns:
                if pattern in text:
                    return False
            
            return True
            
        except (UnicodeError, UnicodeDecodeError, UnicodeEncodeError):
            return False
    
    def detect_problems(self, text: str) -> List[str]:
        """
        Detect potential encoding issues in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of problem descriptions
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        
        problems = []
        
        # Check for known corruption patterns
        corruption_patterns = {
            '窶覇': 'Em dash corruption detected',
            '竊会': 'Quote corruption detected', 
            '窶忤': 'Left quote corruption detected',
            '窶': 'Right quote corruption detected',
            'Ã¢Â€': 'UTF-8/Windows-1252 encoding issue detected',
            'â€': 'Smart quote encoding issue detected',
        }
        
        for pattern, description in corruption_patterns.items():
            if pattern in text:
                problems.append(description)
        
        # Check for control characters
        control_chars = []
        for i, char in enumerate(text):
            code = ord(char)
            if code < 32 and char not in '\n\t\r':
                control_chars.append(f"Control character at position {i} (code {code})")
        
        if control_chars:
            problems.append(f"Control characters found: {', '.join(control_chars[:3])}")
        
        # Check for unusual Unicode ranges that might indicate problems
        unusual_ranges = []
        for char in text:
            code = ord(char)
            # Check for private use areas and other suspicious ranges
            if (0xe000 <= code <= 0xf8ff) or (0xf0000 <= code <= 0xffffd):
                unusual_ranges.append(f"Private use character: {char} (U+{code:04X})")
        
        if unusual_ranges:
            problems.append(f"Unusual Unicode characters: {', '.join(unusual_ranges[:3])}")
        
        return problems


class TextSanitizer:
    """
    Main text sanitization orchestrator that coordinates all sanitization operations.
    
    Follows the Command pattern to execute sanitization pipeline in the correct order:
    1. Input validation
    2. Unicode normalization 
    3. Encoding artifact fixes
    4. Character mapping
    5. Final validation
    """
    
    def __init__(self, normalizer: Optional[UnicodeNormalizer] = None,
                 mapper: Optional[CharacterMapper] = None,
                 validator: Optional[EncodingValidator] = None):
        """
        Initialize text sanitizer with components.
        
        Args:
            normalizer: Unicode normalizer instance
            mapper: Character mapper instance  
            validator: Encoding validator instance
        """
        self.normalizer = normalizer or UnicodeNormalizer()
        self.mapper = mapper or CharacterMapper()
        self.validator = validator or EncodingValidator()
    
    def sanitize_text(self, text: str) -> str:
        """
        Execute the complete text sanitization pipeline.
        
        Args:
            text: Input text to sanitize
            
        Returns:
            Cleaned and sanitized text
            
        Raises:
            TypeError: If input is not a string
            ValueError: If text cannot be processed
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        
        # Handle empty input
        if not text:
            return text
        
        try:
            # Step 1: Fix encoding artifacts first (before normalization)
            text = self.normalizer.fix_encoding_artifacts(text)
            
            # Step 2: Apply Unicode normalization
            text = self.normalizer.normalize(text)
            
            # Step 3: Apply character mappings
            text = self.mapper.map_characters(text)
            
            # Step 4: Validation check (optional - for monitoring)
            is_valid = self.validator.validate_encoding(text)
            if not is_valid:
                # Log validation issues but continue processing
                problems = self.validator.detect_problems(text)
                # In production, you might want to log these problems
                pass
            
            # Step 5: Final cleanup
            # Remove any remaining problematic characters
            text = self._final_cleanup(text)
            
            return text
            
        except Exception as e:
            # For production use, we might want to return original text
            # rather than raising, depending on error handling strategy
            raise ValueError(f"Text sanitization failed: {str(e)}") from e
    
    def _final_cleanup(self, text: str) -> str:
        """
        Perform final cleanup operations on sanitized text.
        
        Args:
            text: Text to clean up
            
        Returns:
            Final cleaned text
        """
        # Remove null bytes and other problematic control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize excessive whitespace while preserving intentional formatting
        # Replace multiple consecutive spaces (3+) with double space
        text = re.sub(r' {3,}', '  ', text)
        
        # Clean up excessive newlines (4+ consecutive) 
        text = re.sub(r'\n{4,}', '\n\n\n', text)
        
        # Remove trailing whitespace from lines while preserving line breaks
        lines = text.split('\n')
        lines = [line.rstrip() for line in lines]
        text = '\n'.join(lines)
        
        return text


# Factory function for easy integration
_sanitizer_instance = None

def get_text_sanitizer() -> TextSanitizer:
    """
    Get a configured text sanitizer instance (singleton pattern).
    
    Returns:
        Configured TextSanitizer instance
    """
    global _sanitizer_instance
    
    if _sanitizer_instance is None:
        config = SanitizationConfig()
        normalizer = UnicodeNormalizer()
        mapper = CharacterMapper(config)
        validator = EncodingValidator()
        
        _sanitizer_instance = TextSanitizer(
            normalizer=normalizer,
            mapper=mapper, 
            validator=validator
        )
    
    return _sanitizer_instance


# Convenience function for direct use
def sanitize_text(text: str) -> str:
    """
    Convenience function to sanitize text with default configuration.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    sanitizer = get_text_sanitizer()
    return sanitizer.sanitize_text(text)