# Phase 10: Unicode Text Sanitization - Clean Architecture Design

## 🏗️ **Architecture Overview**

This document outlines the clean architecture design for Phase 10: Unicode Text Sanitization and Character Encoding Fix.

## 📋 **Problem Statement**

Users experience character corruption issues in generated posts across all LLM providers:
- "窶覇" instead of "—" (em dash)
- Smart quotes becoming unreadable
- Unicode symbols getting corrupted
- Inconsistent character encoding between providers

## 🎯 **Design Principles**

### **1. Single Responsibility Principle**
Each component has one clear responsibility:
- **TextSanitizer**: Main orchestration
- **UnicodeNormalizer**: Unicode normalization only
- **CharacterMapper**: Character replacement mapping
- **EncodingValidator**: Validation logic

### **2. Dependency Inversion**
High-level modules don't depend on low-level modules:
- LLM services depend on abstractions, not concrete implementations
- Text sanitization is injected as a dependency

### **3. Open/Closed Principle**
System is open for extension, closed for modification:
- New character mappings can be added without changing core logic
- New sanitization strategies can be plugged in

### **4. Interface Segregation**
Clients depend only on interfaces they use:
- Separate interfaces for normalization, mapping, and validation
- Minimal surface area for each component

## 🏛️ **Layered Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│                     (Streamlit UI)                         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                        │
│              (Post Generation Workflow)                    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                           │
│         ┌─────────────────────────────────────┐             │
│         │      TEXT SANITIZATION DOMAIN      │             │
│         │                                     │             │
│         │  ┌─────────────────────────────┐   │             │
│         │  │     TextSanitizer          │   │             │
│         │  │   (Main Orchestrator)      │   │             │
│         │  └─────────────────────────────┘   │             │
│         │                │                   │             │
│         │  ┌─────────────────────────────┐   │             │
│         │  │   UnicodeNormalizer        │   │             │
│         │  │   (NFKC Normalization)     │   │             │
│         │  └─────────────────────────────┘   │             │
│         │                                     │             │
│         │  ┌─────────────────────────────┐   │             │
│         │  │    CharacterMapper         │   │             │
│         │  │  (Character Replacements)  │   │             │
│         │  └─────────────────────────────┘   │             │
│         │                                     │             │
│         │  ┌─────────────────────────────┐   │             │
│         │  │   EncodingValidator        │   │             │
│         │  │   (Validation Logic)       │   │             │
│         │  └─────────────────────────────┘   │             │
│         └─────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                INFRASTRUCTURE LAYER                        │
│   ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐│
│   │  LLM Services   │  │  Data Export    │  │ File Storage ││
│   │   (OpenAI,      │  │   (CSV, etc.)   │  │   (Logs)     ││
│   │ Anthropic, etc.)│  │                 │  │              ││
│   └─────────────────┘  └─────────────────┘  └──────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## 🔧 **Component Design**

### **1. TextSanitizer (Main Orchestrator)**

```python
class TextSanitizer:
    """
    Main text sanitization orchestrator following Command pattern.
    Coordinates all sanitization operations in the correct order.
    """
    
    def __init__(self, normalizer: UnicodeNormalizer, 
                 mapper: CharacterMapper, 
                 validator: EncodingValidator):
        self._normalizer = normalizer
        self._mapper = mapper
        self._validator = validator
    
    def sanitize_text(self, text: str) -> str:
        """Main sanitization pipeline."""
        # 1. Validate input
        # 2. Normalize Unicode
        # 3. Map problematic characters
        # 4. Final validation
        # 5. Return clean text
```

### **2. UnicodeNormalizer (Normalization)**

```python
class UnicodeNormalizer:
    """
    Handles Unicode normalization using NFKC form.
    Ensures consistent character representation across platforms.
    """
    
    def normalize(self, text: str) -> str:
        """Apply NFKC Unicode normalization."""
        
    def fix_encoding_artifacts(self, text: str) -> str:
        """Fix common encoding corruption patterns."""
```

### **3. CharacterMapper (Character Replacement)**

```python
class CharacterMapper:
    """
    Maps problematic Unicode characters to safe equivalents.
    Configurable replacement strategy.
    """
    
    def map_characters(self, text: str) -> str:
        """Apply character replacement mappings."""
        
    def add_mapping(self, source: str, target: str) -> None:
        """Add custom character mapping."""
```

### **4. EncodingValidator (Validation)**

```python
class EncodingValidator:
    """
    Validates text encoding and detects problematic characters.
    Provides fallback strategies for unhandleable characters.
    """
    
    def validate_encoding(self, text: str) -> bool:
        """Validate text can be safely encoded/decoded."""
        
    def detect_problems(self, text: str) -> List[str]:
        """Detect potential encoding issues."""
```

## 🔌 **Integration Points**

### **1. LLM Service Layer Integration**

```python
# services/llm_service.py
from utils.text_sanitizer import get_text_sanitizer

def _clean_post_content(content: str) -> str:
    # Existing cleaning logic...
    
    # NEW: Unicode sanitization
    sanitizer = get_text_sanitizer()
    content = sanitizer.sanitize_text(content)
    
    # Continue with existing logic...
    return content
```

### **2. Provider Function Integration**

```python
# All provider functions (_call_openai, _call_anthropic, _call_gemini)
def _call_provider(api_key: str, prompt: str, model: str = None, **kwargs) -> str:
    # Make API call...
    response = api_client.generate(...)
    
    # NEW: Sanitize response before returning
    sanitizer = get_text_sanitizer()
    clean_response = sanitizer.sanitize_text(response)
    
    return clean_response
```

### **3. Data Export Enhancement**

```python
# utils/data_exporter.py
from utils.text_sanitizer import get_text_sanitizer

def _sanitize_csv_content(content: str) -> str:
    # NEW: Unicode sanitization first
    sanitizer = get_text_sanitizer()
    content = sanitizer.sanitize_text(content)
    
    # Existing CSV sanitization...
    return content
```

## 📊 **Configuration Management**

### **Character Mapping Configuration**

```python
# Default character mappings
UNICODE_MAPPINGS = {
    # Em dashes and hyphens
    '\u2014': '—',  # em dash
    '\u2013': '–',  # en dash
    '\u2012': '–',  # figure dash
    
    # Quotes
    '\u201c': '"',  # left double quotation mark
    '\u201d': '"',  # right double quotation mark
    '\u2018': "'",  # left single quotation mark
    '\u2019': "'",  # right single quotation mark
    
    # Common corruption patterns
    '窶覇': '—',    # specific corruption case
    '竊会': '"',    # another common case
    
    # Spaces and separators
    '\u00a0': ' ',  # non-breaking space
    '\u2009': ' ',  # thin space
    '\u200b': '',   # zero-width space
}
```

## 🧪 **Testing Strategy**

### **Unit Tests**
- **TextSanitizer**: Pipeline orchestration tests
- **UnicodeNormalizer**: NFKC normalization tests
- **CharacterMapper**: Character replacement tests
- **EncodingValidator**: Validation logic tests

### **Integration Tests**
- **LLM Provider Integration**: Test with real/mock provider responses
- **Export Pipeline**: Test Unicode handling in CSV export
- **UI Display**: Test character rendering in Streamlit

### **Property-Based Tests**
- **Unicode Roundtrip**: Ensure sanitization doesn't break valid text
- **Idempotency**: Multiple sanitization calls produce same result
- **Character Preservation**: Important characters are preserved

## 🚀 **Performance Considerations**

### **Caching Strategy**
- Cache normalized forms for frequently used text
- Memoize character mapping results
- Lazy loading of character mapping dictionaries

### **Memory Optimization**
- Use generators for large text processing
- Avoid string concatenation in loops
- Efficient regex compilation and reuse

## 🔒 **Security Considerations**

### **Input Validation**
- Validate input text length to prevent DoS
- Sanitize control characters that could affect output
- Prevent injection through Unicode normalization

### **Output Safety**
- Ensure sanitized text is safe for UI display
- Validate exported data doesn't contain dangerous sequences
- Maintain audit trail of sanitization operations

## 📝 **Implementation Order**

1. **Phase 10.1**: Create core text sanitizer components
2. **Phase 10.2**: Integrate with LLM service post-processing
3. **Phase 10.3**: Add provider-specific character handling
4. **Phase 10.4**: Enhance UI and export safety

This architecture ensures:
- ✅ **Clean separation of concerns**
- ✅ **Testable components**
- ✅ **Extensible design**
- ✅ **Performance optimization**
- ✅ **Security validation**
- ✅ **Backward compatibility**