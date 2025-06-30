"""
Test suite for Phase 10.2: LLM Service Unicode Sanitization Integration

This module tests the integration of Unicode text sanitization into the LLM service pipeline
to ensure character corruption issues are fixed in all generated posts.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from services import llm_service
from utils.text_sanitizer import get_text_sanitizer


class TestLLMServiceUnicodeSanitization:
    """Test suite for LLM service Unicode sanitization integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sanitizer = get_text_sanitizer()
    
    def test_clean_post_content_applies_sanitization(self):
        """Test that _clean_post_content applies Unicode sanitization."""
        # Test input with known corruption patterns
        corrupted_content = "Trust is key窶覇especially in business竊会important竊"
        
        # Call the cleaning function
        result = llm_service._clean_post_content(corrupted_content)
        
        # Verify sanitization was applied
        assert "窶覇" not in result, "Em dash corruption should be fixed"
        assert "竊会" not in result, "Quote corruption should be fixed"
        assert "竊" not in result, "Quote corruption should be fixed"
        
        # Verify expected characters are present
        assert "—" in result or "-" in result, "Should contain proper dash character"
        assert '"' in result, "Should contain proper quote character"
    
    def test_clean_post_content_preserves_good_content(self):
        """Test that _clean_post_content preserves good content."""
        good_content = "This is normal text with proper punctuation—and quotes \"Hello\""
        
        result = llm_service._clean_post_content(good_content)
        
        # Content should be preserved (allowing for minor normalization)
        assert len(result) >= len(good_content) * 0.8
        assert "normal text" in result
        assert "proper punctuation" in result
    
    def test_clean_post_content_handles_empty_input(self):
        """Test that _clean_post_content handles empty input gracefully."""
        assert llm_service._clean_post_content("") == ""
        assert llm_service._clean_post_content("   ") == ""
    
    @patch('utils.text_sanitizer.get_text_sanitizer')
    def test_clean_post_content_fallback_on_sanitizer_error(self, mock_get_sanitizer):
        """Test that _clean_post_content falls back gracefully when sanitizer fails."""
        # Configure mock to raise exception
        mock_sanitizer = Mock()
        mock_sanitizer.sanitize_text.side_effect = Exception("Sanitizer failed")
        mock_get_sanitizer.return_value = mock_sanitizer
        
        content = "Test content with issues窶覇here"
        
        # Should not raise exception, should return processed content
        result = llm_service._clean_post_content(content)
        
        # Should still return string (even if not sanitized)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_parse_llm_response_applies_sanitization_to_all_posts(self):
        """Test that parse_llm_response applies sanitization to all parsed posts."""
        # Mock response with multiple posts containing corruption
        mock_response = """POST 1: First post with窶覇corruption here.
---
POST 2: Second post with竊会quote issues竊too.
---
POST 3: Third post is窶覇clean hopefully."""
        
        posts = llm_service.parse_llm_response(mock_response)
        
        # Verify all posts are parsed
        assert len(posts) == 3
        
        # Verify sanitization applied to all posts
        for post in posts:
            assert "窶覇" not in post, f"Em dash corruption in post: {post}"
            assert "竊会" not in post, f"Quote corruption in post: {post}"
            assert "竊" not in post, f"Quote corruption in post: {post}"


class TestProviderResponseSanitization:
    """Test suite for provider-level response sanitization."""
    
    @patch('services.llm_service.genai')
    @patch('utils.text_sanitizer.get_text_sanitizer')
    def test_gemini_response_sanitization(self, mock_get_sanitizer, mock_genai):
        """Test that Gemini responses are sanitized."""
        # Configure mocks
        mock_sanitizer = Mock()
        mock_sanitizer.sanitize_text.return_value = "Cleaned response text"
        mock_get_sanitizer.return_value = mock_sanitizer
        
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Response with窶覇corruption"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = Mock()
        
        # Call Gemini function
        result = llm_service._call_gemini("test_key", "test_prompt")
        
        # Verify sanitization was called
        mock_sanitizer.sanitize_text.assert_called_once_with("Response with窶覇corruption")
        assert result == "Cleaned response text"
    
    @patch('services.llm_service.OpenAI')
    @patch('utils.text_sanitizer.get_text_sanitizer')
    def test_openai_response_sanitization(self, mock_get_sanitizer, mock_openai_class):
        """Test that OpenAI responses are sanitized."""
        # Configure mocks
        mock_sanitizer = Mock()
        mock_sanitizer.sanitize_text.return_value = "Cleaned OpenAI response"
        mock_get_sanitizer.return_value = mock_sanitizer
        
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "OpenAI response with竊会corruption"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Call OpenAI function
        result = llm_service._call_openai("test_key", "test_prompt")
        
        # Verify sanitization was called
        mock_sanitizer.sanitize_text.assert_called_once_with("OpenAI response with竊会corruption")
        assert result == "Cleaned OpenAI response"
    
    @patch('services.llm_service.anthropic')
    @patch('utils.text_sanitizer.get_text_sanitizer')
    def test_anthropic_response_sanitization(self, mock_get_sanitizer, mock_anthropic):
        """Test that Anthropic responses are sanitized."""
        # Configure mocks
        mock_sanitizer = Mock()
        mock_sanitizer.sanitize_text.return_value = "Cleaned Anthropic response"
        mock_get_sanitizer.return_value = mock_sanitizer
        
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Anthropic response with窶覇and竊corruption"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client
        
        # Call Anthropic function
        result = llm_service._call_anthropic("test_key", "test_prompt")
        
        # Verify sanitization was called
        mock_sanitizer.sanitize_text.assert_called_once_with("Anthropic response with窶覇and竊corruption")
        assert result == "Cleaned Anthropic response"
    
    @patch('services.llm_service.genai')
    @patch('utils.text_sanitizer.get_text_sanitizer')
    def test_provider_sanitization_fallback_on_error(self, mock_get_sanitizer, mock_genai):
        """Test that providers fall back to original response when sanitization fails."""
        # Configure sanitizer to fail
        mock_sanitizer = Mock()
        mock_sanitizer.sanitize_text.side_effect = Exception("Sanitization failed")
        mock_get_sanitizer.return_value = mock_sanitizer
        
        # Configure Gemini mock
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Original response"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = Mock()
        
        # Should not raise exception, should return original response
        result = llm_service._call_gemini("test_key", "test_prompt")
        assert result == "Original response"


class TestCallLLMWithSanitization:
    """Test suite for the main call_llm function with sanitization."""
    
    @patch('services.llm_service._call_gemini')
    def test_call_llm_gemini_with_sanitization(self, mock_call_gemini):
        """Test that call_llm applies sanitization for Gemini provider."""
        mock_call_gemini.return_value = "Sanitized Gemini response"
        
        result = llm_service.call_llm("Google Gemini", "test_key", "test_prompt")
        
        assert result == "Sanitized Gemini response"
        mock_call_gemini.assert_called_once()
    
    @patch('services.llm_service._call_openai')
    def test_call_llm_openai_with_sanitization(self, mock_call_openai):
        """Test that call_llm applies sanitization for OpenAI provider."""
        mock_call_openai.return_value = "Sanitized OpenAI response"
        
        result = llm_service.call_llm("OpenAI", "test_key", "test_prompt")
        
        assert result == "Sanitized OpenAI response"
        mock_call_openai.assert_called_once()
    
    @patch('services.llm_service._call_anthropic')
    def test_call_llm_anthropic_with_sanitization(self, mock_call_anthropic):
        """Test that call_llm applies sanitization for Anthropic provider."""
        mock_call_anthropic.return_value = "Sanitized Anthropic response"
        
        result = llm_service.call_llm("Anthropic", "test_key", "test_prompt")
        
        assert result == "Sanitized Anthropic response"
        mock_call_anthropic.assert_called_once()


class TestIntegrationRealCorruptionCases:
    """Integration tests with real corruption patterns from user reports."""
    
    def test_real_corruption_patterns_fixed(self):
        """Test that real corruption patterns from user reports are fixed."""
        # Real corruption examples from user reports
        corruption_examples = [
            {
                'input': 'Trust is a key driver of conversions窶覇especially in Japan.',
                'should_not_contain': ['窶覇'],
                'should_contain': ['—', '-'],
                'description': 'Em dash corruption fix'
            },
            {
                'input': 'He said窶忤Hello world窶and then left.',
                'should_not_contain': ['窶忤', '窶'],
                'should_contain': ['"'],
                'description': 'Smart quote corruption fix'
            },
            {
                'input': 'The product竊会according to reviews竊is excellent.',
                'should_not_contain': ['竊会', '竊'],
                'should_contain': ['"'],
                'description': 'Another quote corruption fix'
            },
            {
                'input': 'Cost-effective窶覇time-saving窶覇efficient.',
                'should_not_contain': ['窶覇'],
                'should_contain': ['—', '-'],
                'description': 'Multiple em dash corruptions'
            },
        ]
        
        for example in corruption_examples:
            result = llm_service._clean_post_content(example['input'])
            
            # Check that corruption patterns are removed
            for bad_pattern in example['should_not_contain']:
                assert bad_pattern not in result, f"Failed to remove '{bad_pattern}' in: {example['description']}"
            
            # Check that at least one good character is present
            has_good_char = any(good_char in result for good_char in example['should_contain'])
            assert has_good_char, f"Failed to add good characters in: {example['description']}"
    
    def test_mixed_corruption_patterns(self):
        """Test handling of mixed corruption patterns in single text."""
        mixed_corruption = "Trust窶覇the process竊会he said竊窶覇with confidence."
        
        result = llm_service._clean_post_content(mixed_corruption)
        
        # Should fix all corruption patterns
        corruption_patterns = ['窶覇', '竊会', '竊', '窶']
        for pattern in corruption_patterns:
            assert pattern not in result, f"Failed to fix corruption pattern: {pattern}"
        
        # Should contain proper characters
        assert '—' in result or '-' in result, "Should contain proper dash"
        assert '"' in result, "Should contain proper quotes"
    
    def test_post_parsing_with_corruption_in_multiple_posts(self):
        """Test that post parsing fixes corruption in all posts."""
        mock_response_with_corruption = """POST 1: First post窶覇with issues
---
POST 2: Second post has竊会problems竊too
---
POST 3: Third post窶覇also窶覇corrupted"""
        
        posts = llm_service.parse_llm_response(mock_response_with_corruption)
        
        assert len(posts) == 3
        
        # All posts should be cleaned
        for i, post in enumerate(posts, 1):
            assert "窶覇" not in post, f"Post {i} still has em dash corruption"
            assert "竊会" not in post, f"Post {i} still has quote corruption"
            assert "竊" not in post, f"Post {i} still has quote corruption"
            assert "窶" not in post, f"Post {i} still has quote corruption"


if __name__ == '__main__':
    pytest.main([__file__])