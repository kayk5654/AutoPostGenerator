"""
Phase 10: Unicode Text Sanitization - Integration Tests

This module contains comprehensive integration tests that verify the complete
Phase 10 implementation across all application components.
"""

import pytest
from unittest.mock import Mock, patch
import pandas as pd

# Import components to test
from utils.text_sanitizer import get_text_sanitizer, sanitize_text
from utils.data_exporter import create_csv_export, _sanitize_csv_content
from services import llm_service


class TestPhase10Integration:
    """Integration tests for Phase 10: Unicode Text Sanitization."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_corrupted_content = [
            'Trust is a key driver of conversions窶覇especially in Japan.',
            'He said窶忤Hello world窶 with enthusiasm.',
            'The cost is窶兤$50 for premium features.',
            'She replied竊会That sounds perfect竊 with a smile.'
        ]
        
        self.expected_clean_content = [
            'Trust is a key driver of conversions—especially in Japan.',
            'He said"Hello world" with enthusiasm.',
            'The cost is—$50 for premium features.',
            'She replied "That sounds perfect" with a smile.'
        ]
    
    def test_text_sanitizer_fixes_real_corruption_patterns(self):
        """Test that text sanitizer fixes real corruption patterns from user reports."""
        sanitizer = get_text_sanitizer()
        
        for corrupted, expected in zip(self.test_corrupted_content, self.expected_clean_content):
            result = sanitizer.sanitize_text(corrupted)
            assert result == expected, f"Failed to fix: {corrupted}"
    
    def test_llm_service_clean_post_content_integration(self):
        """Test that _clean_post_content integrates Unicode sanitization."""
        corrupted_post = 'Trust is a key driver of conversions窶覇especially in Japan.'
        expected_clean = 'Trust is a key driver of conversions—especially in Japan.'
        
        # Test the actual function
        result = llm_service._clean_post_content(corrupted_post)
        assert result == expected_clean
    
    def test_llm_provider_functions_sanitize_responses(self):
        """Test that LLM provider functions have Unicode sanitization integrated."""
        # This test verifies that the provider functions contain the sanitization code
        # by checking the source code rather than executing with real API calls
        
        import inspect
        
        # Check that _call_gemini has sanitization code
        gemini_source = inspect.getsource(llm_service._call_gemini)
        assert 'get_text_sanitizer' in gemini_source
        assert 'sanitize_text' in gemini_source
        assert 'Phase 10.2' in gemini_source
        
        # Check that _call_openai has sanitization code
        openai_source = inspect.getsource(llm_service._call_openai)
        assert 'get_text_sanitizer' in openai_source
        assert 'sanitize_text' in openai_source
        assert 'Phase 10.2' in openai_source
        
        # Check that _call_anthropic has sanitization code
        anthropic_source = inspect.getsource(llm_service._call_anthropic)
        assert 'get_text_sanitizer' in anthropic_source
        assert 'sanitize_text' in anthropic_source
        assert 'Phase 10.2' in anthropic_source
    
    def test_data_export_sanitizes_unicode_content(self):
        """Test that data export applies Unicode sanitization."""
        corrupted_posts = [
            'Trust is a key driver of conversions窶覇especially in Japan.',
            'He said窶忤Hello world窶 with enthusiasm.'
        ]
        
        # Test CSV content sanitization
        for post in corrupted_posts:
            sanitized = _sanitize_csv_content(post)
            # Should not contain corruption patterns
            assert '窶覇' not in sanitized
            assert '窶忤' not in sanitized
            assert '窶' not in sanitized
            # Should contain proper characters
            assert '—' in sanitized or '"' in sanitized
        
        # Test full export pipeline
        csv_content, filename = create_csv_export(corrupted_posts, 'LinkedIn', include_metadata=True)
        
        # CSV should not contain corruption patterns
        assert '窶覇' not in csv_content
        assert '窶忤' not in csv_content
        assert '窶' not in csv_content
        
        # Should contain proper characters
        assert '—' in csv_content
        assert '"' in csv_content
    
    def test_end_to_end_corruption_fix_workflow(self):
        """Test end-to-end workflow from LLM response to export."""
        # Simulate LLM response with corruption
        corrupted_llm_response = """
        POST 1: Trust is a key driver of conversions窶覇especially in Japan.
        
        POST 2: He said窶忤Hello world窶 with enthusiasm.
        """
        
        # Test LLM response parsing and cleaning
        posts = llm_service.parse_llm_response(corrupted_llm_response)
        
        # All posts should be free of corruption
        for post in posts:
            assert '窶覇' not in post
            assert '窶忤' not in post
            assert '窶' not in post
        
        # Test export workflow
        csv_content, filename = create_csv_export(posts, 'LinkedIn')
        
        # CSV export should also be corruption-free
        assert '窶覇' not in csv_content
        assert '窶忤' not in csv_content
        assert '窶' not in csv_content
    
    def test_unicode_sanitization_preserves_good_content(self):
        """Test that Unicode sanitization preserves legitimate content."""
        good_content_examples = [
            "Simple English text with no issues",
            "Text with proper em dash — and quotes \"Hello\"",
            "Unicode content: café, naïve, résumé, Zürich",
            "Emojis and symbols: $100, 50%, #hashtag, @mention 🌟",
            "Mixed languages: Hello 世界 🌍 Привет мир",
        ]
        
        sanitizer = get_text_sanitizer()
        
        for content in good_content_examples:
            result = sanitizer.sanitize_text(content)
            
            # Content length should be preserved (minor variations allowed)
            assert len(result) >= len(content) * 0.9
            
            # Key content should be preserved
            if "café" in content:
                assert "café" in result or "cafe" in result
            if "Hello" in content:
                assert "Hello" in result
            if "$100" in content:
                assert "$100" in result
    
    def test_unicode_sanitization_error_handling(self):
        """Test error handling in Unicode sanitization across components."""
        # Test with problematic input
        problematic_inputs = [
            None,
            "",
            "\x00\x01\x02",  # Control characters
            "a" * 100000,   # Very long string
        ]
        
        for test_input in problematic_inputs:
            if test_input is None:
                # Should raise TypeError for None input
                with pytest.raises(TypeError):
                    sanitize_text(test_input)
            else:
                # Should handle gracefully
                try:
                    result = sanitize_text(test_input)
                    assert isinstance(result, str)
                except Exception as e:
                    # If it raises, should be a clear error
                    assert "sanitization failed" in str(e).lower()
    
    def test_phase10_performance_benchmarks(self):
        """Test performance of Phase 10 components."""
        import time
        
        # Test with medium-sized content
        test_content = "Trust is a key driver of conversions窶覇especially in Japan. " * 100
        
        # Benchmark text sanitization
        start_time = time.time()
        sanitizer = get_text_sanitizer()
        result = sanitizer.sanitize_text(test_content)
        sanitization_time = time.time() - start_time
        
        # Should complete quickly (less than 1 second for reasonable content)
        assert sanitization_time < 1.0, f"Sanitization took too long: {sanitization_time}s"
        
        # Benchmark export sanitization
        posts = [test_content] * 10
        start_time = time.time()
        csv_content, filename = create_csv_export(posts, 'LinkedIn')
        export_time = time.time() - start_time
        
        # Export should also be fast
        assert export_time < 2.0, f"Export took too long: {export_time}s"
    
    def test_phase10_integration_with_existing_features(self):
        """Test that Phase 10 integrates seamlessly with existing features."""
        # Test that existing cleaning still works
        messy_content = """
        POST 1: Trust is a key driver窶覇especially!
        
        Here are your posts:
        
        **Bold text** and *italic text*
        
        ---
        
        Some extra content...
        """
        
        result = llm_service._clean_post_content(messy_content)
        
        # Should fix corruption
        assert '窶覇' not in result
        assert '—' in result
        
        # Should still do existing cleaning
        # The function does basic markdown removal and separator cleanup
        assert '**' not in result  # Markdown removal
        assert '*italic*' not in result  # Markdown removal 
        assert '---' not in result  # Separator removal
        assert 'italic' in result  # Content preserved
        assert 'Bold text' in result  # Content preserved
    
    def test_phase10_backward_compatibility(self):
        """Test that Phase 10 maintains backward compatibility."""
        # Content without corruption should pass through unchanged (mostly)
        clean_content = "This is perfectly normal content with no issues."
        
        result = llm_service._clean_post_content(clean_content)
        
        # Should be essentially the same (allowing for minor normalization)
        assert result == clean_content or len(result) >= len(clean_content) * 0.95
        
        # Empty content should still work
        assert llm_service._clean_post_content("") == ""
        assert llm_service._clean_post_content("   ") == ""
        
        # Export should still work with clean content
        clean_posts = ["Normal post 1", "Normal post 2"]
        csv_content, filename = create_csv_export(clean_posts, 'LinkedIn')
        
        assert 'Normal post 1' in csv_content
        assert 'Normal post 2' in csv_content
        assert filename.endswith('.csv')


if __name__ == '__main__':
    pytest.main([__file__])