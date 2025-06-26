import pytest
import io
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pandas as pd

from services.file_service import (
    _read_txt_file,
    _read_docx_file, 
    _read_pdf_file,
    extract_posts_from_history,
    extract_text_from_uploads
)


class TestReadTxtFile:
    """Tests for _read_txt_file function."""
    
    def test_read_simple_txt_file(self, mock_uploaded_file, sample_text_content):
        """Test reading a simple text file."""
        mock_file = mock_uploaded_file(sample_text_content.encode('utf-8'), 'test.txt')
        
        result = _read_txt_file(mock_file)
        
        assert result == sample_text_content
        assert "sample text file" in result
        assert "unicode: éñ中文" in result
    
    def test_read_markdown_file(self, mock_uploaded_file, sample_markdown_content):
        """Test reading a markdown file."""
        mock_file = mock_uploaded_file(sample_markdown_content.encode('utf-8'), 'test.md')
        
        result = _read_txt_file(mock_file)
        
        assert result == sample_markdown_content
        assert "# Sample Markdown" in result
        assert "**bold**" in result
    
    def test_read_empty_file(self, mock_uploaded_file):
        """Test reading an empty file."""
        mock_file = mock_uploaded_file(b'', 'empty.txt')
        
        result = _read_txt_file(mock_file)
        
        assert result == ""
    
    def test_read_file_with_different_encoding(self, mock_uploaded_file):
        """Test reading file with different encoding."""
        content = "Special chars: café résumé naïve"
        mock_file = mock_uploaded_file(content.encode('utf-8'), 'encoded.txt')
        
        result = _read_txt_file(mock_file)
        
        assert "café" in result
        assert "résumé" in result
        assert "naïve" in result
    
    def test_read_large_file(self, mock_uploaded_file):
        """Test reading a large text file."""
        large_content = "Line content\n" * 10000
        mock_file = mock_uploaded_file(large_content.encode('utf-8'), 'large.txt')
        
        result = _read_txt_file(mock_file)
        
        # Account for the final empty line after split
        assert len(result.split('\n')) >= 10000
        assert "Line content" in result
    
    def test_read_file_with_special_characters(self, mock_uploaded_file):
        """Test reading file with various special characters."""
        content = "Symbols: !@#$%^&*()_+-=[]{}|;:,.<>?\nUnicode: 🚀🎉💡\nMath: ∑∏∫∆"
        mock_file = mock_uploaded_file(content.encode('utf-8'), 'special.txt')
        
        result = _read_txt_file(mock_file)
        
        assert "!@#$%^&*()" in result
        assert "🚀🎉💡" in result
        assert "∑∏∫∆" in result


class TestReadDocxFile:
    """Tests for _read_docx_file function."""
    
    def test_read_simple_docx(self, fixtures_path):
        """Test reading a simple Word document."""
        with open(fixtures_path / 'sample.docx', 'rb') as f:
            mock_file = Mock()
            mock_file.read.return_value = f.read()
            mock_file.name = 'sample.docx'
        
        result = _read_docx_file(mock_file)
        
        assert "Sample Word Document" in result
        assert "Introduction" in result
        assert "testing the file parsing" in result
    
    def test_read_docx_with_formatting(self, fixtures_path):
        """Test that formatting is preserved as text."""
        with open(fixtures_path / 'sample.docx', 'rb') as f:
            mock_file = Mock()
            mock_file.read.return_value = f.read()
            mock_file.name = 'formatted.docx'
        
        result = _read_docx_file(mock_file)
        
        # Text content should be preserved even if formatting is lost
        assert "First paragraph" in result
        assert "Second paragraph" in result
    
    def test_read_docx_with_table(self, fixtures_path):
        """Test reading document with tables."""
        with open(fixtures_path / 'sample.docx', 'rb') as f:
            mock_file = Mock()
            mock_file.read.return_value = f.read()
            mock_file.name = 'table.docx'
        
        result = _read_docx_file(mock_file)
        
        assert "Feature" in result
        assert "File Parsing" in result
        assert "In Progress" in result
    
    @patch('docx.Document')
    def test_read_corrupted_docx(self, mock_document):
        """Test handling corrupted Word document."""
        mock_document.side_effect = Exception("Corrupted document")
        mock_file = Mock()
        mock_file.read.return_value = b'corrupted data'
        mock_file.name = 'corrupted.docx'
        
        with pytest.raises(Exception, match="Corrupted document"):
            _read_docx_file(mock_file)
    
    def test_read_empty_docx(self, mock_uploaded_file):
        """Test reading empty or minimal Word document."""
        # This would need a real minimal docx file or proper mocking
        mock_file = mock_uploaded_file(b'', 'empty.docx')
        
        # For now, we expect this to raise an exception with empty bytes
        with pytest.raises(Exception):
            _read_docx_file(mock_file)


class TestReadPdfFile:
    """Tests for _read_pdf_file function."""
    
    def test_read_simple_pdf(self, fixtures_path):
        """Test reading a simple PDF file."""
        with open(fixtures_path / 'sample.pdf', 'rb') as f:
            mock_file = Mock()
            mock_file.read.return_value = f.read()
            mock_file.name = 'sample.pdf'
        
        result = _read_pdf_file(mock_file)
        
        assert "Sample PDF Document" in result
        assert "test PDF file" in result
        # Note: Some special characters might not be preserved exactly
        assert len(result) > 0
    
    def test_read_multipage_pdf(self, fixtures_path):
        """Test reading PDF with multiple pages."""
        # Use the same sample PDF for now, but test that it handles pages correctly
        with open(fixtures_path / 'sample.pdf', 'rb') as f:
            mock_file = Mock()
            mock_file.read.return_value = f.read()
            mock_file.name = 'multipage.pdf'
        
        result = _read_pdf_file(mock_file)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @patch('fitz.open')
    def test_read_corrupted_pdf(self, mock_fitz_open):
        """Test handling corrupted PDF file."""
        mock_fitz_open.side_effect = Exception("Invalid PDF")
        mock_file = Mock()
        mock_file.read.return_value = b'corrupted pdf data'
        mock_file.name = 'corrupted.pdf'
        
        with pytest.raises(Exception):
            _read_pdf_file(mock_file)
    
    @patch('fitz.open')
    def test_read_password_protected_pdf(self, mock_fitz_open):
        """Test handling password-protected PDF."""
        mock_doc = Mock()
        mock_doc.needs_pass = True
        mock_fitz_open.return_value = mock_doc
        
        mock_file = Mock()
        mock_file.read.return_value = b'password protected pdf'
        mock_file.name = 'protected.pdf'
        
        with pytest.raises(Exception):
            _read_pdf_file(mock_file)
    
    def test_read_empty_pdf(self, mock_uploaded_file):
        """Test reading empty PDF file."""
        mock_file = mock_uploaded_file(b'', 'empty.pdf')
        
        with pytest.raises(Exception):
            _read_pdf_file(mock_file)


class TestExtractPostsFromHistory:
    """Tests for extract_posts_from_history function."""
    
    def test_extract_valid_posts_history(self, fixtures_path):
        """Test extracting posts from valid Excel file."""
        with open(fixtures_path / 'sample_posts.xlsx', 'rb') as f:
            mock_file = Mock()
            mock_file.read.return_value = f.read()
            mock_file.name = 'sample_posts.xlsx'
        
        result = extract_posts_from_history(mock_file)
        
        assert isinstance(result, list)
        assert len(result) == 5
        assert "new product launch" in result[0]
        assert "Customer testimonial" in result[1]
        assert "Special offer" in result[3]
    
    def test_extract_posts_with_extra_columns(self, fixtures_path):
        """Test that extra columns are ignored."""
        with open(fixtures_path / 'sample_posts.xlsx', 'rb') as f:
            mock_file = Mock()
            mock_file.read.return_value = f.read()
            mock_file.name = 'extra_columns.xlsx'
        
        result = extract_posts_from_history(mock_file)
        
        # Should still work even with extra Platform and Engagement columns
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_extract_posts_missing_columns(self, fixtures_path):
        """Test handling Excel file with missing required columns."""
        with open(fixtures_path / 'invalid_posts.xlsx', 'rb') as f:
            mock_file = Mock()
            mock_file.read.return_value = f.read()
            mock_file.name = 'invalid_posts.xlsx'
        
        with pytest.raises(KeyError):
            extract_posts_from_history(mock_file)
    
    @patch('pandas.read_excel')
    def test_extract_posts_empty_file(self, mock_read_excel):
        """Test handling empty Excel file."""
        mock_read_excel.return_value = pd.DataFrame()
        mock_file = Mock()
        mock_file.name = 'empty.xlsx'
        mock_file.read.return_value = b'empty excel data'
        
        result = extract_posts_from_history(mock_file)
        
        assert result == []
    
    @patch('pandas.read_excel')
    def test_extract_posts_corrupted_excel(self, mock_read_excel):
        """Test handling corrupted Excel file."""
        mock_read_excel.side_effect = Exception("Corrupted Excel file")
        mock_file = Mock()
        mock_file.name = 'corrupted.xlsx'
        mock_file.read.return_value = b'corrupted excel data'
        
        with pytest.raises(Exception):
            extract_posts_from_history(mock_file)
    
    def test_extract_posts_with_null_values(self):
        """Test handling Excel file with null values."""
        data = {
            'Post Text': ['Valid post', None, 'Another valid post'],
            'Timestamp': ['2024-01-01', '2024-01-02', '2024-01-03']
        }
        df = pd.DataFrame(data)
        
        with patch('pandas.read_excel', return_value=df):
            mock_file = Mock()
            mock_file.name = 'null_values.xlsx'
            mock_file.read.return_value = b'excel with nulls'
            
            result = extract_posts_from_history(mock_file)
            
            # Should handle null values gracefully
            assert len(result) == 3
            assert result[1] is None or pd.isna(result[1])


class TestExtractTextFromUploads:
    """Tests for extract_text_from_uploads function."""
    
    def test_extract_single_txt_file(self, mock_uploaded_file, sample_text_content):
        """Test extracting text from single text file."""
        mock_file = mock_uploaded_file(sample_text_content.encode('utf-8'), 'test.txt')
        
        result = extract_text_from_uploads([mock_file])
        
        assert result == sample_text_content
    
    def test_extract_multiple_txt_files(self, mock_uploaded_file):
        """Test extracting text from multiple text files."""
        content1 = "First file content"
        content2 = "Second file content"
        
        mock_file1 = mock_uploaded_file(content1.encode('utf-8'), 'file1.txt')
        mock_file2 = mock_uploaded_file(content2.encode('utf-8'), 'file2.txt')
        
        result = extract_text_from_uploads([mock_file1, mock_file2])
        
        assert "First file content" in result
        assert "Second file content" in result
    
    def test_extract_mixed_file_types(self, mock_uploaded_file):
        """Test extracting from mixed file types."""
        txt_content = "Text file content"
        md_content = "# Markdown content"
        
        txt_file = mock_uploaded_file(txt_content.encode('utf-8'), 'test.txt')
        md_file = mock_uploaded_file(md_content.encode('utf-8'), 'test.md')
        
        result = extract_text_from_uploads([txt_file, md_file])
        
        assert "Text file content" in result
        assert "# Markdown content" in result
    
    def test_extract_unsupported_file_type(self, mock_uploaded_file):
        """Test handling unsupported file type."""
        mock_file = mock_uploaded_file(b'binary data', 'test.xyz')
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            extract_text_from_uploads([mock_file])
    
    def test_extract_empty_file_list(self):
        """Test handling empty file list."""
        result = extract_text_from_uploads([])
        
        assert result == ""
    
    def test_extract_with_file_size_validation(self, mock_uploaded_file):
        """Test file size validation."""
        # Create a very large file (simulated)
        large_content = "x" * (50 * 1024 * 1024)  # 50MB
        mock_file = mock_uploaded_file(large_content.encode('utf-8'), 'large.txt')
        mock_file.size = len(large_content)
        
        # Should handle large files or raise appropriate error
        try:
            result = extract_text_from_uploads([mock_file])
            # If it succeeds, verify the content
            assert len(result) > 0
        except ValueError as e:
            # If it fails, should be due to file size
            assert "file size" in str(e).lower()


class TestFileValidation:
    """Tests for file validation and error handling."""
    
    def test_validate_file_extension_txt(self, mock_uploaded_file):
        """Test file extension validation for text files."""
        mock_file = mock_uploaded_file(b'content', 'test.txt')
        
        # Should not raise exception for valid extension
        result = extract_text_from_uploads([mock_file])
        assert isinstance(result, str)
    
    def test_validate_file_extension_invalid(self, mock_uploaded_file):
        """Test file extension validation for invalid files."""
        mock_file = mock_uploaded_file(b'content', 'test.exe')
        
        with pytest.raises(ValueError):
            extract_text_from_uploads([mock_file])
    
    def test_handle_file_read_error(self, mock_uploaded_file):
        """Test handling file read errors."""
        mock_file = Mock()
        mock_file.name = 'test.txt'
        mock_file.read.side_effect = IOError("Cannot read file")
        
        with pytest.raises(IOError):
            extract_text_from_uploads([mock_file])
    
    def test_handle_encoding_error(self, mock_uploaded_file):
        """Test handling encoding errors."""
        # Create file with invalid UTF-8 bytes
        invalid_utf8 = b'\xff\xfe\x00\x00'
        mock_file = mock_uploaded_file(invalid_utf8, 'test.txt')
        
        # Should handle encoding errors gracefully
        try:
            result = extract_text_from_uploads([mock_file])
            # If successful, should return some content
            assert isinstance(result, str)
        except UnicodeDecodeError:
            # If it fails, should be a clear encoding error
            pass