import pytest
from unittest.mock import Mock, patch, MagicMock
from services.llm_service import (
    build_master_prompt,
    call_llm,
    parse_llm_response,
    _call_gemini,
    _call_openai,
    _call_anthropic
)


class TestBuildMasterPrompt:
    """Tests for build_master_prompt function."""
    
    def test_build_prompt_with_all_components(self):
        """Test that prompt includes all required components."""
        source_text = "New product launch announcement"
        brand_guide_text = "Brand voice: Professional yet approachable"
        post_history = ["Previous post 1", "Previous post 2"]
        platform = "LinkedIn"
        count = 3
        
        result = build_master_prompt(source_text, brand_guide_text, post_history, platform, count)
        
        # Test that all components are included in prompt
        assert "Professional yet approachable" in result
        assert "New product launch announcement" in result
        assert "Previous post 1" in result
        assert "LinkedIn" in result
        assert "3" in result or "three" in result.lower()
    
    def test_build_prompt_role_definition(self):
        """Test that prompt includes role definition for AI."""
        result = build_master_prompt("content", "guide", ["post"], "X", 1)
        
        # Should define AI role as social media content creator
        assert "social media" in result.lower() and "content creator" in result.lower()
    
    def test_build_prompt_brand_guide_integration(self):
        """Test brand guide integration in prompt."""
        brand_guide = "Voice: Casual and friendly. Avoid technical jargon."
        result = build_master_prompt("content", brand_guide, ["post"], "X", 1)
        
        assert "Casual and friendly" in result
        assert "technical jargon" in result
    
    def test_build_prompt_post_history_examples(self):
        """Test that post history is included as style reference."""
        post_history = ["Great update on our progress! #innovation", "Excited to share our latest features"]
        result = build_master_prompt("content", "guide", post_history, "X", 1)
        
        assert "#innovation" in result
        assert "Excited to share" in result
    
    def test_build_prompt_platform_requirements(self):
        """Test platform-specific formatting rules."""
        result_x = build_master_prompt("content", "guide", ["post"], "X", 1)
        result_linkedin = build_master_prompt("content", "guide", ["post"], "LinkedIn", 1)
        
        # X should mention character limits and hashtags
        assert "280" in result_x or "character" in result_x.lower()
        
        # LinkedIn should mention professional tone
        assert "professional" in result_linkedin.lower()
    
    def test_build_prompt_generation_instructions(self):
        """Test clear instructions for number of posts."""
        result = build_master_prompt("content", "guide", ["post"], "X", 5)
        
        assert "5" in result or "five" in result.lower()
        assert "generate" in result.lower() or "create" in result.lower()
    
    def test_build_prompt_output_format_specification(self):
        """Test that prompt specifies how to separate posts."""
        result = build_master_prompt("content", "guide", ["post"], "X", 2)
        
        # Should specify separation format
        assert "---" in result or "separate" in result.lower() or "POST" in result
    
    def test_build_prompt_empty_inputs(self):
        """Test handling of empty inputs."""
        result = build_master_prompt("", "", [], "X", 1)
        
        # Should still generate a valid prompt structure
        assert len(result) > 0
        assert "X" in result
        assert "1" in result or "one" in result.lower()
    
    def test_build_prompt_special_characters(self):
        """Test handling of special characters in inputs."""
        source_text = "Content with émojis 🚀 and special chars: @#$%"
        brand_guide_text = "Voice: Use émojis sparingly & maintain professionalism"
        
        result = build_master_prompt(source_text, brand_guide_text, ["post"], "X", 1)
        
        assert "🚀" in result
        assert "émojis" in result
        assert "@#$%" in result


class TestCallLLM:
    """Tests for call_llm factory function."""
    
    @patch('services.llm_service._call_gemini')
    def test_call_llm_routes_to_gemini(self, mock_gemini):
        """Test routing to Gemini provider."""
        mock_gemini.return_value = "Generated content"
        
        result = call_llm("Google Gemini", "api-key-123", "test prompt")
        
        mock_gemini.assert_called_once_with("api-key-123", "test prompt")
        assert result == "Generated content"
    
    @patch('services.llm_service._call_openai')
    def test_call_llm_routes_to_openai(self, mock_openai):
        """Test routing to OpenAI provider."""
        mock_openai.return_value = "Generated content"
        
        result = call_llm("OpenAI", "api-key-456", "test prompt")
        
        mock_openai.assert_called_once_with("api-key-456", "test prompt")
        assert result == "Generated content"
    
    @patch('services.llm_service._call_anthropic')
    def test_call_llm_routes_to_anthropic(self, mock_anthropic):
        """Test routing to Anthropic provider."""
        mock_anthropic.return_value = "Generated content"
        
        result = call_llm("Anthropic", "api-key-789", "test prompt")
        
        mock_anthropic.assert_called_once_with("api-key-789", "test prompt")
        assert result == "Generated content"
    
    def test_call_llm_invalid_provider(self):
        """Test handling of invalid provider."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            call_llm("InvalidProvider", "api-key", "prompt")
    
    def test_call_llm_empty_api_key(self):
        """Test handling of empty API key."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            call_llm("Google Gemini", "", "prompt")
    
    def test_call_llm_empty_prompt(self):
        """Test handling of empty prompt."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            call_llm("Google Gemini", "api-key", "")


class TestParseResponseLLM:
    """Tests for parse_llm_response function."""
    
    def test_parse_response_with_dashes(self):
        """Test parsing response separated by dashes."""
        response = """Post 1: Great update on our progress!
---
Post 2: Excited to share our latest features
---
Post 3: Join us for the upcoming event"""
        
        result = parse_llm_response(response)
        
        assert len(result) == 3
        assert "Great update on our progress!" in result[0]
        assert "Excited to share our latest features" in result[1]
        assert "Join us for the upcoming event" in result[2]
    
    def test_parse_response_with_post_numbers(self):
        """Test parsing response with POST N: format."""
        response = """POST 1: First social media post content here

POST 2: Second social media post content here

POST 3: Third social media post content here"""
        
        result = parse_llm_response(response)
        
        assert len(result) == 3
        assert "First social media post" in result[0]
        assert "Second social media post" in result[1]
        assert "Third social media post" in result[2]
    
    def test_parse_response_with_numbered_format(self):
        """Test parsing response with 1. 2. 3. format."""
        response = """1. First post content with hashtags #innovation

2. Second post content about features

3. Third post content for engagement"""
        
        result = parse_llm_response(response)
        
        assert len(result) == 3
        assert "#innovation" in result[0]
        assert "features" in result[1]
        assert "engagement" in result[2]
    
    def test_parse_response_single_post(self):
        """Test parsing single post response."""
        response = "Single post content without separators"
        
        result = parse_llm_response(response)
        
        assert len(result) == 1
        assert result[0] == "Single post content without separators"
    
    def test_parse_response_whitespace_cleaning(self):
        """Test whitespace cleaning in parsed posts."""
        response = """   POST 1: Content with extra spaces   

POST 2:     Another post    
   
POST 3: Final post   """
        
        result = parse_llm_response(response)
        
        assert len(result) == 3
        assert result[0] == "Content with extra spaces"
        assert result[1] == "Another post"
        assert result[2] == "Final post"
    
    def test_parse_response_empty_posts_filtered(self):
        """Test that empty posts are filtered out."""
        response = """POST 1: Valid content
---

---
POST 2: Another valid post
---

"""
        
        result = parse_llm_response(response)
        
        assert len(result) == 2
        assert "Valid content" in result[0]
        assert "Another valid post" in result[1]
    
    def test_parse_response_malformed_response(self):
        """Test handling of malformed response."""
        response = "Malformed response without proper separators or format"
        
        result = parse_llm_response(response)
        
        # Should return single post or handle gracefully
        assert len(result) >= 1
        assert "Malformed response" in result[0]


class TestCallGemini:
    """Tests for _call_gemini function."""
    
    @patch('services.llm_service.genai')
    def test_call_gemini_success(self, mock_genai):
        """Test successful Gemini API call."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Generated content from Gemini"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        result = _call_gemini("api-key-123", "test prompt")
        
        mock_genai.configure.assert_called_once_with(api_key="api-key-123")
        mock_genai.GenerativeModel.assert_called_once()
        mock_model.generate_content.assert_called_once_with("test prompt")
        assert result == "Generated content from Gemini"
    
    @patch('services.llm_service.genai')
    def test_call_gemini_invalid_api_key(self, mock_genai):
        """Test Gemini API call with invalid API key."""
        mock_genai.configure.side_effect = Exception("Invalid API key")
        
        with pytest.raises(Exception, match="Invalid API key"):
            _call_gemini("invalid-key", "test prompt")
    
    @patch('services.llm_service.genai')
    def test_call_gemini_api_error(self, mock_genai):
        """Test Gemini API error handling."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API rate limit exceeded")
        mock_genai.GenerativeModel.return_value = mock_model
        
        with pytest.raises(Exception, match="API rate limit exceeded"):
            _call_gemini("api-key", "test prompt")


class TestCallOpenAI:
    """Tests for _call_openai function."""
    
    @patch('services.llm_service.OpenAI')
    def test_call_openai_success(self, mock_openai_class):
        """Test successful OpenAI API call."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Generated content from OpenAI"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        result = _call_openai("api-key-456", "test prompt")
        
        mock_openai_class.assert_called_once_with(api_key="api-key-456")
        mock_client.chat.completions.create.assert_called_once()
        assert result == "Generated content from OpenAI"
    
    @patch('services.llm_service.OpenAI')
    def test_call_openai_invalid_api_key(self, mock_openai_class):
        """Test OpenAI API call with invalid API key."""
        mock_openai_class.side_effect = Exception("Invalid API key")
        
        with pytest.raises(Exception, match="Invalid API key"):
            _call_openai("invalid-key", "test prompt")
    
    @patch('services.llm_service.OpenAI')
    def test_call_openai_quota_exceeded(self, mock_openai_class):
        """Test OpenAI quota exceeded error."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Quota exceeded")
        mock_openai_class.return_value = mock_client
        
        with pytest.raises(Exception, match="Quota exceeded"):
            _call_openai("api-key", "test prompt")


class TestCallAnthropic:
    """Tests for _call_anthropic function."""
    
    @patch('services.llm_service.anthropic')
    def test_call_anthropic_success(self, mock_anthropic):
        """Test successful Anthropic API call."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content[0].text = "Generated content from Claude"
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client
        
        result = _call_anthropic("api-key-789", "test prompt")
        
        mock_anthropic.Anthropic.assert_called_once_with(api_key="api-key-789")
        mock_client.messages.create.assert_called_once()
        assert result == "Generated content from Claude"
    
    @patch('services.llm_service.anthropic')
    def test_call_anthropic_invalid_api_key(self, mock_anthropic):
        """Test Anthropic API call with invalid API key."""
        mock_anthropic.Anthropic.side_effect = Exception("Invalid API key")
        
        with pytest.raises(Exception, match="Invalid API key"):
            _call_anthropic("invalid-key", "test prompt")
    
    @patch('services.llm_service.anthropic')
    def test_call_anthropic_rate_limit(self, mock_anthropic):
        """Test Anthropic rate limit error."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("Rate limit exceeded")
        mock_anthropic.Anthropic.return_value = mock_client
        
        with pytest.raises(Exception, match="Rate limit exceeded"):
            _call_anthropic("api-key", "test prompt")


class TestLLMServiceIntegration:
    """Integration tests for LLM service functions."""
    
    @patch('services.llm_service._call_gemini')
    def test_end_to_end_workflow(self, mock_gemini):
        """Test complete workflow from prompt building to response parsing."""
        # Setup
        mock_gemini.return_value = """POST 1: Great update on our progress! #innovation

POST 2: Excited to share our latest features

POST 3: Join us for the upcoming event"""
        
        # Build prompt
        source_text = "New product launch"
        brand_guide_text = "Professional tone"
        post_history = ["Previous post example"]
        platform = "LinkedIn"
        count = 3
        
        prompt = build_master_prompt(source_text, brand_guide_text, post_history, platform, count)
        
        # Call LLM
        response = call_llm("Google Gemini", "test-api-key", prompt)
        
        # Parse response
        posts = parse_llm_response(response)
        
        # Verify
        assert len(posts) == 3
        assert "Great update on our progress!" in posts[0]
        assert "Excited to share our latest features" in posts[1]
        assert "Join us for the upcoming event" in posts[2]
        
        mock_gemini.assert_called_once_with("test-api-key", prompt)
    
    def test_prompt_quality_validation(self):
        """Test that generated prompts meet quality standards."""
        prompt = build_master_prompt(
            "Launch new AI feature",
            "Voice: Professional, innovative, customer-focused",
            ["We're excited to announce...", "Innovation drives us..."],
            "LinkedIn",
            2
        )
        
        # Verify prompt structure and content quality
        assert len(prompt) > 200  # Substantial prompt
        assert "professional" in prompt.lower()
        assert "linkedin" in prompt.lower()
        assert "AI feature" in prompt
        assert "customer-focused" in prompt
        assert "2" in prompt or "two" in prompt.lower()
        
        # Verify prompt contains clear sections
        sections = ["role", "brand", "history", "platform", "generate"]
        matching_sections = sum(1 for section in sections if section in prompt.lower())
        assert matching_sections >= 3  # At least 3 key sections present