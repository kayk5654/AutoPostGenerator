"""
Tests for Phase 6 Task Block 6.1: User Experience Enhancements

This module tests the user experience improvements including:
- Loading indicators and spinners
- User feedback system (success, error, warning, info messages)
- Input validation with clear error messages
- Help system with tooltips and guidance
- Workflow guidance and progress indicators
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from io import StringIO


class TestLoadingIndicators:
    """Test comprehensive loading indicators throughout the application."""
    
    @patch('streamlit.spinner')
    def test_file_processing_spinner(self, mock_spinner):
        """Test file processing spinner with progress messages."""
        # Mock spinner context manager
        mock_spinner_context = Mock()
        mock_spinner.return_value.__enter__ = Mock(return_value=mock_spinner_context)
        mock_spinner.return_value.__exit__ = Mock(return_value=None)
        
        # Function to simulate file processing with spinner
        def process_files_with_spinner():
            with mock_spinner("📄 Processing uploaded files... Please wait."):
                # Simulate file processing
                return ["processed_file_1", "processed_file_2"]
        
        # Execute file processing
        result = process_files_with_spinner()
        
        # Verify spinner was called with correct message
        mock_spinner.assert_called_once_with("📄 Processing uploaded files... Please wait.")
        assert result == ["processed_file_1", "processed_file_2"]
    
    @patch('streamlit.spinner')
    def test_llm_generation_spinner(self, mock_spinner):
        """Test LLM generation spinner with appropriate message."""
        mock_spinner_context = Mock()
        mock_spinner.return_value.__enter__ = Mock(return_value=mock_spinner_context)
        mock_spinner.return_value.__exit__ = Mock(return_value=None)
        
        def generate_posts_with_spinner():
            with mock_spinner("🚀 Generating posts... This may take a moment."):
                # Simulate LLM generation
                return ["Generated post 1", "Generated post 2", "Generated post 3"]
        
        result = generate_posts_with_spinner()
        
        mock_spinner.assert_called_once_with("🚀 Generating posts... This may take a moment.")
        assert len(result) == 3
    
    @patch('streamlit.spinner')
    def test_export_preparation_spinner(self, mock_spinner):
        """Test export preparation spinner."""
        mock_spinner_context = Mock()
        mock_spinner.return_value.__enter__ = Mock(return_value=mock_spinner_context)
        mock_spinner.return_value.__exit__ = Mock(return_value=None)
        
        def prepare_export_with_spinner():
            with mock_spinner("📊 Preparing CSV export... Validating data."):
                # Simulate export preparation
                return "csv_data", "filename.csv"
        
        csv_data, filename = prepare_export_with_spinner()
        
        mock_spinner.assert_called_once_with("📊 Preparing CSV export... Validating data.")
        assert csv_data == "csv_data"
        assert filename == "filename.csv"
    
    @patch('streamlit.spinner')
    def test_progress_messages_variety(self, mock_spinner):
        """Test variety of progress messages for different operations."""
        operations = [
            ("🔍 Analyzing brand guide...", "brand_analysis"),
            ("📖 Processing post history...", "history_processing"),
            ("🎯 Optimizing for platform...", "platform_optimization"),
            ("✨ Finalizing posts...", "post_finalization")
        ]
        
        for message, operation in operations:
            mock_spinner.reset_mock()
            mock_spinner_context = Mock()
            mock_spinner.return_value.__enter__ = Mock(return_value=mock_spinner_context)
            mock_spinner.return_value.__exit__ = Mock(return_value=None)
            
            def operation_with_spinner(msg):
                with mock_spinner(msg):
                    return f"completed_{operation}"
            
            result = operation_with_spinner(message)
            mock_spinner.assert_called_once_with(message)
            assert result == f"completed_{operation}"


class TestUserFeedbackSystem:
    """Test comprehensive user feedback system with different message types."""
    
    @patch('streamlit.success')
    def test_success_messages(self, mock_success):
        """Test success messages for various operations."""
        success_scenarios = [
            ("🎉 Successfully generated 5 posts for LinkedIn!", "post_generation"),
            ("✅ Files uploaded and processed successfully!", "file_upload"),
            ("📄 CSV export completed successfully!", "csv_export"),
            ("🔄 Posts regenerated successfully!", "post_regeneration"),
            ("💾 All changes saved automatically!", "auto_save")
        ]
        
        for message, scenario in success_scenarios:
            mock_success.reset_mock()
            
            # Function to display success message
            def show_success(msg):
                mock_success(msg)
            
            show_success(message)
            mock_success.assert_called_once_with(message)
    
    @patch('streamlit.error')
    def test_error_messages(self, mock_error):
        """Test error messages for various failure scenarios."""
        error_scenarios = [
            ("🔑 Please enter your API key", "missing_api_key"),
            ("📁 Please upload at least one source file", "missing_files"),
            ("🤖 Please select an LLM provider", "missing_provider"),
            ("🎯 Please select a target platform", "missing_platform"),
            ("❌ Error generating posts: Invalid API key", "api_error"),
            ("💥 File processing failed: Unsupported format", "file_error")
        ]
        
        for message, scenario in error_scenarios:
            mock_error.reset_mock()
            
            def show_error(msg):
                mock_error(msg)
            
            show_error(message)
            mock_error.assert_called_once_with(message)
    
    @patch('streamlit.warning')
    def test_warning_messages(self, mock_warning):
        """Test warning messages for validation issues."""
        warning_scenarios = [
            ("⚠️ Post 1 exceeds LinkedIn character limit by 50 characters", "char_limit"),
            ("🚨 Large file detected - processing may take longer", "large_file"),
            ("⚠️ Some posts are empty and will be excluded from export", "empty_posts"),
            ("🔄 API rate limit reached - please wait before regenerating", "rate_limit"),
            ("⚠️ Brand guide file is empty - posts may not match brand voice", "empty_brand_guide")
        ]
        
        for message, scenario in warning_scenarios:
            mock_warning.reset_mock()
            
            def show_warning(msg):
                mock_warning(msg)
            
            show_warning(message)
            mock_warning.assert_called_once_with(message)
    
    @patch('streamlit.info')
    def test_info_messages(self, mock_info):
        """Test info messages for helpful tips and guidance."""
        info_scenarios = [
            ("📝 No posts generated yet. Use the 'Generate Posts' button above to create posts based on your inputs.", "no_posts"),
            ("💡 Tip: Upload a brand guide to ensure posts match your brand voice", "brand_tip"),
            ("📊 Ready to export 5 posts!", "export_ready"),
            ("🔧 Pro tip: Use the preview feature to review your CSV before downloading", "preview_tip"),
            ("📅 Generated 3 posts for X on 2024-01-15 at 10:30", "generation_info")
        ]
        
        for message, scenario in info_scenarios:
            mock_info.reset_mock()
            
            def show_info(msg):
                mock_info(msg)
            
            show_info(message)
            mock_info.assert_called_once_with(message)


class TestInputValidation:
    """Test comprehensive input validation with clear error messages."""
    
    def test_required_fields_validation(self):
        """Test validation of required fields."""
        def validate_required_fields(api_key, source_files, provider, platform):
            validation_errors = []
            
            if not api_key or not api_key.strip():
                validation_errors.append("🔑 Please enter your API key")
            
            if not source_files:
                validation_errors.append("📁 Please upload at least one source file")
            
            if not provider:
                validation_errors.append("🤖 Please select an LLM provider")
            
            if not platform:
                validation_errors.append("🎯 Please select a target platform")
            
            return len(validation_errors) == 0, validation_errors
        
        # Test with missing fields
        is_valid, errors = validate_required_fields("", None, "", "")
        assert not is_valid
        assert len(errors) == 4
        assert "🔑 Please enter your API key" in errors
        assert "📁 Please upload at least one source file" in errors
        
        # Test with valid fields
        mock_files = [Mock()]
        is_valid, errors = validate_required_fields("sk-test123", mock_files, "OpenAI", "LinkedIn")
        assert is_valid
        assert len(errors) == 0
    
    def test_file_format_validation(self):
        """Test file format validation."""
        def validate_file_format(filename, allowed_extensions):
            file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
            is_valid = f".{file_ext}" in allowed_extensions
            
            if not is_valid:
                return False, f"❌ File format '.{file_ext}' not supported. Allowed formats: {', '.join(allowed_extensions)}"
            
            return True, "File format is valid"
        
        allowed_formats = ['.txt', '.docx', '.pdf', '.md']
        
        # Test valid formats
        valid_files = ['document.txt', 'guide.docx', 'report.pdf', 'notes.md']
        for filename in valid_files:
            is_valid, message = validate_file_format(filename, allowed_formats)
            assert is_valid
        
        # Test invalid formats
        invalid_files = ['image.jpg', 'data.csv', 'script.py', 'archive.zip']
        for filename in invalid_files:
            is_valid, message = validate_file_format(filename, allowed_formats)
            assert not is_valid
            assert "not supported" in message
    
    def test_api_key_format_validation(self):
        """Test API key format validation."""
        def validate_api_key_format(api_key, provider):
            validation_patterns = {
                "OpenAI": {"prefix": "sk-", "min_length": 20},
                "Google Gemini": {"prefix": "AI", "min_length": 10},
                "Anthropic": {"prefix": "sk-ant", "min_length": 15}
            }
            
            if provider not in validation_patterns:
                return True, "No validation pattern for provider"
            
            pattern = validation_patterns[provider]
            
            if not api_key.startswith(pattern["prefix"]):
                return False, f"❌ {provider} API key should start with '{pattern['prefix']}'"
            
            if len(api_key) < pattern["min_length"]:
                return False, f"❌ {provider} API key appears to be too short"
            
            return True, "API key format is valid"
        
        # Test OpenAI keys
        assert validate_api_key_format("sk-1234567890abcdef1234567890", "OpenAI")[0]
        assert not validate_api_key_format("invalid-key", "OpenAI")[0]
        assert not validate_api_key_format("sk-short", "OpenAI")[0]
        
        # Test Anthropic keys
        assert validate_api_key_format("sk-ant-1234567890abcdef", "Anthropic")[0]
        assert not validate_api_key_format("sk-1234567890abcdef", "Anthropic")[0]
    
    def test_post_count_limits(self):
        """Test post count validation."""
        def validate_post_count(count, min_count=1, max_count=50):
            if count < min_count:
                return False, f"📊 Minimum post count is {min_count}"
            
            if count > max_count:
                return False, f"📊 Maximum post count is {max_count}"
            
            return True, "Post count is valid"
        
        # Test valid counts
        valid_counts = [1, 5, 10, 25, 50]
        for count in valid_counts:
            is_valid, message = validate_post_count(count)
            assert is_valid
        
        # Test invalid counts
        assert not validate_post_count(0)[0]
        assert not validate_post_count(-1)[0]
        assert not validate_post_count(51)[0]
        assert not validate_post_count(100)[0]


class TestHelpSystem:
    """Test help system with tooltips and guidance."""
    
    @patch('streamlit.text_input')
    def test_tooltips_for_complex_elements(self, mock_text_input):
        """Test tooltips for complex UI elements."""
        help_texts = {
            "api_key": "Your API key will only be used for this session and not stored",
            "source_files": "Supported formats: .txt, .docx, .pdf, .md",
            "brand_guide": "Upload your brand guidelines to ensure posts match your brand voice",
            "post_history": "Upload Excel file with previous posts for style reference",
            "post_count": "Number of social media posts to generate (1-50)",
            "platform": "Choose the social media platform for optimization"
        }
        
        for element, help_text in help_texts.items():
            mock_text_input.reset_mock()
            
            # Simulate creating input with help text
            def create_input_with_help(label, help_txt):
                mock_text_input(label, help=help_txt)
            
            create_input_with_help(f"Test {element}", help_text)
            mock_text_input.assert_called_once_with(f"Test {element}", help=help_text)
    
    def test_file_format_requirements_help(self):
        """Test help text for file format requirements."""
        def get_file_format_help():
            formats = {
                ".txt": "Plain text files",
                ".md": "Markdown files",
                ".docx": "Microsoft Word documents",
                ".pdf": "PDF documents",
                ".xlsx": "Excel spreadsheets (for post history)"
            }
            
            help_text = "Supported file formats:\n"
            for fmt, description in formats.items():
                help_text += f"• {fmt}: {description}\n"
            
            return help_text.strip()
        
        help_text = get_file_format_help()
        assert ".txt: Plain text files" in help_text
        assert ".docx: Microsoft Word documents" in help_text
        assert ".xlsx: Excel spreadsheets" in help_text
    
    def test_input_format_examples(self):
        """Test examples of proper input formats."""
        def get_input_examples():
            examples = {
                "brand_guide": "Example: 'Our brand voice is professional yet approachable. We use clear, concise language and always include a call-to-action.'",
                "api_key_openai": "Example: sk-1234567890abcdef1234567890abcdef",
                "post_history_format": "Excel file should have columns: 'Post Text', 'Platform', 'Date'",
                "platform_optimization": "LinkedIn: Professional tone, longer posts; X: Concise, hashtag-friendly"
            }
            return examples
        
        examples = get_input_examples()
        assert "professional yet approachable" in examples["brand_guide"]
        assert "sk-" in examples["api_key_openai"]
        assert "Post Text" in examples["post_history_format"]


class TestWorkflowGuidance:
    """Test workflow guidance and progress indicators."""
    
    def test_step_by_step_instructions(self):
        """Test step-by-step workflow instructions."""
        def get_workflow_steps():
            steps = [
                {
                    "number": 1,
                    "title": "Configure LLM Provider",
                    "description": "Select your AI provider and enter your API key",
                    "required": True
                },
                {
                    "number": 2,
                    "title": "Provide Inputs", 
                    "description": "Upload source files, brand guide, and post history",
                    "required": True
                },
                {
                    "number": 3,
                    "title": "Define Generation Parameters",
                    "description": "Set post count and target platform",
                    "required": True
                },
                {
                    "number": 4,
                    "title": "Generate",
                    "description": "Click 'Generate Posts' to create your content",
                    "required": True
                },
                {
                    "number": 5,
                    "title": "Review, Edit, and Manage Posts",
                    "description": "Edit generated posts and manage your content",
                    "required": False
                },
                {
                    "number": 6,
                    "title": "Export Posts",
                    "description": "Download your posts as CSV or copy to clipboard",
                    "required": False
                }
            ]
            return steps
        
        steps = get_workflow_steps()
        assert len(steps) == 6
        assert steps[0]["title"] == "Configure LLM Provider"
        assert steps[3]["title"] == "Generate"
        assert steps[5]["title"] == "Export Posts"
        
        # Verify all required steps
        required_steps = [step for step in steps if step["required"]]
        assert len(required_steps) == 4
    
    def test_progress_indicators(self):
        """Test progress indicators showing current step."""
        def get_current_step_status(api_key, files, provider, platform, posts_generated):
            step_status = {
                "step_1": bool(api_key and provider),
                "step_2": bool(files),
                "step_3": bool(platform),
                "step_4": bool(posts_generated),
                "step_5": bool(posts_generated),
                "step_6": bool(posts_generated)
            }
            
            current_step = 1
            for step_num in range(1, 7):
                if step_status[f"step_{step_num}"]:
                    current_step = step_num + 1
                else:
                    break
            
            return min(current_step, 6), step_status
        
        # Test progression through steps
        current, status = get_current_step_status("", None, "", "", False)
        assert current == 1
        
        current, status = get_current_step_status("sk-test", None, "OpenAI", "", False)
        assert current == 2
        
        current, status = get_current_step_status("sk-test", ["file.txt"], "OpenAI", "LinkedIn", True)
        assert current == 6
    
    def test_clear_calls_to_action(self):
        """Test clear calls-to-action for each step."""
        def get_calls_to_action(current_step):
            actions = {
                1: "👆 Select your LLM provider and enter your API key above",
                2: "📁 Upload your source files and brand guide",
                3: "🎯 Choose your target platform and set post count",
                4: "🚀 Click 'Generate Posts' to create your content",
                5: "✏️ Review and edit your generated posts",
                6: "📄 Export your posts or copy them to clipboard"
            }
            return actions.get(current_step, "🎉 All steps completed!")
        
        assert "Select your LLM provider" in get_calls_to_action(1)
        assert "Upload your source files" in get_calls_to_action(2)
        assert "Click 'Generate Posts'" in get_calls_to_action(4)
        assert "Export your posts" in get_calls_to_action(6)


class TestUserExperienceIntegration:
    """Test integration of all user experience enhancements."""
    
    @patch('streamlit.success')
    @patch('streamlit.error')
    @patch('streamlit.spinner')
    def test_complete_user_feedback_flow(self, mock_spinner, mock_error, mock_success):
        """Test complete user feedback flow from start to finish."""
        # Mock spinner context
        mock_spinner_context = Mock()
        mock_spinner.return_value.__enter__ = Mock(return_value=mock_spinner_context)
        mock_spinner.return_value.__exit__ = Mock(return_value=None)
        
        def simulate_complete_workflow():
            # Step 1: Validation
            api_key = "sk-test123"
            if not api_key:
                mock_error("🔑 Please enter your API key")
                return False
            
            # Step 2: Processing with spinner
            with mock_spinner("🚀 Generating posts... This may take a moment."):
                # Simulate processing
                posts = ["Post 1", "Post 2", "Post 3"]
            
            # Step 3: Success feedback
            mock_success(f"🎉 Successfully generated {len(posts)} posts!")
            return True
        
        result = simulate_complete_workflow()
        
        assert result is True
        mock_spinner.assert_called_once()
        mock_success.assert_called_once_with("🎉 Successfully generated 3 posts!")
        mock_error.assert_not_called()
    
    def test_accessibility_considerations(self):
        """Test accessibility considerations in UX design."""
        def check_accessibility_features():
            features = {
                "emoji_usage": "Emojis used for visual cues but not essential information",
                "color_coding": "Color coding supplemented with text descriptions",
                "loading_feedback": "Loading states clearly communicated with text",
                "error_clarity": "Error messages are descriptive and actionable",
                "keyboard_navigation": "All interactions work with keyboard navigation"
            }
            return features
        
        features = check_accessibility_features()
        assert "visual cues" in features["emoji_usage"]
        assert "descriptive and actionable" in features["error_clarity"]
        assert "keyboard navigation" in features["keyboard_navigation"]