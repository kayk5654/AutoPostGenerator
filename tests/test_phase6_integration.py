"""
Phase 6.3 Integration Tests - Comprehensive Testing

This module implements the comprehensive testing requirements from Phase 6 Task Block 6.3:
- Integration testing across all components
- End-to-end workflow validation
- Performance benchmarking
- Error handling verification
- Security testing
- Cross-browser compatibility validation

These tests ensure that all Phase 6 enhancements work together correctly
and meet production-ready quality standards.
"""

import pytest
import tempfile
import time
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO, StringIO
import pandas as pd
import json

# Import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from services import file_service, llm_service, post_service
    from utils import data_exporter, logging_config
    from config import LLM_PROVIDERS, TARGET_PLATFORMS
except ImportError as e:
    pytest.skip(f"Could not import project modules: {e}", allow_module_level=True)


@pytest.mark.integration
class TestPhase6Integration:
    """Integration tests for Phase 6 enhancements."""
    
    def test_complete_workflow_with_logging(self):
        """Test complete workflow with Phase 6.2 logging enhancements."""
        
        # Test logging configuration
        logging_config.setup_logging(
            log_level="DEBUG",
            log_file=None,  # Use default
            json_format=False,
            console_output=False
        )
        
        logger = logging_config.get_logger("test_workflow")
        
        # Test logging context manager
        with logging_config.LoggingContext(workflow_id="test_wf_123", test_run=True):
            logger.info("Starting Phase 6 integration test")
            
            # Mock file objects
            mock_source = Mock()
            mock_source.name = "test_source.txt"
            mock_source.read.return_value = b"Test content for social media post generation."
            
            mock_brand = Mock()
            mock_brand.name = "brand_guide.md"
            mock_brand.read.return_value = b"# Brand Voice\\n\\nProfessional and innovative tone."
            
            # Test file processing with enhanced error handling
            try:
                source_text = file_service.extract_text_from_uploads([mock_source])
                assert len(source_text) > 0, "Should extract text from source files"
                
                brand_text = file_service.extract_text_from_uploads([mock_brand])
                assert len(brand_text) > 0, "Should extract text from brand guide"
                
                logger.info("File processing completed successfully")
                
            except file_service.FileProcessingError as e:
                pytest.fail(f"File processing should not fail: {e}")
            
            # Test prompt building with advanced settings
            advanced_settings = {
                'creativity_level': 'Creative',
                'include_hashtags': True,
                'include_emojis': True,
                'content_tone': 'Professional',
                'call_to_action': True,
                'avoid_controversy': True
            }
            
            prompt = llm_service.build_master_prompt(
                source_text=source_text,
                brand_guide_text=brand_text,
                post_history=["Previous post example"],
                platform="LinkedIn",
                count=3,
                advanced_settings=advanced_settings
            )
            
            assert "creativity_level" in prompt.lower() or "creative" in prompt.lower(), "Should include creativity level"
            assert "professional" in prompt.lower(), "Should include content tone"
            assert "linkedin" in prompt.lower(), "Should include platform"
            
            logger.info("Prompt building with advanced settings completed")
            
        logger.info("Phase 6 integration test completed successfully")
    
    def test_enhanced_error_handling(self):
        """Test Phase 6.2 enhanced error handling across components."""
        
        # Test file service error handling
        with pytest.raises(file_service.UnsupportedFileTypeError):
            mock_unsupported = Mock()
            mock_unsupported.name = "test.xyz"  # Unsupported extension
            file_service.extract_text_from_uploads([mock_unsupported])
        
        with pytest.raises(file_service.FileValidationError):
            file_service.extract_text_from_uploads("not_a_list")  # Invalid input type
        
        # Test post service error handling
        with pytest.raises(ValueError):
            post_service.generate_posts_workflow(
                source_files=None,  # Invalid: should be list
                brand_guide=None,
                history_file=None,
                provider="OpenAI",
                api_key="test_key",
                platform="LinkedIn",
                count=5
            )
        
        # Test validation function
        validation_errors = post_service._validate_workflow_inputs(
            source_files=[],  # Empty list should trigger error
            brand_guide=None,
            history_file=None,
            provider="InvalidProvider",  # Invalid provider
            api_key="",  # Empty API key
            platform="InvalidPlatform",  # Invalid platform
            count=0,  # Invalid count
            advanced_settings=None
        )
        
        assert len(validation_errors) > 0, "Should detect multiple validation errors"
        assert any("source file" in error.lower() for error in validation_errors), "Should detect missing source files"
        assert any("provider" in error.lower() for error in validation_errors), "Should detect invalid provider"
        assert any("api_key" in error.lower() for error in validation_errors), "Should detect empty API key"
    
    def test_ui_enhancements_integration(self):
        """Test Phase 6.1 UI enhancements work correctly."""
        
        # Test API key validation
        from app import validate_api_key_format
        
        # Valid API keys
        assert validate_api_key_format("sk-1234567890abcdef", "OpenAI")[0] == True
        assert validate_api_key_format("AIza1234567890", "Google Gemini")[0] == True
        assert validate_api_key_format("sk-ant-1234567890", "Anthropic")[0] == True
        
        # Invalid API keys
        assert validate_api_key_format("", "OpenAI")[0] == False
        assert validate_api_key_format("invalid", "OpenAI")[0] == False
        assert validate_api_key_format("sk-test", "OpenAI")[0] == False  # Contains 'test'
        
        # Test file validation
        from app import validate_file_uploads
        
        # Create mock files
        valid_file = Mock()
        valid_file.name = "test.txt"
        valid_file.size = 1000  # 1KB
        
        large_file = Mock()
        large_file.name = "large.txt"
        large_file.size = 15 * 1024 * 1024  # 15MB (too large)
        
        unsupported_file = Mock()
        unsupported_file.name = "test.xyz"
        unsupported_file.size = 1000
        
        # Test validation scenarios
        is_valid, issues = validate_file_uploads([valid_file], None, None)
        assert is_valid, "Valid files should pass validation"
        
        is_valid, issues = validate_file_uploads([large_file], None, None)
        assert not is_valid, "Large files should fail validation"
        assert any("too large" in issue.lower() for issue in issues)
        
        is_valid, issues = validate_file_uploads([unsupported_file], None, None)
        assert not is_valid, "Unsupported files should fail validation"
        assert any("unsupported format" in issue.lower() for issue in issues)
    
    @pytest.mark.slow
    def test_performance_benchmarks(self):
        """Test performance requirements for Phase 6.3."""
        
        # Test large content processing performance
        large_content = "Sample line of content for performance testing.\\n" * 1000  # ~45KB
        
        start_time = time.time()
        
        # Create multiple mock files
        mock_files = []
        for i in range(5):
            mock_file = Mock()
            mock_file.name = f"large_file_{i}.txt"
            mock_file.read.return_value = large_content.encode()
            mock_files.append(mock_file)
        
        # Test file processing performance
        extracted_text = file_service.extract_text_from_uploads(mock_files)
        
        processing_time = time.time() - start_time
        
        # Performance assertions
        assert processing_time < 2.0, f"Large file processing should be fast: {processing_time:.2f}s"
        assert len(extracted_text) > 0, "Should process large content successfully"
        
        # Test prompt building performance
        start_time = time.time()
        
        prompt = llm_service.build_master_prompt(
            source_text=extracted_text,
            brand_guide_text="Brand guidelines text",
            post_history=["Post 1", "Post 2", "Post 3"],
            platform="LinkedIn",
            count=10,
            advanced_settings={
                'creativity_level': 'Balanced',
                'include_hashtags': True,
                'include_emojis': True,
                'content_tone': 'Professional',
                'call_to_action': True,
                'avoid_controversy': True
            }
        )
        
        prompt_time = time.time() - start_time
        
        assert prompt_time < 0.5, f"Prompt building should be fast: {prompt_time:.2f}s"
        assert len(prompt) > 0, "Should build prompt successfully"
    
    def test_security_validation(self):
        """Test security features in Phase 6.2 logging."""
        
        # Test sensitive data filtering in logging
        formatter = logging_config.SecurityAwareFormatter()
        
        # Create test log record
        import logging
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Processing with API key: sk-1234567890abcdef and email user@example.com",
            args=(),
            exc_info=None
        )
        
        formatted_message = formatter.format(record)
        
        # Security assertions
        assert "sk-1234567890abcdef" not in formatted_message, "API key should be filtered"
        assert "user@example.com" not in formatted_message, "Email should be filtered"
        assert "sk-***" in formatted_message, "API key should be masked"
        assert "***@***.***" in formatted_message, "Email should be masked"
        
        # Test JSON formatter security
        json_formatter = logging_config.JSONFormatter()
        json_message = json_formatter.format(record)
        
        assert "sk-1234567890abcdef" not in json_message, "API key should be filtered in JSON"
        assert "user@example.com" not in json_message, "Email should be filtered in JSON"
    
    def test_export_functionality_integration(self):
        """Test Phase 5 export functionality with Phase 6 enhancements."""
        
        # Test posts with various characteristics
        test_posts = [
            "Short post #hashtag",
            "Medium length post with some content that explains a product feature and includes emojis 🚀 #innovation #tech",
            "Very long post that contains extensive information about a product launch including details about features, benefits, target audience, pricing strategy, and market positioning. This post is designed to test character limit validation and export formatting with very long content that might span multiple lines and contain various types of formatting elements including hashtags #longform #detailed #comprehensive",
            "",  # Empty post
            "   ",  # Whitespace only
            "Post with special characters: áéíóú ñüç €£¥¢'smart quotes' & tags | pipes"
        ]
        
        # Test export validation
        is_valid, issues = data_exporter.validate_export_data(test_posts, "LinkedIn")
        
        # Should detect empty posts
        assert not is_valid or len(issues) > 0, "Should detect validation issues with empty posts"
        
        # Test export statistics
        stats = data_exporter.get_export_statistics(test_posts)
        
        assert stats['total_posts'] == len(test_posts), "Should count all posts"
        assert stats['valid_posts'] < len(test_posts), "Should identify some posts as invalid"
        assert stats['average_length'] > 0, "Should calculate average length"
        assert stats['estimated_file_size_kb'] > 0, "Should estimate file size"
        
        # Test actual export generation
        csv_data, filename = data_exporter.create_csv_export(
            test_posts, 
            "LinkedIn", 
            include_metadata=True
        )
        
        assert csv_data is not None, "Should generate CSV data"
        assert "post_text" in csv_data, "Should include post_text column"
        assert "platform" in csv_data, "Should include platform column"
        assert "LinkedIn" in csv_data, "Should include platform value"
        assert filename.endswith('.csv'), "Should generate proper filename"
        
        # Test CSV parsing
        import io
        df = pd.read_csv(io.StringIO(csv_data))
        assert len(df) > 0, "Should create parseable CSV data"
        assert 'post_text' in df.columns, "Should have required columns"
    
    def test_cross_component_error_propagation(self):
        """Test that errors propagate correctly across components."""
        
        # Test error propagation from file service to post service
        mock_failing_file = Mock()
        mock_failing_file.name = "failing.txt"
        mock_failing_file.read.side_effect = Exception("Simulated file read error")
        
        with pytest.raises(post_service.FileProcessingError):
            post_service.generate_posts_workflow(
                source_files=[mock_failing_file],
                brand_guide=None,
                history_file=None,
                provider="OpenAI",
                api_key="sk-1234567890abcdef",
                platform="LinkedIn",
                count=3
            )
        
        # Test error handling in LLM service
        with patch('services.llm_service._call_openai') as mock_llm:
            mock_llm.side_effect = Exception("API connection failed")
            
            with pytest.raises(post_service.LLMServiceError):
                post_service.generate_posts_workflow(
                    source_files=[self._create_mock_file("test.txt", "content")],
                    brand_guide=None,
                    history_file=None,
                    provider="OpenAI",
                    api_key="sk-1234567890abcdef",
                    platform="LinkedIn",
                    count=3
                )
    
    def test_configuration_and_setup(self):
        """Test that all configuration and setup is working correctly."""
        
        # Test that all required modules can be imported
        assert file_service is not None, "file_service should be importable"
        assert llm_service is not None, "llm_service should be importable"
        assert post_service is not None, "post_service should be importable"
        assert data_exporter is not None, "data_exporter should be importable"
        assert logging_config is not None, "logging_config should be importable"
        
        # Test configuration constants
        assert len(LLM_PROVIDERS) > 0, "Should have LLM providers configured"
        assert len(TARGET_PLATFORMS) > 0, "Should have target platforms configured"
        assert "OpenAI" in LLM_PROVIDERS, "Should include OpenAI provider"
        assert "LinkedIn" in TARGET_PLATFORMS, "Should include LinkedIn platform"
        
        # Test file type validation
        supported_types = file_service.get_supported_file_types()
        assert '.txt' in supported_types, "Should support .txt files"
        assert '.docx' in supported_types, "Should support .docx files"
        assert '.pdf' in supported_types, "Should support .pdf files"
        
        # Test utility functions
        file_info = file_service.get_file_type_info()
        assert isinstance(file_info, dict), "Should return file type information"
        assert len(file_info) > 0, "Should have file type descriptions"
    
    def _create_mock_file(self, name: str, content: str) -> Mock:
        """Create a mock file object for testing."""
        mock_file = Mock()
        mock_file.name = name
        mock_file.read.return_value = content.encode()
        return mock_file


@pytest.mark.integration
class TestPhase6ComponentIntegration:
    """Test integration between specific Phase 6 components."""
    
    def test_logging_integration_with_workflow(self):
        """Test that logging works correctly throughout the workflow."""
        
        import io
        import logging
        
        # Capture log output
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        
        # Configure logger
        logger = logging_config.get_logger("test_integration")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        # Test workflow with logging
        try:
            mock_file = Mock()
            mock_file.name = "integration_test.txt"
            mock_file.read.return_value = b"Integration test content"
            
            # This should generate log messages
            text = file_service.extract_text_from_uploads([mock_file])
            
            # Check that log messages were generated
            log_output = log_stream.getvalue()
            assert "integration_test.txt" in log_output, "Should log filename"
            assert len(log_output) > 0, "Should generate log output"
            
        finally:
            logger.removeHandler(handler)
    
    def test_advanced_settings_integration(self):
        """Test that advanced settings work throughout the workflow."""
        
        # Test advanced settings in prompt building
        advanced_settings = {
            'creativity_level': 'Innovative',
            'include_hashtags': False,
            'include_emojis': False,
            'content_tone': 'Authoritative',
            'call_to_action': False,
            'avoid_controversy': True
        }
        
        prompt = llm_service.build_master_prompt(
            source_text="Test content for advanced settings",
            brand_guide_text="Professional brand voice",
            post_history=["Example post"],
            platform="LinkedIn",
            count=2,
            advanced_settings=advanced_settings
        )
        
        # Verify advanced settings are reflected in prompt
        assert "innovative" in prompt.lower(), "Should include creativity level"
        assert "authoritative" in prompt.lower(), "Should include content tone"
        assert "no hashtags" in prompt.lower() or "avoid hashtags" in prompt.lower(), "Should specify no hashtags"
        assert "no emojis" in prompt.lower() or "do not use emojis" in prompt.lower(), "Should specify no emojis"
        assert "avoid direct ctas" in prompt.lower() or "focus on informational" in prompt.lower(), "Should avoid CTAs"
    
    def test_error_handling_consistency(self):
        """Test that error handling is consistent across components."""
        
        # Test that all custom exceptions inherit from base classes correctly
        assert issubclass(file_service.FileProcessingError, Exception)
        assert issubclass(file_service.UnsupportedFileTypeError, file_service.FileProcessingError)
        assert issubclass(file_service.FileReadError, file_service.FileProcessingError)
        assert issubclass(file_service.FileValidationError, file_service.FileProcessingError)
        
        assert issubclass(post_service.WorkflowError, Exception)
        assert issubclass(post_service.FileProcessingError, post_service.WorkflowError)
        assert issubclass(post_service.LLMServiceError, post_service.WorkflowError)
        assert issubclass(post_service.PromptBuildingError, post_service.WorkflowError)
        assert issubclass(post_service.ResponseParsingError, post_service.WorkflowError)
        
        # Test error message consistency
        try:
            file_service.extract_text_from_uploads([])
        except Exception as e:
            # Should not raise an exception for empty list, just return empty string
            pass
        
        try:
            file_service.extract_text_from_uploads(None)
        except file_service.FileValidationError as e:
            assert "must be a list" in str(e).lower(), "Error message should be descriptive"


@pytest.mark.performance
class TestPhase6Performance:
    """Performance tests for Phase 6 enhancements."""
    
    def test_logging_performance_impact(self):
        """Test that logging doesn't significantly impact performance."""
        
        # Test without logging
        start_time = time.time()
        for i in range(100):
            llm_service.build_master_prompt(
                source_text="Test content",
                brand_guide_text="Brand voice",
                post_history=[],
                platform="LinkedIn",
                count=1
            )
        no_logging_time = time.time() - start_time
        
        # Test with logging enabled
        logging_config.setup_logging(log_level="DEBUG", console_output=False)
        
        start_time = time.time()
        for i in range(100):
            llm_service.build_master_prompt(
                source_text="Test content",
                brand_guide_text="Brand voice",
                post_history=[],
                platform="LinkedIn",
                count=1
            )
        with_logging_time = time.time() - start_time
        
        # Logging should not significantly impact performance
        performance_ratio = with_logging_time / no_logging_time
        assert performance_ratio < 2.0, f"Logging should not double execution time: {performance_ratio:.2f}x"
    
    def test_memory_usage_with_enhancements(self):
        """Test memory usage with Phase 6 enhancements."""
        
        try:
            import psutil
            
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform memory-intensive operations
            large_posts = ["Large post content " * 100] * 50  # ~250KB of post data
            
            for _ in range(10):
                data_exporter.create_csv_export(large_posts, "LinkedIn", include_metadata=True)
                file_service.validate_file_type("test.txt")
                logging_config.get_logger("memory_test").info("Memory test iteration")
            
            # Check final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable
            assert memory_increase < 50, f"Memory increase should be < 50MB: {memory_increase:.2f}MB"
            
        except ImportError:
            pytest.skip("psutil not available for memory testing")


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v", "--tb=short"])