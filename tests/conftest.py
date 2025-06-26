import pytest
import io
from pathlib import Path
from unittest.mock import Mock
import pandas as pd


@pytest.fixture
def mock_uploaded_file():
    """Create a mock Streamlit UploadedFile object."""
    def _create_mock_file(content: bytes, filename: str, file_type: str = None):
        mock_file = Mock()
        mock_file.read.return_value = content
        mock_file.name = filename
        mock_file.type = file_type or f"application/{filename.split('.')[-1]}"
        mock_file.size = len(content)
        
        # Reset read position after each call
        def reset_and_read():
            return content
        mock_file.read = reset_and_read
        
        # Mock getvalue for StringIO compatibility
        mock_file.getvalue.return_value = content
        
        return mock_file
    
    return _create_mock_file


@pytest.fixture
def sample_text_content():
    """Sample text content for testing."""
    return "This is a sample text file.\nIt contains multiple lines.\nAnd some unicode: éñ中文"


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing."""
    return """# Sample Markdown
    
This is a **bold** text and *italic* text.

## Features
- List item 1
- List item 2

[Link example](https://example.com)
"""


@pytest.fixture
def sample_excel_data():
    """Sample Excel data as DataFrame."""
    data = {
        'Post Text': [
            'First social media post about our product',
            'Second post with engagement focus',
            'Third post about company culture'
        ],
        'Timestamp': [
            '2024-01-01 10:00:00',
            '2024-01-02 14:30:00',
            '2024-01-03 09:15:00'
        ]
    }
    return pd.DataFrame(data)


@pytest.fixture
def fixtures_path():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def create_temp_file(tmp_path):
    """Helper to create temporary test files."""
    def _create_file(filename: str, content: str, encoding: str = 'utf-8'):
        file_path = tmp_path / filename
        if isinstance(content, str):
            file_path.write_text(content, encoding=encoding)
        else:
            file_path.write_bytes(content)
        return file_path
    
    return _create_file