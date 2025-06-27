# API Reference

Technical documentation for the Auto Post Generator application architecture, components, and APIs.

## 📋 Architecture Overview

The Auto Post Generator follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   Services      │    │   Utilities     │
│   (app.py)      │◄──►│   Layer         │◄──►│   Layer         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                       ┌─────────────────┐
                       │   External      │
                       │   APIs          │
                       └─────────────────┘
```

### Components

- **Frontend Layer**: Streamlit UI components and user interaction
- **Services Layer**: Business logic and workflow orchestration
- **Utilities Layer**: Cross-cutting concerns (logging, data export)
- **External APIs**: LLM provider integrations

## 🔧 Services Layer

### file_service.py

Core file processing functionality with support for multiple formats.

#### Functions

##### `extract_text_from_uploads(uploaded_files: List[Any]) -> str`

Extracts and concatenates text from multiple uploaded files.

**Parameters:**
- `uploaded_files`: List of Streamlit UploadedFile objects

**Returns:**
- `str`: Combined text content from all files

**Raises:**
- `FileProcessingError`: Base exception for file processing issues
- `UnsupportedFileTypeError`: Unsupported file format
- `FileReadError`: File cannot be read
- `FileValidationError`: File validation fails

**Example:**
```python
files = [txt_file, docx_file, pdf_file]
combined_text = extract_text_from_uploads(files)
```

##### `extract_posts_from_history(history_file: Any) -> List[str]`

Extracts post text from Excel history file.

**Parameters:**
- `history_file`: Excel file with 'Post Text' column

**Returns:**
- `List[str]`: List of historical post texts

**Excel Format:**
| Post Text | Platform | Date |
|-----------|----------|------|
| "Sample post content" | LinkedIn | 2024-01-15 |

##### `get_supported_file_types() -> List[str]`

Returns list of supported file extensions.

**Returns:**
- `List[str]`: ['.txt', '.md', '.docx', '.pdf', '.xlsx']

#### Private Functions

##### `_read_txt_file(file: Any) -> str`
Processes plain text and Markdown files with encoding detection.

##### `_read_docx_file(file: Any) -> str`
Extracts text from Word documents including tables and headers.

##### `_read_pdf_file(file: Any) -> str`
Extracts text from PDF documents with page processing.

### llm_service.py

LLM integration and prompt management.

#### Functions

##### `build_master_prompt(...) -> str`

Constructs comprehensive prompts for LLM generation.

**Parameters:**
- `source_text: str`: Content to base posts on
- `brand_guide_text: str`: Brand voice guidelines
- `post_history: List[str]`: Previous successful posts
- `platform: str`: Target platform ('X', 'LinkedIn', etc.)
- `count: int`: Number of posts to generate
- `advanced_settings: Optional[Dict]`: Advanced preferences

**Advanced Settings:**
```python
{
    'creativity_level': 'Conservative' | 'Balanced' | 'Creative' | 'Innovative',
    'include_hashtags': bool,
    'include_emojis': bool,
    'content_tone': 'Professional' | 'Casual' | 'Friendly' | 'Authoritative',
    'call_to_action': bool,
    'avoid_controversy': bool
}
```

**Returns:**
- `str`: Formatted prompt for LLM

##### `call_llm(provider: str, api_key: str, prompt: str) -> str`

Factory function for LLM provider calls.

**Parameters:**
- `provider`: 'OpenAI' | 'Google Gemini' | 'Anthropic'
- `api_key`: Provider API key
- `prompt`: Formatted prompt string

**Returns:**
- `str`: Raw LLM response

**Raises:**
- `ValueError`: Invalid provider or parameters
- `Exception`: API-specific errors (authentication, rate limits, etc.)

##### `parse_llm_response(response: str) -> List[str]`

Parses LLM response into individual posts using multiple strategies.

**Parsing Strategies:**
1. "POST N:" format with "---" separators
2. "POST N:" without separators
3. Numbered format "1. 2. 3."
4. "---" separators only
5. Double newline separation
6. Single post fallback

**Parameters:**
- `response`: Raw LLM response text

**Returns:**
- `List[str]`: Individual cleaned post texts

### post_service.py

Workflow orchestration and business logic.

#### Functions

##### `generate_posts_workflow(...) -> List[str]`

Main orchestration function for the complete post generation workflow.

**Parameters:**
- `source_files`: List of uploaded source files
- `brand_guide`: Optional brand guide file
- `history_file`: Optional post history file
- `provider: str`: LLM provider name
- `api_key: str`: API key for authentication
- `platform: str`: Target platform
- `count: int`: Number of posts (1-50)
- `advanced_settings: Optional[Dict]`: Advanced preferences

**Returns:**
- `List[str]`: Generated and validated posts

**Workflow Steps:**
1. Input validation
2. Source file text extraction
3. Brand guide processing
4. Post history extraction
5. Prompt building
6. LLM generation
7. Response parsing
8. Validation and cleanup

**Exception Hierarchy:**
```
WorkflowError
├── FileProcessingError
├── LLMServiceError
├── PromptBuildingError
└── ResponseParsingError
```

##### `get_workflow_status() -> Dict[str, Any]`

Returns current service capabilities and status.

**Returns:**
```python
{
    'service_name': 'post_service',
    'version': '6.2.0',
    'supported_providers': ['OpenAI', 'Google Gemini', 'Anthropic'],
    'supported_platforms': ['X', 'LinkedIn', 'Facebook', 'Instagram'],
    'max_post_count': 50,
    'features': [...]
}
```

## 🛠️ Utilities Layer

### data_exporter.py

Data export functionality with validation and statistics.

#### Functions

##### `create_csv_export(posts: List[str], platform: str, include_metadata: bool = False) -> Tuple[str, str]`

Creates CSV export data from generated posts.

**Parameters:**
- `posts`: List of post texts
- `platform`: Target platform name
- `include_metadata`: Include additional columns

**Returns:**
- `Tuple[str, str]`: (csv_content, filename)

**CSV Formats:**

*Standard:*
```csv
post_text,generation_timestamp
"Post content here","2024-01-15T10:30:00"
```

*With Metadata:*
```csv
post_text,generation_timestamp,platform,post_number,character_count
"Post content","2024-01-15T10:30:00","LinkedIn",1,145
```

##### `validate_export_data(posts: List[str], platform: str) -> Tuple[bool, List[str]]`

Validates posts before export.

**Validation Checks:**
- Empty or whitespace-only posts
- Platform character limits
- Content quality indicators

**Returns:**
- `Tuple[bool, List[str]]`: (is_valid, list_of_issues)

##### `get_export_statistics(posts: List[str]) -> Dict[str, Any]`

Calculates export statistics and metrics.

**Returns:**
```python
{
    'total_posts': int,
    'valid_posts': int,
    'average_length': float,
    'estimated_file_size_kb': float
}
```

### logging_config.py

Production-ready logging with security features.

#### Classes

##### `SecurityAwareFormatter(logging.Formatter)`

Custom formatter that filters sensitive information.

**Filtered Patterns:**
- API keys (sk-, AIza, sk-ant-)
- Email addresses
- File paths
- Password patterns

##### `JSONFormatter(SecurityAwareFormatter)`

JSON formatter for structured logging.

**Output Format:**
```json
{
    "timestamp": "2024-01-15T10:30:00",
    "level": "INFO",
    "logger": "module_name",
    "message": "Log message",
    "module": "file_name",
    "function": "function_name",
    "line_number": 123
}
```

#### Functions

##### `setup_logging(...) -> None`

Configures comprehensive logging for the application.

**Parameters:**
- `log_level: str`: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
- `log_file: Optional[str]`: Log file path (default: logs/app.log)
- `max_file_size: int`: Maximum file size before rotation (bytes)
- `backup_count: int`: Number of backup files to keep
- `json_format: bool`: Use JSON formatting
- `console_output: bool`: Output to console

**Features:**
- Automatic log rotation
- Separate error logs
- Security filtering
- Performance monitoring

##### `get_logger(name: str) -> logging.Logger`

Gets configured logger instance.

##### `LoggingContext(**context)`

Context manager for adding structured context to logs.

**Example:**
```python
with LoggingContext(workflow_id="wf_123", user_id="user_456"):
    logger.info("Processing started")
# Log includes workflow_id and user_id
```

## 🖥️ Frontend Layer

### app.py

Streamlit UI components and user interaction handling.

#### Key Functions

##### `validate_api_key_format(api_key: str, provider: str) -> Tuple[bool, str]`

Real-time API key format validation.

**Provider Patterns:**
- OpenAI: `sk-` prefix, 20+ characters
- Google Gemini: `AI` prefix, 10+ characters
- Anthropic: `sk-ant-` prefix, 15+ characters

##### `validate_file_uploads(...) -> Tuple[bool, List[str]]`

Comprehensive file upload validation.

**Validation Checks:**
- File format support
- File size limits (10MB)
- Content accessibility
- Security scanning

##### `get_current_workflow_step(...) -> Tuple[int, str]`

Determines current workflow progress for UI indicators.

**Returns:**
- `Tuple[int, str]`: (step_number, next_action_description)

## 🔌 External API Integration

### Supported Providers

#### OpenAI Integration

**Models:**
- GPT-3.5-turbo (default)
- GPT-4 (if available)

**Configuration:**
```python
{
    "model": "gpt-3.5-turbo",
    "max_tokens": 2000,
    "temperature": 0.7
}
```

**Error Handling:**
- Authentication errors
- Rate limiting
- Token limits
- Network issues

#### Google Gemini Integration

**Models:**
- gemini-pro (default)

**Configuration:**
```python
{
    "model": "gemini-pro",
    "generation_config": {
        "temperature": 0.7,
        "max_output_tokens": 2000
    }
}
```

#### Anthropic Integration

**Models:**
- claude-3-sonnet-20240229 (default)

**Configuration:**
```python
{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 2000,
    "temperature": 0.7
}
```

## 📊 Performance Characteristics

### Benchmarks

| Operation | Typical Time | Memory Usage |
|-----------|--------------|--------------|
| File upload (1MB) | < 1s | +10MB |
| Text extraction | < 2s | +5MB |
| Prompt building | < 0.5s | +2MB |
| LLM generation (5 posts) | 10-30s | +15MB |
| Export creation | < 1s | +5MB |

### Limits

| Resource | Limit | Configurable |
|----------|-------|--------------|
| File size | 10MB | Yes (MAX_FILE_SIZE_MB) |
| Post count | 50 | Yes (MAX_POSTS_PER_REQUEST) |
| Memory usage | ~100MB peak | No |
| Concurrent users | 10-50 | Infrastructure dependent |

## 🔒 Security Features

### Data Protection

1. **API Key Security**
   - Never logged or persisted
   - Automatic filtering in logs
   - Transmitted securely to providers

2. **File Processing Security**
   - Memory-only processing
   - No persistent storage
   - Format validation
   - Size limits

3. **Log Security**
   - Sensitive data filtering
   - Structured logging
   - Access controls

### Security Headers

When deployed with Nginx:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin

## 🧪 Testing Framework

### Test Categories

#### Unit Tests (`@pytest.mark.unit`)
- Individual component testing
- Mock external dependencies
- Fast execution (< 5s total)

#### Integration Tests (`@pytest.mark.integration`)
- Cross-component interactions
- End-to-end workflows
- External API mocking

#### Performance Tests (`@pytest.mark.slow`)
- Load testing
- Memory usage validation
- Response time benchmarks

### Test Execution

```bash
# All tests
python run_phase6_tests.py

# Specific categories
pytest -m unit
pytest -m integration
pytest -m "slow or performance"

# With coverage
pytest --cov=services --cov=utils --cov-report=html
```

## 📈 Monitoring and Observability

### Health Checks

**Endpoint:** `/_stcore/health`
**Response:** `{"status": "ok"}`

### Metrics Collection

Available through logging and custom monitoring:

```python
# Performance metrics
{
    "operation": "post_generation",
    "duration": 15.5,
    "posts_count": 5,
    "platform": "LinkedIn",
    "provider": "OpenAI"
}

# Error metrics
{
    "error_type": "FileProcessingError",
    "error_message": "Unsupported file format",
    "file_type": ".xyz",
    "timestamp": "2024-01-15T10:30:00"
}
```

### Log Analysis

Structured JSON logs enable:
- Error rate monitoring
- Performance tracking
- Usage analytics
- Security monitoring

## 🔄 Configuration Management

### Environment Variables

```bash
# Core configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
MAX_FILE_SIZE_MB=10

# Performance tuning
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8501

# Security
SECURE_HEADERS=true
SESSION_TIMEOUT=3600
```

### Runtime Configuration

Configuration can be updated through:
- Environment variables
- Config file modification
- Command-line arguments

---

**For implementation examples and detailed usage, see the [User Guide](user-guide.md) and [Deployment Guide](deployment.md).**