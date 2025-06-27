"""
Logging Configuration Module - Phase 6.2

Provides centralized logging configuration for the entire application
with appropriate handlers, formatters, and log levels for production use.

Features:
- Structured logging with JSON format option
- File rotation to prevent disk space issues
- Different log levels for different environments
- Security-conscious logging (no sensitive data)
- Performance monitoring capabilities
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime


class SecurityAwareFormatter(logging.Formatter):
    """
    Custom formatter that removes sensitive information from log messages.
    
    Sensitive patterns to filter:
    - API keys (sk-, AI*, etc.)
    - Email addresses
    - Potential passwords
    - File paths (for privacy)
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sensitive_patterns = [
            (r'sk-[a-zA-Z0-9]{20,}', 'sk-***'),
            (r'AIza[a-zA-Z0-9]{35}', 'AIza***'),
            (r'sk-ant-[a-zA-Z0-9-]{20,}', 'sk-ant-***'),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***'),
            (r'password["\s]*[:=]["\s]*[^"\s]+', 'password: ***'),
            (r'/[a-zA-Z0-9/_.-]+/[a-zA-Z0-9/_.-]+\.[a-zA-Z0-9]+', '/***/***/***')
        ]
    
    def format(self, record):
        # Format the basic message
        message = super().format(record)
        
        # Filter sensitive information
        import re
        for pattern, replacement in self.sensitive_patterns:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        
        return message


class JSONFormatter(SecurityAwareFormatter):
    """
    JSON formatter for structured logging.
    
    Outputs log records as JSON objects with consistent fields:
    - timestamp
    - level
    - logger
    - message
    - module
    - function
    - line_number
    """
    
    def format(self, record):
        # Create base log entry
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line_number': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'workflow_id'):
            log_entry['workflow_id'] = record.workflow_id
        
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
        
        # Apply security filtering to the message
        filtered_message = self._filter_sensitive_data(log_entry['message'])
        log_entry['message'] = filtered_message
        
        return json.dumps(log_entry)
    
    def _filter_sensitive_data(self, message: str) -> str:
        """Apply sensitive data filtering to message."""
        import re
        for pattern, replacement in self.sensitive_patterns:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        return message


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 100 * 1024 * 1024,  # 100MB
    backup_count: int = 5,
    json_format: bool = False,
    console_output: bool = True
) -> None:
    """
    Set up comprehensive logging configuration for the application.
    
    Args:
        log_level (str): Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file (str, optional): Path to log file. If None, creates default log file
        max_file_size (int): Maximum size of log file before rotation (bytes)
        backup_count (int): Number of backup files to keep
        json_format (bool): Use JSON formatting for structured logging
        console_output (bool): Whether to output logs to console
        
    Example:
        >>> setup_logging(
        ...     log_level="INFO",
        ...     log_file="app.log",
        ...     json_format=True,
        ...     console_output=True
        ... )
    """
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set root logger level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # Create formatters
    if json_format:
        formatter = JSONFormatter()
        console_formatter = SecurityAwareFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        formatter = SecurityAwareFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        console_formatter = SecurityAwareFormatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file is None:
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "app.log"
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Add error file handler for ERROR and CRITICAL messages
    error_log_file = Path(log_file).parent / "error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # Log initial setup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={log_level}, file={log_file}, json={json_format}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with consistent configuration.
    
    Args:
        name (str): Logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


class LoggingContext:
    """
    Context manager for adding extra context to log messages.
    
    Example:
        >>> with LoggingContext(workflow_id="wf_123", user_id="user_456"):
        ...     logger.info("Processing started")
        # Log will include workflow_id and user_id
    """
    
    def __init__(self, **context):
        self.context = context
        self.old_factory = logging.getLogRecordFactory()
    
    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)


def configure_production_logging():
    """
    Configure logging for production deployment.
    
    Features:
    - WARNING level and above only
    - JSON formatting for log aggregation
    - File rotation to prevent disk issues
    - Error logs in separate file
    - No console output (for daemon mode)
    """
    setup_logging(
        log_level="WARNING",
        log_file="logs/production.log",
        max_file_size=50 * 1024 * 1024,  # 50MB
        backup_count=10,
        json_format=True,
        console_output=False
    )


def configure_development_logging():
    """
    Configure logging for development environment.
    
    Features:
    - DEBUG level for detailed information
    - Human-readable formatting
    - Console output for immediate feedback
    - Smaller file rotation
    """
    setup_logging(
        log_level="DEBUG",
        log_file="logs/development.log",
        max_file_size=10 * 1024 * 1024,  # 10MB
        backup_count=3,
        json_format=False,
        console_output=True
    )


def log_performance(func):
    """
    Decorator to log function performance metrics.
    
    Args:
        func: Function to monitor
        
    Returns:
        Wrapped function with performance logging
        
    Example:
        >>> @log_performance
        ... def expensive_operation():
        ...     time.sleep(1)
        ...     return "result"
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            with LoggingContext(duration=duration):
                logger.info(f"Function {func.__name__} completed successfully in {duration:.3f}s")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            with LoggingContext(duration=duration):
                logger.error(f"Function {func.__name__} failed after {duration:.3f}s: {str(e)}")
            
            raise
    
    return wrapper


# Auto-configure logging based on environment
def auto_configure_logging():
    """
    Automatically configure logging based on environment variables.
    
    Environment Variables:
    - LOG_LEVEL: Logging level (default: INFO)
    - LOG_FILE: Log file path (default: logs/app.log)
    - LOG_FORMAT: 'json' or 'text' (default: text)
    - LOG_CONSOLE: '1' or '0' (default: 1)
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', None)
    json_format = os.getenv('LOG_FORMAT', 'text').lower() == 'json'
    console_output = os.getenv('LOG_CONSOLE', '1') == '1'
    
    setup_logging(
        log_level=log_level,
        log_file=log_file,
        json_format=json_format,
        console_output=console_output
    )


# Initialize logging if this module is imported
if not logging.getLogger().handlers:
    auto_configure_logging()