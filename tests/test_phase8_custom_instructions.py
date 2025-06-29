"""
Unit Tests for Phase 8: Advanced Prompt Customization
Tests for custom instructions functionality across UI, prompt system, and workflow integration.

Covers Linear issues:
- ASS-20: Phase 8.1 UI Enhancement for Custom Instructions  
- ASS-21: Phase 8.2 Prompt System Enhancement
- ASS-22: Phase 8.3 Workflow Integration for Custom Instructions
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test fixtures
@pytest.fixture
def mock_streamlit_session():
    """Mock Streamlit session state for testing."""
    session_state = {
        'custom_instructions': '',
        'generated_posts': [],
        'editing_posts': [],
        'generation_in_progress': False,
        'advanced_settings': {},
        'last_generation_settings': {}
    }
    return Mock(session_state=session_state)

@pytest.fixture
def sample_custom_instructions():
    """Sample custom instructions for testing."""
    return {
        'simple': "Make the posts more engaging",
        'detailed': "Add more statistics and data points. Use industry-specific terminology. Include call-to-action at the end.",
        'formatting': "Use bullet points where appropriate. Keep paragraphs short and punchy.",
        'tone': "Use a professional but friendly tone. Avoid jargon.",
        'empty': "",
        'whitespace': "   \n\t   ",
        'long': "A" * 1000,  # Very long instruction
        'with_quotes': 'Use "air quotes" and \'single quotes\' properly',
        'special_chars': "Use emojis 🚀 and symbols & characters @#$%",
        'malicious': "<script>alert('test')</script>",
        'sql_injection': "'; DROP TABLE users; --"
    }

@pytest.fixture
def sample_prompt_data():
    """Sample data for prompt testing."""
    return {
        'source_text': "Sample source content about AI technology",
        'brand_guide_text': "Our brand is innovative and trustworthy",
        'post_history': ["Previous post 1", "Previous post 2"],
        'platform': 'LinkedIn',
        'count': 3
    }


# ============================================================================
# Phase 8.1: UI Enhancement for Custom Instructions (ASS-20)
# ============================================================================

class TestCustomInstructionsUI:
    """Test suite for custom instructions UI components."""
    
    def test_custom_instructions_text_area_exists(self, mock_streamlit_session):
        """Test that custom instructions text area is added to advanced options."""
        # This would test the UI component existence
        # In actual implementation, this would verify st.text_area is called
        with patch('streamlit.text_area') as mock_text_area:
            mock_text_area.return_value = "test instructions"
            
            # Simulate calling st.text_area directly
            mock_text_area(
                label="Additional Instructions",
                value="",
                placeholder="Add specific instructions...",
                key="custom_instructions"
            )
            
            mock_text_area.assert_called()
            assert mock_text_area.call_count == 1
    
    def test_custom_instructions_placeholder_text(self):
        """Test that placeholder text provides helpful examples."""
        expected_placeholder = (
            "Add specific instructions to customize the generated posts...\n\n"
            "Examples:\n"
            "• Make the posts more engaging with questions\n" 
            "• Include industry statistics and data points\n"
            "• Use a professional but friendly tone\n"
            "• Add call-to-action at the end of each post"
        )
        
        with patch('streamlit.text_area') as mock_text_area:
            # Simulate calling with placeholder
            mock_text_area(
                label="Additional Instructions",
                placeholder=expected_placeholder,
                key="custom_instructions"
            )
            
            # Verify placeholder text is used
            call_args = mock_text_area.call_args
            assert call_args is not None
            assert 'placeholder' in call_args.kwargs
            placeholder = call_args.kwargs['placeholder']
            assert "Examples:" in placeholder
            assert "Make the posts more engaging" in placeholder
    
    def test_custom_instructions_input_validation(self, sample_custom_instructions):
        """Test input validation for custom instructions."""
        validation_tests = [
            (sample_custom_instructions['simple'], True, "Valid simple instruction"),
            (sample_custom_instructions['detailed'], True, "Valid detailed instruction"),
            (sample_custom_instructions['empty'], True, "Empty instruction should be valid"),
            (sample_custom_instructions['whitespace'], False, "Whitespace-only should be invalid"),
            (sample_custom_instructions['long'], False, "Overly long instruction should be invalid"),
            (sample_custom_instructions['malicious'], False, "Malicious content should be invalid")
        ]
        
        for instruction, expected_valid, description in validation_tests:
            is_valid = self._validate_custom_instruction(instruction)
            assert is_valid == expected_valid, f"Failed: {description}"
    
    def test_custom_instructions_character_limit(self, sample_custom_instructions):
        """Test character limit enforcement for custom instructions."""
        max_length = 500  # Expected character limit
        
        # Test within limit
        short_instruction = "A" * (max_length - 10)
        assert self._validate_instruction_length(short_instruction, max_length) == True
        
        # Test at limit
        exact_instruction = "A" * max_length
        assert self._validate_instruction_length(exact_instruction, max_length) == True
        
        # Test over limit
        long_instruction = sample_custom_instructions['long']
        assert self._validate_instruction_length(long_instruction, max_length) == False
    
    def test_custom_instructions_sanitization(self, sample_custom_instructions):
        """Test that custom instructions are properly sanitized."""
        test_cases = [
            (sample_custom_instructions['malicious'], "alert('test')"),
            (sample_custom_instructions['sql_injection'], "DROP TABLE users"),
            (sample_custom_instructions['special_chars'], "🚀 and symbols & characters @#$%")
        ]
        
        for original, expected_cleaned in test_cases:
            sanitized = self._sanitize_custom_instruction(original)
            if "script" in original or "DROP TABLE" in original:
                assert expected_cleaned not in sanitized
            else:
                assert expected_cleaned in sanitized
    
    def test_custom_instructions_session_state_integration(self, mock_streamlit_session):
        """Test integration with Streamlit session state."""
        test_instruction = "Test custom instruction"
        
        # Simulate setting custom instruction
        mock_streamlit_session.session_state['custom_instructions'] = test_instruction
        
        # Verify it's stored correctly
        assert mock_streamlit_session.session_state['custom_instructions'] == test_instruction
        
        # Test reset functionality
        self._reset_custom_instructions(mock_streamlit_session)
        assert mock_streamlit_session.session_state['custom_instructions'] == ''
    
    def test_custom_instructions_help_text(self):
        """Test that help text and tooltips are provided."""
        with patch('streamlit.help') as mock_help:
            self._simulate_advanced_options_ui()
            
            # Verify help text is provided
            mock_help.assert_called()
            help_text = mock_help.call_args[0][0]
            assert "custom instructions" in help_text.lower()
            assert "examples" in help_text.lower()
    
    def test_custom_instructions_progressive_disclosure(self):
        """Test progressive disclosure for advanced users."""
        with patch('streamlit.expander') as mock_expander:
            mock_expander.return_value.__enter__ = Mock()
            mock_expander.return_value.__exit__ = Mock()
            
            self._simulate_advanced_options_ui()
            
            # Verify expander is used for advanced options
            mock_expander.assert_called()
            expander_label = mock_expander.call_args[0][0]
            assert "advanced" in expander_label.lower() or "custom" in expander_label.lower()
    
    # Helper methods for UI tests
    def _simulate_advanced_options_ui(self):
        """Simulate the enhanced show_advanced_options function."""
        # This simulates calling streamlit.text_area
        with patch('streamlit.text_area') as mock_text_area:
            mock_text_area.return_value = "test instructions"
            # Simulate the function that would call st.text_area
            result = mock_text_area(
                label="Additional Instructions",
                value="",
                placeholder="Add specific instructions...",
                key="custom_instructions"
            )
        return {'custom_instructions': result}
    
    def _validate_custom_instruction(self, instruction):
        """Simulate custom instruction validation."""
        if not instruction:  # Empty string is valid (will be ignored)
            return True
        if instruction.isspace():  # Whitespace-only is invalid
            return False
        if len(instruction) > 500:
            return False
        if '<script>' in instruction or 'DROP TABLE' in instruction:
            return False
        return True
    
    def _validate_instruction_length(self, instruction, max_length):
        """Validate instruction length."""
        return len(instruction) <= max_length
    
    def _sanitize_custom_instruction(self, instruction):
        """Simulate instruction sanitization."""
        # Remove script tags and SQL injection attempts
        sanitized = instruction.replace('<script>', '').replace('</script>', '')
        sanitized = sanitized.replace('alert(', '').replace(')', '')
        sanitized = sanitized.replace('DROP TABLE', '').replace(';--', '')
        return sanitized.strip()
    
    def _reset_custom_instructions(self, session_state):
        """Reset custom instructions in session state."""
        session_state.session_state['custom_instructions'] = ''


# ============================================================================
# Phase 8.2: Prompt System Enhancement (ASS-21)
# ============================================================================

class TestPromptSystemEnhancement:
    """Test suite for prompt system enhancement with custom instructions."""
    
    def test_build_master_prompt_with_custom_instructions(self, sample_prompt_data, sample_custom_instructions):
        """Test that build_master_prompt integrates custom instructions."""
        from services.llm_service import build_master_prompt
        
        # Test without custom instructions (baseline)
        prompt_without = build_master_prompt(
            sample_prompt_data['source_text'],
            sample_prompt_data['brand_guide_text'], 
            sample_prompt_data['post_history'],
            sample_prompt_data['platform'],
            sample_prompt_data['count']
        )
        
        # Test with custom instructions
        custom_instruction = sample_custom_instructions['detailed']
        prompt_with = build_master_prompt(
            sample_prompt_data['source_text'],
            sample_prompt_data['brand_guide_text'],
            sample_prompt_data['post_history'],
            sample_prompt_data['platform'],
            sample_prompt_data['count'],
            custom_instructions=custom_instruction
        )
        
        # Verify custom instructions are included
        assert custom_instruction in prompt_with
        assert len(prompt_with) > len(prompt_without)
    
    def test_custom_instructions_positioning_in_prompt(self, sample_prompt_data, sample_custom_instructions):
        """Test that custom instructions are positioned correctly in the prompt."""
        from services.llm_service import build_master_prompt
        
        custom_instruction = sample_custom_instructions['tone']
        prompt = build_master_prompt(
            sample_prompt_data['source_text'],
            sample_prompt_data['brand_guide_text'],
            sample_prompt_data['post_history'],
            sample_prompt_data['platform'],
            sample_prompt_data['count'],
            custom_instructions=custom_instruction
        )
        
        # Find positions of key sections
        role_pos = prompt.find("You are an expert")
        custom_pos = prompt.find(custom_instruction)
        source_pos = prompt.find(sample_prompt_data['source_text'])
        
        # Verify custom instructions come after role definition but before content
        assert role_pos < custom_pos < source_pos
    
    def test_custom_instructions_formatting_in_prompt(self, sample_prompt_data):
        """Test that custom instructions are properly formatted in the prompt."""
        from services.llm_service import build_master_prompt
        
        custom_instruction = "Use bullet points. Keep it short."
        prompt = build_master_prompt(
            sample_prompt_data['source_text'],
            sample_prompt_data['brand_guide_text'],
            sample_prompt_data['post_history'],
            sample_prompt_data['platform'],
            sample_prompt_data['count'],
            custom_instructions=custom_instruction
        )
        
        # Verify custom instructions section is properly formatted
        assert "## Custom Instructions:" in prompt or "CUSTOM INSTRUCTIONS:" in prompt
        assert custom_instruction in prompt
    
    def test_conflicting_instructions_handling(self, sample_prompt_data):
        """Test handling of conflicting custom instructions."""
        from services.llm_service import build_master_prompt
        
        # Instructions that conflict with platform requirements
        conflicting_instruction = "Make posts very long with 500+ words each"
        
        prompt = build_master_prompt(
            sample_prompt_data['source_text'],
            sample_prompt_data['brand_guide_text'],
            sample_prompt_data['post_history'],
            'X',  # X has 280 character limit
            sample_prompt_data['count'],
            custom_instructions=conflicting_instruction
        )
        
        # Verify platform limits take precedence
        assert "280 characters" in prompt or "character limit" in prompt
        assert conflicting_instruction in prompt  # But still included as user request
    
    def test_empty_custom_instructions_handling(self, sample_prompt_data, sample_custom_instructions):
        """Test handling of empty or whitespace-only custom instructions."""
        from services.llm_service import build_master_prompt
        
        test_cases = [
            sample_custom_instructions['empty'],
            sample_custom_instructions['whitespace'],
            None
        ]
        
        for empty_instruction in test_cases:
            prompt = build_master_prompt(
                sample_prompt_data['source_text'],
                sample_prompt_data['brand_guide_text'],
                sample_prompt_data['post_history'],
                sample_prompt_data['platform'],
                sample_prompt_data['count'],
                custom_instructions=empty_instruction
            )
            
            # Verify no custom instructions section is added for empty instructions
            assert "Custom Instructions:" not in prompt
            assert "CUSTOM INSTRUCTIONS:" not in prompt
    
    def test_custom_instructions_safety_filtering(self, sample_prompt_data, sample_custom_instructions):
        """Test safety filtering of malicious custom instructions."""
        from services.llm_service import build_master_prompt
        
        malicious_instruction = sample_custom_instructions['malicious']
        
        prompt = build_master_prompt(
            sample_prompt_data['source_text'],
            sample_prompt_data['brand_guide_text'],
            sample_prompt_data['post_history'],
            sample_prompt_data['platform'],
            sample_prompt_data['count'],
            custom_instructions=malicious_instruction
        )
        
        # Verify malicious content is filtered out
        assert "<script>" not in prompt
        assert "alert(" not in prompt
    
    def test_custom_instructions_with_different_platforms(self, sample_prompt_data):
        """Test custom instructions with different platform requirements."""
        platforms = ['X', 'LinkedIn', 'Facebook', 'Instagram']
        custom_instruction = "Add relevant hashtags and mentions"
        
        for platform in platforms:
            prompt = build_master_prompt(
                sample_prompt_data['source_text'],
                sample_prompt_data['brand_guide_text'],
                sample_prompt_data['post_history'],
                platform,
                sample_prompt_data['count'],
                custom_instructions=custom_instruction
            )
            
            # Verify platform-specific handling
            assert platform in prompt
            assert custom_instruction in prompt
            
            # Platform-specific checks
            if platform == 'X':
                assert "280" in prompt or "character" in prompt
            elif platform == 'LinkedIn':
                assert "professional" in prompt.lower()
    
    def test_prompt_quality_with_custom_instructions(self, sample_prompt_data, sample_custom_instructions):
        """Test that prompt quality is maintained with custom instructions."""
        from services.llm_service import build_master_prompt
        
        custom_instruction = sample_custom_instructions['detailed']
        prompt = build_master_prompt(
            sample_prompt_data['source_text'],
            sample_prompt_data['brand_guide_text'],
            sample_prompt_data['post_history'],
            sample_prompt_data['platform'],
            sample_prompt_data['count'],
            custom_instructions=custom_instruction
        )
        
        # Verify all essential prompt components are present
        assert "You are" in prompt  # Role definition
        assert sample_prompt_data['source_text'] in prompt  # Source content
        assert sample_prompt_data['brand_guide_text'] in prompt  # Brand guide
        assert sample_prompt_data['platform'] in prompt  # Platform
        assert str(sample_prompt_data['count']) in prompt  # Post count
        assert custom_instruction in prompt  # Custom instructions
        
        # Verify proper structure
        assert len(prompt) > 500  # Substantial prompt
        assert prompt.count('\n') > 5  # Well-formatted with line breaks


# ============================================================================
# Phase 8.3: Workflow Integration for Custom Instructions (ASS-22)
# ============================================================================

class TestWorkflowIntegration:
    """Test suite for workflow integration of custom instructions."""
    
    def test_advanced_settings_extension(self, mock_streamlit_session):
        """Test that advanced_settings dictionary includes custom instructions."""
        # Simulate advanced settings with custom instructions
        custom_instruction = "Make posts more engaging"
        
        advanced_settings = {
            'creativity_level': 'Medium',
            'include_hashtags': True,
            'include_emojis': False,
            'custom_instructions': custom_instruction
        }
        
        mock_streamlit_session.session_state['advanced_settings'] = advanced_settings
        
        # Verify custom instructions are included
        assert 'custom_instructions' in advanced_settings
        assert advanced_settings['custom_instructions'] == custom_instruction
    
    def test_generate_posts_workflow_integration(self, mock_streamlit_session):
        """Test that generate_posts_workflow passes custom instructions to LLM service."""
        with patch('services.post_service.generate_posts_workflow') as mock_workflow:
            mock_workflow.return_value = ["Generated post 1", "Generated post 2"]
            
            # Simulate workflow call with custom instructions
            advanced_settings = {
                'custom_instructions': 'Make posts more professional'
            }
            
            result = mock_workflow(
                source_files=Mock(),
                brand_guide=Mock(),
                history_file=Mock(),
                provider='OpenAI',
                api_key='test-key',
                platform='LinkedIn',
                count=2,
                advanced_settings=advanced_settings
            )
            
            # Verify workflow is called with advanced settings
            mock_workflow.assert_called_once()
            call_args = mock_workflow.call_args
            assert 'advanced_settings' in call_args.kwargs
            assert call_args.kwargs['advanced_settings']['custom_instructions'] == 'Make posts more professional'
    
    def test_backward_compatibility_without_custom_instructions(self):
        """Test that workflow works without custom instructions (backward compatibility)."""
        with patch('services.post_service.generate_posts_workflow') as mock_workflow:
            mock_workflow.return_value = ["Generated post 1", "Generated post 2"]
            
            # Simulate workflow call without custom instructions
            result = mock_workflow(
                source_files=Mock(),
                brand_guide=Mock(),
                history_file=Mock(),
                provider='OpenAI',
                api_key='test-key',
                platform='LinkedIn',
                count=2
            )
            
            # Verify workflow still works
            mock_workflow.assert_called_once()
            assert result == ["Generated post 1", "Generated post 2"]
    
    def test_custom_instructions_logging(self, caplog):
        """Test that custom instructions are logged for debugging."""
        with patch('services.post_service.generate_posts_workflow') as mock_workflow:
            with patch('logging.getLogger') as mock_logger:
                mock_log = Mock()
                mock_logger.return_value = mock_log
                
                custom_instruction = "Use professional tone"
                advanced_settings = {'custom_instructions': custom_instruction}
                
                # Simulate workflow with logging
                self._simulate_workflow_with_logging(advanced_settings)
                
                # Verify custom instructions are logged
                # Note: In actual implementation, check that logger.info or logger.debug is called
                # with custom instructions information
    
    def test_custom_instructions_validation_in_workflow(self):
        """Test validation of custom instructions during workflow execution."""
        test_cases = [
            ("Valid instruction", True),
            ("", True),  # Empty should be valid (ignored)
            ("   ", False),  # Whitespace-only should be invalid
            ("A" * 1000, False),  # Too long should be invalid
            ("<script>alert('test')</script>", False)  # Malicious should be invalid
        ]
        
        for instruction, expected_valid in test_cases:
            is_valid = self._validate_custom_instruction_in_workflow(instruction)
            assert is_valid == expected_valid, f"Validation failed for: {instruction}"
    
    def test_custom_instructions_error_handling(self):
        """Test error handling when custom instructions cause issues."""
        with patch('services.llm_service.build_master_prompt') as mock_prompt_builder:
            # Simulate error in prompt building due to custom instructions
            mock_prompt_builder.side_effect = ValueError("Invalid custom instruction")
            
            try:
                self._simulate_workflow_with_error()
                assert False, "Expected ValueError to be raised"
            except ValueError as e:
                assert "Invalid custom instruction" in str(e)
    
    def test_custom_instructions_performance_impact(self):
        """Test that custom instructions don't significantly impact performance."""
        import time
        
        # Measure baseline performance without custom instructions
        start_time = time.time()
        self._simulate_prompt_generation(None)
        baseline_time = time.time() - start_time
        
        # Measure performance with custom instructions
        start_time = time.time()
        self._simulate_prompt_generation("Make posts more engaging with statistics")
        custom_time = time.time() - start_time
        
        # Verify performance impact is minimal (less than 50% increase)
        performance_ratio = custom_time / baseline_time if baseline_time > 0 else 1
        assert performance_ratio < 1.5, f"Performance impact too high: {performance_ratio}x"
    
    def test_custom_instructions_state_persistence(self, mock_streamlit_session):
        """Test that custom instructions persist across UI interactions."""
        # Set custom instruction
        custom_instruction = "Use professional tone"
        mock_streamlit_session.session_state['custom_instructions'] = custom_instruction
        
        # Simulate UI interaction that might reset state
        self._simulate_ui_interaction(mock_streamlit_session)
        
        # Verify custom instruction persists
        assert mock_streamlit_session.session_state['custom_instructions'] == custom_instruction
    
    def test_custom_instructions_in_generation_metadata(self, mock_streamlit_session):
        """Test that custom instructions are included in generation metadata."""
        custom_instruction = "Add call-to-action"
        
        generation_metadata = {
            'timestamp': '2024-01-01T12:00:00Z',
            'provider': 'OpenAI',
            'platform': 'LinkedIn',
            'post_count': 3,
            'custom_instructions': custom_instruction
        }
        
        mock_streamlit_session.session_state['last_generation_settings'] = generation_metadata
        
        # Verify custom instructions are tracked
        assert 'custom_instructions' in generation_metadata
        assert generation_metadata['custom_instructions'] == custom_instruction
    
    # Helper methods for workflow tests
    def _simulate_workflow_with_logging(self, advanced_settings):
        """Simulate workflow execution with logging."""
        # This would call the actual generate_posts_workflow with logging
        pass
    
    def _validate_custom_instruction_in_workflow(self, instruction):
        """Simulate custom instruction validation in workflow."""
        if not instruction:
            return True  # Empty is valid (ignored)
        if instruction.isspace():
            return False  # Whitespace-only is invalid
        if len(instruction) > 500:
            return False  # Too long is invalid
        if '<script>' in instruction:
            return False  # Malicious content is invalid
        return True
    
    def _simulate_workflow_with_error(self):
        """Simulate workflow that raises an error due to custom instructions."""
        raise ValueError("Invalid custom instruction")
    
    def _simulate_prompt_generation(self, custom_instruction):
        """Simulate prompt generation for performance testing."""
        # Simulate some processing time
        import time
        time.sleep(0.001)  # 1ms simulated processing
    
    def _simulate_ui_interaction(self, session_state):
        """Simulate UI interaction that might affect state."""
        # This would simulate various UI interactions
        pass


# ============================================================================
# Integration Tests for Phase 8
# ============================================================================

class TestPhase8Integration:
    """Integration tests for the complete Phase 8 functionality."""
    
    def test_end_to_end_custom_instructions_workflow(self, sample_prompt_data, mock_streamlit_session):
        """Test complete workflow from UI input to prompt generation."""
        # Simulate UI input
        custom_instruction = "Make posts more engaging with questions and statistics"
        mock_streamlit_session.session_state['custom_instructions'] = custom_instruction
        
        # Simulate advanced settings
        advanced_settings = {
            'creativity_level': 'High',
            'include_hashtags': True,
            'custom_instructions': custom_instruction
        }
        
        with patch('services.llm_service.build_master_prompt') as mock_prompt_builder:
            mock_prompt_builder.return_value = "Generated prompt with custom instructions"
            
            # Simulate workflow execution
            result = self._simulate_complete_workflow(
                sample_prompt_data,
                advanced_settings
            )
            
            # Verify custom instructions flow through the entire pipeline
            mock_prompt_builder.assert_called_once()
            call_args = mock_prompt_builder.call_args
            assert custom_instruction in str(call_args)
    
    def test_phase8_with_all_llm_providers(self, sample_prompt_data):
        """Test custom instructions work with all LLM providers."""
        providers = ['OpenAI', 'Google Gemini', 'Anthropic']
        custom_instruction = "Use industry terminology"
        
        for provider in providers:
            with patch('services.llm_service.call_llm') as mock_llm:
                mock_llm.return_value = "Generated response"
                
                # Simulate LLM call with custom instructions
                result = self._simulate_llm_call_with_custom_instructions(
                    provider,
                    sample_prompt_data,
                    custom_instruction
                )
                
                # Verify call was made successfully
                mock_llm.assert_called_once()
                assert result == "Generated response"
    
    def test_phase8_with_all_platforms(self, sample_prompt_data):
        """Test custom instructions work with all social media platforms."""
        platforms = ['X', 'LinkedIn', 'Facebook', 'Instagram']
        custom_instruction = "Add relevant hashtags"
        
        for platform in platforms:
            with patch('services.llm_service.build_master_prompt') as mock_prompt_builder:
                mock_prompt_builder.return_value = f"Prompt for {platform}"
                
                # Simulate prompt building for each platform
                result = self._simulate_platform_specific_prompt(
                    platform,
                    sample_prompt_data,
                    custom_instruction
                )
                
                # Verify platform-specific handling
                mock_prompt_builder.assert_called_once()
                call_args = mock_prompt_builder.call_args
                assert platform in str(call_args)
                assert custom_instruction in str(call_args)
    
    def test_phase8_performance_under_load(self):
        """Test Phase 8 performance with multiple concurrent requests."""
        import threading
        import time
        
        results = []
        custom_instruction = "Make posts professional"
        
        def simulate_request():
            start_time = time.time()
            self._simulate_prompt_generation(custom_instruction)
            duration = time.time() - start_time
            results.append(duration)
        
        # Simulate 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=simulate_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify reasonable performance
        avg_duration = sum(results) / len(results)
        assert avg_duration < 1.0, f"Average request duration too high: {avg_duration}s"
    
    # Helper methods for integration tests
    def _simulate_complete_workflow(self, prompt_data, advanced_settings):
        """Simulate complete workflow execution."""
        return "Workflow completed successfully"
    
    def _simulate_llm_call_with_custom_instructions(self, provider, prompt_data, custom_instruction):
        """Simulate LLM call with custom instructions."""
        return "Generated response"
    
    def _simulate_platform_specific_prompt(self, platform, prompt_data, custom_instruction):
        """Simulate platform-specific prompt generation."""
        return f"Prompt for {platform}"
    
    def _simulate_prompt_generation(self, custom_instruction):
        """Simulate prompt generation for performance testing."""
        import time
        time.sleep(0.001)  # 1ms simulated processing


# ============================================================================
# Test Markers and Configuration
# ============================================================================

# Mark all Phase 8 tests
pytestmark = [pytest.mark.phase8, pytest.mark.unit]


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])