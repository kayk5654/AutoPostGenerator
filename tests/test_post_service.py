import pytest
from unittest.mock import Mock, patch, MagicMock
from services.post_service import generate_posts_workflow


class TestGeneratePostsWorkflow:
    """Tests for generate_posts_workflow orchestration function."""
    
    @patch('services.post_service.llm_service')
    @patch('services.post_service.file_service')
    def test_workflow_orchestration_success(self, mock_file_service, mock_llm_service):
        """Test successful end-to-end workflow orchestration."""
        # Setup mocks
        mock_file_service.extract_text_from_uploads.side_effect = [
            "Source content text",  # source files
            "Brand guide content"   # brand guide
        ]
        mock_file_service.extract_posts_from_history.return_value = [
            "Historical post 1",
            "Historical post 2"
        ]
        mock_llm_service.build_master_prompt.return_value = "Constructed prompt"
        mock_llm_service.call_llm.return_value = "Raw LLM response"
        mock_llm_service.parse_llm_response.return_value = [
            "Generated post 1",
            "Generated post 2",
            "Generated post 3"
        ]
        
        # Mock uploaded files
        source_files = [Mock(name="file1.txt"), Mock(name="file2.pdf")]
        brand_guide = Mock(name="brand.docx")
        history_file = Mock(name="history.xlsx")
        
        # Execute workflow
        result = generate_posts_workflow(
            source_files=source_files,
            brand_guide=brand_guide,
            history_file=history_file,
            provider="Google Gemini",
            api_key="test-api-key",
            platform="LinkedIn",
            count=3
        )
        
        # Verify function calls in correct order
        mock_file_service.extract_text_from_uploads.assert_any_call(source_files)
        mock_file_service.extract_text_from_uploads.assert_any_call([brand_guide])
        mock_file_service.extract_posts_from_history.assert_called_once_with(history_file)
        mock_llm_service.build_master_prompt.assert_called_once_with(
            "Source content text",
            "Brand guide content", 
            ["Historical post 1", "Historical post 2"],
            "LinkedIn",
            3
        )
        mock_llm_service.call_llm.assert_called_once_with(
            "Google Gemini",
            "test-api-key",
            "Constructed prompt"
        )
        mock_llm_service.parse_llm_response.assert_called_once_with("Raw LLM response")
        
        # Verify result
        assert result == ["Generated post 1", "Generated post 2", "Generated post 3"]
        assert len(result) == 3
    
    @patch('services.post_service.llm_service')
    @patch('services.post_service.file_service')
    def test_workflow_with_different_providers(self, mock_file_service, mock_llm_service):
        """Test workflow with different LLM providers."""
        # Setup basic mocks
        mock_file_service.extract_text_from_uploads.side_effect = ["source", "brand"]
        mock_file_service.extract_posts_from_history.return_value = ["post"]
        mock_llm_service.build_master_prompt.return_value = "prompt"
        mock_llm_service.call_llm.return_value = "response"
        mock_llm_service.parse_llm_response.return_value = ["result"]
        
        providers = ["Google Gemini", "OpenAI", "Anthropic"]
        
        for provider in providers:
            result = generate_posts_workflow(
                source_files=[Mock()],
                brand_guide=Mock(),
                history_file=Mock(),
                provider=provider,
                api_key="test-key",
                platform="X",
                count=1
            )
            
            # Verify LLM called with correct provider
            mock_llm_service.call_llm.assert_called_with(provider, "test-key", "prompt")
            assert result == ["result"]
    
    @patch('services.post_service.llm_service')  
    @patch('services.post_service.file_service')
    def test_workflow_with_different_platforms(self, mock_file_service, mock_llm_service):
        """Test workflow with different target platforms."""
        # Setup basic mocks
        mock_file_service.extract_text_from_uploads.side_effect = ["source", "brand"]
        mock_file_service.extract_posts_from_history.return_value = ["post"]
        mock_llm_service.build_master_prompt.return_value = "prompt"
        mock_llm_service.call_llm.return_value = "response"
        mock_llm_service.parse_llm_response.return_value = ["result"]
        
        platforms = ["X", "Facebook", "LinkedIn", "Instagram"]
        
        for platform in platforms:
            result = generate_posts_workflow(
                source_files=[Mock()],
                brand_guide=Mock(),
                history_file=Mock(),
                provider="Google Gemini",
                api_key="test-key",
                platform=platform,
                count=1
            )
            
            # Verify prompt built with correct platform
            mock_llm_service.build_master_prompt.assert_called_with(
                "source", "brand", ["post"], platform, 1
            )
            assert result == ["result"]
    
    @patch('services.post_service.llm_service')
    @patch('services.post_service.file_service')
    def test_workflow_with_varying_post_counts(self, mock_file_service, mock_llm_service):
        """Test workflow with different post counts."""
        # Setup mocks
        mock_file_service.extract_text_from_uploads.side_effect = ["source", "brand"]
        mock_file_service.extract_posts_from_history.return_value = ["post"]
        mock_llm_service.build_master_prompt.return_value = "prompt"
        mock_llm_service.call_llm.return_value = "response"
        
        # Test different counts
        test_counts = [1, 5, 10]
        
        for count in test_counts:
            # Mock different number of posts returned
            mock_posts = [f"Post {i+1}" for i in range(count)]
            mock_llm_service.parse_llm_response.return_value = mock_posts
            
            result = generate_posts_workflow(
                source_files=[Mock()],
                brand_guide=Mock(),
                history_file=Mock(),
                provider="Google Gemini",
                api_key="test-key",
                platform="X",
                count=count
            )
            
            # Verify correct count passed to prompt builder
            mock_llm_service.build_master_prompt.assert_called_with(
                "source", "brand", ["post"], "X", count
            )
            assert len(result) == count
            assert result[0] == "Post 1"
    
    @patch('services.post_service.file_service')
    def test_workflow_file_service_error_propagation(self, mock_file_service):
        """Test that file service errors are properly propagated."""
        # Mock file service to raise error
        mock_file_service.extract_text_from_uploads.side_effect = Exception("File parsing error")
        
        with pytest.raises(Exception, match="File parsing error"):
            generate_posts_workflow(
                source_files=[Mock()],
                brand_guide=Mock(),
                history_file=Mock(),
                provider="Google Gemini",
                api_key="test-key",
                platform="X",
                count=1
            )
    
    @patch('services.post_service.llm_service')
    @patch('services.post_service.file_service')
    def test_workflow_llm_service_error_propagation(self, mock_file_service, mock_llm_service):
        """Test that LLM service errors are properly propagated."""
        # Setup file service mocks
        mock_file_service.extract_text_from_uploads.side_effect = ["source", "brand"]
        mock_file_service.extract_posts_from_history.return_value = ["post"]
        mock_llm_service.build_master_prompt.return_value = "prompt"
        
        # Mock LLM service to raise error
        mock_llm_service.call_llm.side_effect = Exception("API key invalid")
        
        with pytest.raises(Exception, match="API key invalid"):
            generate_posts_workflow(
                source_files=[Mock()],
                brand_guide=Mock(),
                history_file=Mock(),
                provider="Google Gemini",
                api_key="invalid-key",
                platform="X",
                count=1
            )
    
    @patch('services.post_service.llm_service')
    @patch('services.post_service.file_service')
    def test_workflow_prompt_construction_error(self, mock_file_service, mock_llm_service):
        """Test handling of prompt construction errors."""
        # Setup file service mocks
        mock_file_service.extract_text_from_uploads.side_effect = ["source", "brand"]
        mock_file_service.extract_posts_from_history.return_value = ["post"]
        
        # Mock prompt building to raise error
        mock_llm_service.build_master_prompt.side_effect = Exception("Prompt construction failed")
        
        with pytest.raises(Exception, match="Prompt construction failed"):
            generate_posts_workflow(
                source_files=[Mock()],
                brand_guide=Mock(),
                history_file=Mock(),
                provider="Google Gemini",
                api_key="test-key",
                platform="X",
                count=1
            )
    
    @patch('services.post_service.llm_service')
    @patch('services.post_service.file_service')
    def test_workflow_response_parsing_error(self, mock_file_service, mock_llm_service):
        """Test handling of response parsing errors."""
        # Setup mocks up to LLM call
        mock_file_service.extract_text_from_uploads.side_effect = ["source", "brand"]
        mock_file_service.extract_posts_from_history.return_value = ["post"]
        mock_llm_service.build_master_prompt.return_value = "prompt"
        mock_llm_service.call_llm.return_value = "malformed response"
        
        # Mock response parsing to raise error
        mock_llm_service.parse_llm_response.side_effect = Exception("Response parsing failed")
        
        with pytest.raises(Exception, match="Response parsing failed"):
            generate_posts_workflow(
                source_files=[Mock()],
                brand_guide=Mock(),
                history_file=Mock(),
                provider="Google Gemini",
                api_key="test-key",
                platform="X",
                count=1
            )
    
    def test_workflow_input_validation(self):
        """Test input validation for workflow function."""
        # Test with None values
        with pytest.raises(ValueError, match="source_files cannot be None"):
            generate_posts_workflow(
                source_files=None,
                brand_guide=Mock(),
                history_file=Mock(),
                provider="Google Gemini",
                api_key="test-key",
                platform="X",
                count=1
            )
        
        # Test with empty provider
        with pytest.raises(ValueError, match="provider cannot be empty"):
            generate_posts_workflow(
                source_files=[Mock()],
                brand_guide=Mock(),
                history_file=Mock(),
                provider="",
                api_key="test-key",
                platform="X",
                count=1
            )
        
        # Test with empty API key
        with pytest.raises(ValueError, match="api_key cannot be empty"):
            generate_posts_workflow(
                source_files=[Mock()],
                brand_guide=Mock(),
                history_file=Mock(),
                provider="Google Gemini",
                api_key="",
                platform="X",
                count=1
            )
        
        # Test with invalid count
        with pytest.raises(ValueError, match="count must be positive"):
            generate_posts_workflow(
                source_files=[Mock()],
                brand_guide=Mock(),
                history_file=Mock(),
                provider="Google Gemini",
                api_key="test-key",
                platform="X",
                count=0
            )
    
    @patch('services.post_service.llm_service')
    @patch('services.post_service.file_service')
    def test_workflow_empty_source_files(self, mock_file_service, mock_llm_service):
        """Test workflow handling of empty source files."""
        # Setup mocks with empty source content
        mock_file_service.extract_text_from_uploads.side_effect = ["", "brand guide"]
        mock_file_service.extract_posts_from_history.return_value = ["post"]
        mock_llm_service.build_master_prompt.return_value = "prompt"
        mock_llm_service.call_llm.return_value = "response"
        mock_llm_service.parse_llm_response.return_value = ["post"]
        
        result = generate_posts_workflow(
            source_files=[Mock()],
            brand_guide=Mock(),
            history_file=Mock(),
            provider="Google Gemini",
            api_key="test-key",
            platform="X",
            count=1
        )
        
        # Verify workflow continues with empty source content
        mock_llm_service.build_master_prompt.assert_called_once_with(
            "", "brand guide", ["post"], "X", 1
        )
        assert result == ["post"]
    
    @patch('services.post_service.llm_service')
    @patch('services.post_service.file_service')
    def test_workflow_empty_post_history(self, mock_file_service, mock_llm_service):
        """Test workflow handling of empty post history."""
        # Setup mocks with empty post history
        mock_file_service.extract_text_from_uploads.side_effect = ["source", "brand"]
        mock_file_service.extract_posts_from_history.return_value = []
        mock_llm_service.build_master_prompt.return_value = "prompt"
        mock_llm_service.call_llm.return_value = "response"
        mock_llm_service.parse_llm_response.return_value = ["post"]
        
        result = generate_posts_workflow(
            source_files=[Mock()], 
            brand_guide=Mock(),
            history_file=Mock(),
            provider="Google Gemini",
            api_key="test-key",
            platform="X",
            count=1
        )
        
        # Verify workflow continues with empty post history
        mock_llm_service.build_master_prompt.assert_called_once_with(
            "source", "brand", [], "X", 1
        )
        assert result == ["post"]
    
    @patch('services.post_service.llm_service')
    @patch('services.post_service.file_service')
    def test_workflow_logging_and_monitoring(self, mock_file_service, mock_llm_service):
        """Test that workflow provides proper logging for monitoring."""
        # Setup mocks
        mock_file_service.extract_text_from_uploads.side_effect = ["source", "brand"]
        mock_file_service.extract_posts_from_history.return_value = ["post"]
        mock_llm_service.build_master_prompt.return_value = "prompt"
        mock_llm_service.call_llm.return_value = "response"
        mock_llm_service.parse_llm_response.return_value = ["post1", "post2"]
        
        with patch('services.post_service.logging') as mock_logging:
            result = generate_posts_workflow(
                source_files=[Mock()],
                brand_guide=Mock(), 
                history_file=Mock(),
                provider="Google Gemini",
                api_key="test-key",
                platform="X",
                count=2
            )
            
            # Verify logging calls for monitoring
            assert mock_logging.info.call_count >= 2  # Start and completion logs
            assert result == ["post1", "post2"]


class TestWorkflowIntegration:
    """Integration tests for complete workflow scenarios."""
    
    @patch('services.post_service.llm_service')
    @patch('services.post_service.file_service')
    def test_realistic_workflow_scenario(self, mock_file_service, mock_llm_service):
        """Test realistic end-to-end scenario with complex data."""
        # Setup realistic mock data
        complex_source = """
        Product Launch: Revolutionary AI Assistant
        - Advanced natural language processing
        - 24/7 availability
        - Multi-language support
        - Integration with popular tools
        """
        
        brand_guide = """
        Brand Voice Guidelines:
        - Professional yet approachable
        - Emphasize innovation and reliability
        - Use inclusive language
        - Highlight customer benefits
        """
        
        post_history = [
            "Excited to share our latest innovation in AI technology! 🚀",
            "Customer feedback drives everything we do. Here's what you told us...",
            "Behind the scenes: How our team builds reliable AI solutions"
        ]
        
        expected_response = """POST 1: Revolutionary AI just got smarter! 🤖 Our new assistant brings advanced NLP and 24/7 support to your workflow. #Innovation #AI

POST 2: Breaking language barriers with our multi-language AI assistant. Now supporting 50+ languages for global teams! 🌍 #GlobalSupport

POST 3: Seamless integration meets powerful AI. Connect your favorite tools and let our assistant handle the rest. Ready to boost productivity? 💼"""
        
        # Configure mocks
        mock_file_service.extract_text_from_uploads.side_effect = [complex_source, brand_guide]
        mock_file_service.extract_posts_from_history.return_value = post_history
        mock_llm_service.build_master_prompt.return_value = "detailed_prompt"
        mock_llm_service.call_llm.return_value = expected_response
        mock_llm_service.parse_llm_response.return_value = [
            "Revolutionary AI just got smarter! 🤖 Our new assistant brings advanced NLP and 24/7 support to your workflow. #Innovation #AI",
            "Breaking language barriers with our multi-language AI assistant. Now supporting 50+ languages for global teams! 🌍 #GlobalSupport", 
            "Seamless integration meets powerful AI. Connect your favorite tools and let our assistant handle the rest. Ready to boost productivity? 💼"
        ]
        
        # Execute workflow
        result = generate_posts_workflow(
            source_files=[Mock(name="launch_announcement.pdf"), Mock(name="features.docx")],
            brand_guide=Mock(name="brand_guidelines.txt"),
            history_file=Mock(name="previous_posts.xlsx"),
            provider="Google Gemini",
            api_key="sk-test-key-realistic",
            platform="LinkedIn",
            count=3
        )
        
        # Verify realistic output
        assert len(result) == 3
        assert "🤖" in result[0]  # Emoji preserved
        assert "#Innovation" in result[0]  # Hashtags included
        assert "multi-language" in result[1]  # Key features mentioned
        assert "productivity" in result[2]  # Business benefits highlighted
        
        # Verify all services called with realistic data
        mock_llm_service.build_master_prompt.assert_called_once_with(
            complex_source, brand_guide, post_history, "LinkedIn", 3
        )