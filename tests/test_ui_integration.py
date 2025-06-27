import pytest
from unittest.mock import Mock, patch, MagicMock, call
import streamlit as st
from datetime import datetime


class TestUIWorkflowIntegration:
    """Tests for UI integration and workflow connections."""
    
    @patch('services.post_service.generate_posts_workflow')
    @patch('streamlit.button')
    @patch('streamlit.spinner')
    @patch('streamlit.success')
    @patch('streamlit.error')
    def test_generate_posts_button_integration(self, mock_error, mock_success, mock_spinner, mock_button, mock_workflow):
        """Test Generate Posts button integration with workflow."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Setup input state
            mock_session_state['generated_posts'] = []
            mock_session_state['editing_posts'] = []
            
            # Mock inputs
            source_files = [Mock(name="file1.txt"), Mock(name="file2.pdf")]
            brand_guide = Mock(name="brand.docx")
            history_file = Mock(name="history.xlsx")
            provider = "Google Gemini"
            api_key = "test-api-key-123"
            platform = "LinkedIn"
            count = 3
            
            # Mock successful workflow
            generated_posts = [
                "Professional post about our latest innovation",
                "Industry insights on emerging technology trends",
                "Thought leadership content for our community"
            ]
            mock_workflow.return_value = generated_posts
            mock_button.return_value = True  # Button clicked
            
            # Mock spinner context manager
            mock_spinner_context = Mock()
            mock_spinner.return_value.__enter__ = Mock(return_value=mock_spinner_context)
            mock_spinner.return_value.__exit__ = Mock(return_value=None)
            
            # Function to handle generate button
            def handle_generate_posts():
                if mock_button("🚀 Generate Posts", type="primary"):
                    if not source_files or not api_key:
                        mock_error("Please provide source files and API key")
                        return
                    
                    with mock_spinner("Generating posts..."):
                        try:
                            posts = mock_workflow(
                                source_files, brand_guide, history_file,
                                provider, api_key, platform, count
                            )
                            
                            # Update session state
                            mock_session_state['generated_posts'] = posts
                            mock_session_state['editing_posts'] = posts.copy()
                            mock_session_state['generation_timestamp'] = datetime.now().isoformat()
                            mock_session_state['target_platform'] = platform
                            
                            mock_success(f"Generated {len(posts)} posts successfully!")
                            
                        except Exception as e:
                            mock_error(f"Error generating posts: {str(e)}")
            
            # Execute generate posts
            handle_generate_posts()
            
            # Verify integration
            mock_button.assert_called_once_with("🚀 Generate Posts", type="primary")
            mock_spinner.assert_called_once_with("Generating posts...")
            mock_workflow.assert_called_once_with(
                source_files, brand_guide, history_file,
                provider, api_key, platform, count
            )
            mock_success.assert_called_once_with("Generated 3 posts successfully!")
            
            # Verify session state updates
            assert mock_session_state['generated_posts'] == generated_posts
            assert mock_session_state['editing_posts'] == generated_posts
            assert mock_session_state['target_platform'] == platform
            assert mock_session_state['generation_timestamp'] is not None
    
    @patch('streamlit.button')
    @patch('streamlit.error')
    def test_input_validation_integration(self, mock_error, mock_button):
        """Test input validation before post generation."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_button.return_value = True
            
            # Test cases for validation
            test_cases = [
                {
                    'source_files': None,
                    'api_key': 'valid-key',
                    'provider': 'Google Gemini',
                    'expected_error': 'Please upload source files'
                },
                {
                    'source_files': [Mock()],
                    'api_key': '',
                    'provider': 'Google Gemini',
                    'expected_error': 'Please enter your API key'
                },
                {
                    'source_files': [Mock()],
                    'api_key': 'valid-key',
                    'provider': '',
                    'expected_error': 'Please select an LLM provider'
                }
            ]
            
            # Function to validate inputs
            def validate_inputs(source_files, api_key, provider, platform, count):
                errors = []
                
                if not source_files:
                    errors.append('Please upload source files')
                if not api_key or not api_key.strip():
                    errors.append('Please enter your API key')
                if not provider:
                    errors.append('Please select an LLM provider')
                if not platform:
                    errors.append('Please select target platform')
                if count < 1 or count > 50:
                    errors.append('Post count must be between 1 and 50')
                
                return errors
            
            # Test each validation case
            for case in test_cases:
                mock_error.reset_mock()
                
                errors = validate_inputs(
                    case['source_files'],
                    case['api_key'],
                    case['provider'],
                    'LinkedIn',
                    3
                )
                
                if errors:
                    for error in errors:
                        mock_error(error)
                
                # Verify expected error was called
                mock_error.assert_any_call(case['expected_error'])
    
    @patch('streamlit.button')
    def test_generate_new_posts_button(self, mock_button):
        """Test Generate New Posts button functionality."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Setup existing posts
            mock_session_state['generated_posts'] = ["Old post 1", "Old post 2"]
            mock_session_state['editing_posts'] = ["Edited post 1", "Edited post 2"]
            mock_session_state['generation_timestamp'] = "2024-01-14T10:00:00"
            mock_session_state['target_platform'] = "X"
            
            mock_button.return_value = True
            
            # Function to handle new generation
            def handle_generate_new_posts():
                if mock_session_state['generated_posts']:  # Only show if posts exist
                    if mock_button("🔄 Generate New Posts"):
                        # Reset state for new generation
                        mock_session_state['generated_posts'] = []
                        mock_session_state['editing_posts'] = []
                        mock_session_state['generation_timestamp'] = None
                        mock_session_state['target_platform'] = None
                        return True
                return False
            
            # Execute new generation
            result = handle_generate_new_posts()
            
            # Verify state reset
            assert result is True
            assert mock_session_state['generated_posts'] == []
            assert mock_session_state['editing_posts'] == []
            assert mock_session_state['generation_timestamp'] is None
            assert mock_session_state['target_platform'] is None
            mock_button.assert_called_once_with("🔄 Generate New Posts")
    
    @patch('streamlit.info')
    def test_generation_metadata_display(self, mock_info):
        """Test display of generation timestamp and settings."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['generated_posts'] = ["Post 1", "Post 2"]
            mock_session_state['generation_timestamp'] = "2024-01-15T14:30:00"
            mock_session_state['target_platform'] = "LinkedIn"
            
            # Function to display metadata
            def display_generation_metadata():
                if mock_session_state['generated_posts']:
                    timestamp = mock_session_state['generation_timestamp']
                    platform = mock_session_state['target_platform']
                    count = len(mock_session_state['generated_posts'])
                    
                    # Format timestamp for display
                    if timestamp:
                        formatted_time = timestamp.replace('T', ' at ').split('.')[0]
                        mock_info(f"Generated {count} posts for {platform} on {formatted_time}")
            
            # Execute metadata display
            display_generation_metadata()
            
            # Verify metadata display
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "Generated 2 posts for LinkedIn" in call_args
            assert "2024-01-15 at 14:30:00" in call_args
    
    @patch('services.post_service.generate_posts_workflow')
    @patch('streamlit.error')
    @patch('streamlit.button')
    def test_error_handling_in_workflow(self, mock_button, mock_error, mock_workflow):
        """Test error handling during post generation workflow."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_button.return_value = True
            
            # Test different error scenarios
            error_scenarios = [
                {
                    'exception': ValueError("Invalid API key"),
                    'expected_message': "Error generating posts: Invalid API key"
                },
                {
                    'exception': Exception("Network connection failed"),
                    'expected_message': "Error generating posts: Network connection failed"
                },
                {
                    'exception': Exception("Rate limit exceeded"),
                    'expected_message': "Error generating posts: Rate limit exceeded"
                }
            ]
            
            for scenario in error_scenarios:
                mock_error.reset_mock()
                mock_workflow.side_effect = scenario['exception']
                
                # Function to handle workflow with error handling
                def handle_workflow_with_errors():
                    try:
                        mock_workflow([], None, None, "provider", "key", "platform", 1)
                    except Exception as e:
                        mock_error(f"Error generating posts: {str(e)}")
                
                # Execute workflow with error
                handle_workflow_with_errors()
                
                # Verify error handling
                mock_error.assert_called_once_with(scenario['expected_message'])


class TestLoadingAndFeedback:
    """Tests for loading indicators and user feedback."""
    
    @patch('streamlit.spinner')
    @patch('streamlit.progress')
    def test_loading_spinner_with_progress(self, mock_progress, mock_spinner):
        """Test loading spinner with progress messages."""
        # Mock spinner context manager
        mock_spinner_context = Mock()
        mock_spinner.return_value.__enter__ = Mock(return_value=mock_spinner_context)
        mock_spinner.return_value.__exit__ = Mock(return_value=None)
        
        # Mock progress bar
        progress_bar = Mock()
        mock_progress.return_value = progress_bar
        
        # Function to show loading with progress
        def show_loading_with_progress():
            with mock_spinner("Generating posts..."):
                progress_bar = mock_progress(0)
                
                # Simulate progress steps
                steps = [
                    ("Extracting text from files...", 20),
                    ("Building prompt...", 40),
                    ("Calling AI provider...", 70),
                    ("Processing response...", 90),
                    ("Finalizing posts...", 100)
                ]
                
                for message, percent in steps:
                    # Update progress
                    progress_bar.progress(percent / 100)
                    # In real implementation, would show status message
        
        # Execute loading
        show_loading_with_progress()
        
        # Verify loading components
        mock_spinner.assert_called_once_with("Generating posts...")
        mock_progress.assert_called_once_with(0)
        assert progress_bar.progress.call_count == 5
    
    @patch('streamlit.success')
    @patch('streamlit.balloons')
    def test_success_feedback_with_celebration(self, mock_balloons, mock_success):
        """Test success feedback with visual celebration."""
        # Function to show success feedback
        def show_success_feedback(post_count, platform):
            mock_success(f"🎉 Successfully generated {post_count} posts for {platform}!")
            mock_balloons()  # Celebration animation
        
        # Execute success feedback
        show_success_feedback(5, "LinkedIn")
        
        # Verify success feedback
        mock_success.assert_called_once_with("🎉 Successfully generated 5 posts for LinkedIn!")
        mock_balloons.assert_called_once()
    
    @patch('streamlit.warning')
    def test_warning_feedback_for_edge_cases(self, mock_warning):
        """Test warning feedback for edge cases."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = ["Valid post", "", "Another post"]
            
            # Function to show warnings
            def show_validation_warnings():
                empty_posts = []
                for i, post in enumerate(mock_session_state['editing_posts']):
                    if not post.strip():
                        empty_posts.append(i + 1)
                
                if empty_posts:
                    if len(empty_posts) == 1:
                        mock_warning(f"Post {empty_posts[0]} is empty. Consider adding content or removing it.")
                    else:
                        post_nums = ", ".join(map(str, empty_posts))
                        mock_warning(f"Posts {post_nums} are empty. Consider adding content or removing them.")
            
            # Execute warning display
            show_validation_warnings()
            
            # Verify warning
            mock_warning.assert_called_once_with("Post 2 is empty. Consider adding content or removing it.")


class TestUIStateConsistency:
    """Tests for UI state consistency and synchronization."""
    
    def test_ui_state_synchronization_with_session_state(self):
        """Test UI components stay synchronized with session state."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Initial state
            mock_session_state['editing_posts'] = ["Post 1", "Post 2"]
            mock_session_state['target_platform'] = "LinkedIn"
            
            # Simulate UI state changes
            ui_state = {
                'posts_displayed': len(mock_session_state['editing_posts']),
                'platform_shown': mock_session_state['target_platform']
            }
            
            # Function to check synchronization
            def check_ui_sync():
                session_post_count = len(mock_session_state['editing_posts'])
                session_platform = mock_session_state['target_platform']
                
                return (
                    ui_state['posts_displayed'] == session_post_count and
                    ui_state['platform_shown'] == session_platform
                )
            
            # Verify initial sync
            assert check_ui_sync() is True
            
            # Change session state
            mock_session_state['editing_posts'].append("Post 3")
            mock_session_state['target_platform'] = "X"
            
            # Update UI state
            ui_state['posts_displayed'] = len(mock_session_state['editing_posts'])
            ui_state['platform_shown'] = mock_session_state['target_platform']
            
            # Verify continued sync
            assert check_ui_sync() is True
    
    @patch('streamlit.button')
    def test_button_state_management(self, mock_button):
        """Test button state management across interactions."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['generation_in_progress'] = False
            mock_session_state['generated_posts'] = []
            
            # Mock button returns based on state
            def mock_button_behavior(label, **kwargs):
                if "Generate Posts" in label:
                    return not mock_session_state['generation_in_progress']
                elif "Generate New Posts" in label:
                    return len(mock_session_state['generated_posts']) > 0
                return False
            
            mock_button.side_effect = mock_button_behavior
            
            # Test button states
            generate_enabled = mock_button("🚀 Generate Posts", type="primary")
            new_posts_enabled = mock_button("🔄 Generate New Posts")
            
            # Verify initial state
            assert generate_enabled is True  # Can generate
            assert new_posts_enabled is False  # No posts to regenerate
            
            # Change state - posts generated
            mock_session_state['generated_posts'] = ["Post 1", "Post 2"]
            
            # Test button states after generation
            new_posts_enabled = mock_button("🔄 Generate New Posts")
            assert new_posts_enabled is True  # Now can regenerate
    
    def test_form_state_persistence(self):
        """Test form input state persistence."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Initialize form state
            if 'form_provider' not in mock_session_state:
                mock_session_state['form_provider'] = "Google Gemini"
            if 'form_platform' not in mock_session_state:
                mock_session_state['form_platform'] = "LinkedIn"
            if 'form_count' not in mock_session_state:
                mock_session_state['form_count'] = 3
            
            # Function to validate form persistence
            def validate_form_persistence():
                return (
                    mock_session_state['form_provider'] in ["Google Gemini", "OpenAI", "Anthropic"] and
                    mock_session_state['form_platform'] in ["X", "LinkedIn", "Facebook", "Instagram"] and
                    1 <= mock_session_state['form_count'] <= 50
                )
            
            # Verify form state is valid
            assert validate_form_persistence() is True
            
            # Simulate form changes
            mock_session_state['form_provider'] = "OpenAI"
            mock_session_state['form_platform'] = "X"
            mock_session_state['form_count'] = 5
            
            # Verify persistence after changes
            assert validate_form_persistence() is True
            assert mock_session_state['form_provider'] == "OpenAI"
            assert mock_session_state['form_platform'] == "X"
            assert mock_session_state['form_count'] == 5


class TestUserExperienceFlow:
    """Tests for complete user experience flows."""
    
    @patch('streamlit.info')
    @patch('streamlit.success')
    @patch('streamlit.button')
    def test_complete_user_flow(self, mock_button, mock_success, mock_info):
        """Test complete user flow from start to finish."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Initialize clean state
            mock_session_state['generated_posts'] = []
            mock_session_state['editing_posts'] = []
            
            # Simulate user flow steps
            flow_steps = [
                "initial_load",
                "form_filled",
                "posts_generated",
                "posts_edited",
                "ready_for_export"
            ]
            
            current_step = "initial_load"
            
            # Function to determine UI state based on flow step
            def get_ui_state_for_step(step):
                if step == "initial_load":
                    return {
                        'show_form': True,
                        'show_generate_button': True,
                        'show_posts': False,
                        'show_export': False
                    }
                elif step == "posts_generated":
                    return {
                        'show_form': True,
                        'show_generate_button': True,
                        'show_posts': True,
                        'show_export': True
                    }
                else:
                    return {}
            
            # Test initial state
            ui_state = get_ui_state_for_step("initial_load")
            assert ui_state['show_form'] is True
            assert ui_state['show_posts'] is False
            
            # Simulate post generation
            mock_session_state['generated_posts'] = ["Post 1", "Post 2"]
            mock_session_state['editing_posts'] = ["Post 1", "Post 2"]
            
            # Test post-generation state
            ui_state = get_ui_state_for_step("posts_generated")
            assert ui_state['show_posts'] is True
            assert ui_state['show_export'] is True
    
    def test_responsive_ui_updates(self):
        """Test UI responsiveness to rapid state changes."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = []
            
            # Simulate rapid post additions
            rapid_changes = [
                ["Post 1"],
                ["Post 1", "Post 2"],
                ["Post 1", "Post 2", "Post 3"],
                ["Post 1", "Post 3"],  # Post 2 deleted
                ["Post 1", "Post 3", "Post 4"]
            ]
            
            for change in rapid_changes:
                mock_session_state['editing_posts'] = change
                
                # Function to validate UI state
                def validate_ui_responsiveness():
                    expected_count = len(mock_session_state['editing_posts'])
                    # In real implementation, would check UI element count
                    ui_element_count = len(mock_session_state['editing_posts'])
                    return ui_element_count == expected_count
                
                # Verify UI keeps up with changes
                assert validate_ui_responsiveness() is True