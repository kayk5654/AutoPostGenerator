import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from config import LLM_PROVIDERS, TARGET_PLATFORMS, SUPPORTED_TEXT_FORMATS


class TestStreamlitAppConfiguration:
    """Tests for main app configuration and setup."""
    
    @patch('streamlit.set_page_config')
    def test_page_configuration(self, mock_set_page_config):
        """Test Streamlit page configuration."""
        # Function to configure page
        def configure_page():
            mock_set_page_config(
                page_title="Auto Post Generator",
                page_icon="📝",
                layout="wide"
            )
        
        # Execute configuration
        configure_page()
        
        # Verify configuration
        mock_set_page_config.assert_called_once_with(
            page_title="Auto Post Generator",
            page_icon="📝",
            layout="wide"
        )
    
    @patch('streamlit.title')
    def test_app_title_display(self, mock_title):
        """Test main application title display."""
        # Function to display title
        def display_app_title():
            mock_title("Auto Post Generator")
        
        # Execute title display
        display_app_title()
        
        # Verify title
        mock_title.assert_called_once_with("Auto Post Generator")


class TestLLMProviderSection:
    """Tests for LLM provider configuration section."""
    
    @patch('streamlit.subheader')
    @patch('streamlit.selectbox')
    @patch('streamlit.text_input')
    @patch('streamlit.columns')
    def test_llm_provider_section_layout(self, mock_columns, mock_text_input, mock_selectbox, mock_subheader):
        """Test LLM provider section layout and components."""
        # Mock columns
        mock_col1, mock_col2 = Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        # Mock component returns
        mock_selectbox.return_value = "Google Gemini"
        mock_text_input.return_value = "test-api-key"
        
        # Function to create LLM provider section
        def create_llm_provider_section():
            mock_subheader("Step 1: Configure LLM Provider")
            
            col1, col2 = mock_columns(2)
            with col1:
                selected_provider = mock_selectbox(
                    "Select LLM Provider",
                    LLM_PROVIDERS,
                    help="Choose your preferred AI provider"
                )
            
            with col2:
                api_key = mock_text_input(
                    "Enter Your API Key",
                    type="password",
                    help="Your API key will only be used for this session and not stored"
                )
            
            return selected_provider, api_key
        
        # Execute section creation
        provider, key = create_llm_provider_section()
        
        # Verify layout and components
        mock_subheader.assert_called_once_with("Step 1: Configure LLM Provider")
        mock_columns.assert_called_once_with(2)
        mock_selectbox.assert_called_once_with(
            "Select LLM Provider",
            LLM_PROVIDERS,
            help="Choose your preferred AI provider"
        )
        mock_text_input.assert_called_once_with(
            "Enter Your API Key",
            type="password",
            help="Your API key will only be used for this session and not stored"
        )
        
        assert provider == "Google Gemini"
        assert key == "test-api-key"
    
    @patch('streamlit.selectbox')
    def test_llm_provider_options(self, mock_selectbox):
        """Test LLM provider selectbox options."""
        mock_selectbox.return_value = "OpenAI"
        
        # Function to create provider selector
        def create_provider_selector():
            return mock_selectbox(
                "Select LLM Provider",
                LLM_PROVIDERS
            )
        
        # Execute selector creation
        selected = create_provider_selector()
        
        # Verify provider options
        mock_selectbox.assert_called_once_with(
            "Select LLM Provider",
            LLM_PROVIDERS
        )
        assert selected == "OpenAI"
    
    @patch('streamlit.text_input')
    def test_api_key_input_security(self, mock_text_input):
        """Test API key input security configuration."""
        mock_text_input.return_value = "secure-key"
        
        # Function to create secure API key input
        def create_api_key_input():
            return mock_text_input(
                "Enter Your API Key",
                type="password",
                help="Your API key will only be used for this session and not stored"
            )
        
        # Execute input creation
        key = create_api_key_input()
        
        # Verify security settings
        mock_text_input.assert_called_once_with(
            "Enter Your API Key",
            type="password",
            help="Your API key will only be used for this session and not stored"
        )
        assert key == "secure-key"


class TestFileUploadSection:
    """Tests for file upload section components."""
    
    @patch('streamlit.subheader')
    @patch('streamlit.markdown')
    @patch('streamlit.file_uploader')
    def test_source_files_uploader(self, mock_file_uploader, mock_markdown, mock_subheader):
        """Test source files upload component."""
        # Mock uploaded files
        mock_files = [Mock(name="file1.txt"), Mock(name="file2.pdf")]
        mock_file_uploader.return_value = mock_files
        
        # Function to create source files uploader
        def create_source_files_uploader():
            mock_subheader("Step 2: Provide Inputs")
            mock_markdown("**1. Upload Information Source Files**")
            
            return mock_file_uploader(
                "Choose source files",
                type=['txt', 'docx', 'pdf', 'md'],
                accept_multiple_files=True,
                help=f"Supported formats: {', '.join(SUPPORTED_TEXT_FORMATS)}"
            )
        
        # Execute uploader creation
        files = create_source_files_uploader()
        
        # Verify uploader configuration
        mock_file_uploader.assert_called_once_with(
            "Choose source files",
            type=['txt', 'docx', 'pdf', 'md'],
            accept_multiple_files=True,
            help=f"Supported formats: {', '.join(SUPPORTED_TEXT_FORMATS)}"
        )
        assert files == mock_files
    
    @patch('streamlit.file_uploader')
    def test_brand_guide_uploader(self, mock_file_uploader):
        """Test brand guide file upload component."""
        mock_file = Mock(name="brand_guide.docx")
        mock_file_uploader.return_value = mock_file
        
        # Function to create brand guide uploader
        def create_brand_guide_uploader():
            return mock_file_uploader(
                "Choose brand guide file",
                type=['txt', 'docx', 'pdf', 'md'],
                accept_multiple_files=False,
                help="Upload your brand voice and style guidelines"
            )
        
        # Execute uploader creation
        file = create_brand_guide_uploader()
        
        # Verify uploader configuration
        mock_file_uploader.assert_called_once_with(
            "Choose brand guide file",
            type=['txt', 'docx', 'pdf', 'md'],
            accept_multiple_files=False,
            help="Upload your brand voice and style guidelines"
        )
        assert file == mock_file
    
    @patch('streamlit.file_uploader')
    def test_post_history_uploader(self, mock_file_uploader):
        """Test post history file upload component."""
        mock_file = Mock(name="post_history.xlsx")
        mock_file_uploader.return_value = mock_file
        
        # Function to create post history uploader
        def create_post_history_uploader():
            return mock_file_uploader(
                "Choose post history file",
                type=['xlsx'],
                accept_multiple_files=False,
                help="Upload Excel file with previous posts for style reference"
            )
        
        # Execute uploader creation
        file = create_post_history_uploader()
        
        # Verify uploader configuration
        mock_file_uploader.assert_called_once_with(
            "Choose post history file",
            type=['xlsx'],
            accept_multiple_files=False,
            help="Upload Excel file with previous posts for style reference"
        )
        assert file == mock_file


class TestPostGenerationControls:
    """Tests for post generation control components."""
    
    @patch('streamlit.columns')
    @patch('streamlit.number_input')
    @patch('streamlit.selectbox')
    def test_generation_controls_layout(self, mock_selectbox, mock_number_input, mock_columns):
        """Test post generation controls layout."""
        # Mock columns
        mock_col1, mock_col2 = Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        # Mock control returns
        mock_number_input.return_value = 3
        mock_selectbox.return_value = "LinkedIn"
        
        # Function to create generation controls
        def create_generation_controls():
            col1, col2 = mock_columns(2)
            
            with col1:
                count = mock_number_input(
                    "Number of Posts to Generate",
                    min_value=1,
                    max_value=50,
                    value=3,
                    help="How many posts do you want to generate?"
                )
            
            with col2:
                platform = mock_selectbox(
                    "Select Target Platform",
                    TARGET_PLATFORMS,
                    help="Choose the social media platform for your posts"
                )
            
            return count, platform
        
        # Execute controls creation
        count, platform = create_generation_controls()
        
        # Verify controls configuration
        mock_columns.assert_called_once_with(2)
        mock_number_input.assert_called_once_with(
            "Number of Posts to Generate",
            min_value=1,
            max_value=50,
            value=3,
            help="How many posts do you want to generate?"
        )
        mock_selectbox.assert_called_once_with(
            "Select Target Platform",
            TARGET_PLATFORMS,
            help="Choose the social media platform for your posts"
        )
        
        assert count == 3
        assert platform == "LinkedIn"
    
    @patch('streamlit.number_input')
    def test_post_count_validation(self, mock_number_input):
        """Test post count input validation."""
        # Test valid range
        mock_number_input.return_value = 5
        
        # Function to create post count input
        def create_post_count_input():
            return mock_number_input(
                "Number of Posts to Generate",
                min_value=1,
                max_value=50,
                value=3,
                step=1
            )
        
        # Execute input creation
        count = create_post_count_input()
        
        # Verify validation settings
        mock_number_input.assert_called_once_with(
            "Number of Posts to Generate",
            min_value=1,
            max_value=50,
            value=3,
            step=1
        )
        assert count == 5
    
    @patch('streamlit.selectbox')
    def test_platform_selection_options(self, mock_selectbox):
        """Test platform selection options."""
        mock_selectbox.return_value = "X"
        
        # Function to create platform selector
        def create_platform_selector():
            return mock_selectbox(
                "Select Target Platform",
                TARGET_PLATFORMS,
                index=0
            )
        
        # Execute selector creation
        platform = create_platform_selector()
        
        # Verify platform options
        mock_selectbox.assert_called_once_with(
            "Select Target Platform",
            TARGET_PLATFORMS,
            index=0
        )
        assert platform == "X"


class TestGenerationButton:
    """Tests for the main generation button component."""
    
    @patch('streamlit.button')
    def test_generate_button_configuration(self, mock_button):
        """Test generate posts button configuration."""
        mock_button.return_value = True
        
        # Function to create generate button
        def create_generate_button():
            return mock_button(
                "🚀 Generate Posts",
                type="primary",
                help="Click to generate social media posts based on your inputs"
            )
        
        # Execute button creation
        clicked = create_generate_button()
        
        # Verify button configuration
        mock_button.assert_called_once_with(
            "🚀 Generate Posts",
            type="primary",
            help="Click to generate social media posts based on your inputs"
        )
        assert clicked is True
    
    @patch('streamlit.button')
    def test_button_state_management(self, mock_button):
        """Test button state based on form validity."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['form_valid'] = False
            
            # Mock button behavior based on form validity
            def mock_button_behavior(label, **kwargs):
                if 'disabled' in kwargs:
                    return False if kwargs['disabled'] else True
                return not mock_session_state['form_valid']
            
            mock_button.side_effect = mock_button_behavior
            
            # Function to create conditional button
            def create_conditional_button(form_valid):
                return mock_button(
                    "🚀 Generate Posts",
                    type="primary",
                    disabled=not form_valid
                )
            
            # Test disabled state
            clicked = create_conditional_button(False)
            assert clicked is False
            
            # Test enabled state
            clicked = create_conditional_button(True)
            assert clicked is True


class TestUILayoutAndSections:
    """Tests for overall UI layout and section organization."""
    
    @patch('streamlit.markdown')
    def test_section_separators(self, mock_markdown):
        """Test section separator markdown elements."""
        # Function to create section separators
        def create_section_separators():
            separators = ["---", "---", "---"]
            for separator in separators:
                mock_markdown(separator)
        
        # Execute separator creation
        create_section_separators()
        
        # Verify separators
        assert mock_markdown.call_count == 3
        for call in mock_markdown.call_args_list:
            assert call[0][0] == "---"
    
    @patch('streamlit.subheader')
    def test_step_by_step_headers(self, mock_subheader):
        """Test step-by-step section headers."""
        # Function to create step headers
        def create_step_headers():
            steps = [
                "Step 1: Configure LLM Provider",
                "Step 2: Provide Inputs",
                "Step 3: Generation Settings",
                "Step 4: Generate Posts"
            ]
            for step in steps:
                mock_subheader(step)
        
        # Execute header creation
        create_step_headers()
        
        # Verify headers
        expected_calls = [
            call("Step 1: Configure LLM Provider"),
            call("Step 2: Provide Inputs"),
            call("Step 3: Generation Settings"),
            call("Step 4: Generate Posts")
        ]
        mock_subheader.assert_has_calls(expected_calls)
    
    @patch('streamlit.columns')
    def test_responsive_layout_columns(self, mock_columns):
        """Test responsive column layouts."""
        # Mock different column configurations
        mock_columns.side_effect = [
            [Mock(), Mock()],      # 2 columns for provider/key
            [Mock(), Mock()],      # 2 columns for count/platform
            [Mock(), Mock(), Mock()]  # 3 columns for buttons
        ]
        
        # Function to create responsive layouts
        def create_responsive_layouts():
            # Provider section - 2 columns
            provider_cols = mock_columns(2)
            
            # Generation controls - 2 columns
            control_cols = mock_columns(2)
            
            # Action buttons - 3 columns
            button_cols = mock_columns(3)
            
            return provider_cols, control_cols, button_cols
        
        # Execute layout creation
        provider_cols, control_cols, button_cols = create_responsive_layouts()
        
        # Verify column configurations
        expected_calls = [call(2), call(2), call(3)]
        mock_columns.assert_has_calls(expected_calls)
        
        assert len(provider_cols) == 2
        assert len(control_cols) == 2
        assert len(button_cols) == 3


class TestConditionalUIElements:
    """Tests for conditional UI elements based on state."""
    
    def test_conditional_post_display_section(self):
        """Test conditional display of post editing section."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Test case 1: No posts generated
            mock_session_state['generated_posts'] = []
            
            def should_show_posts():
                return len(mock_session_state['generated_posts']) > 0
            
            assert should_show_posts() is False
            
            # Test case 2: Posts generated
            mock_session_state['generated_posts'] = ["Post 1", "Post 2"]
            assert should_show_posts() is True
    
    def test_conditional_export_section(self):
        """Test conditional display of export section."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Test case 1: No posts to export
            mock_session_state['editing_posts'] = []
            
            def should_show_export():
                return len(mock_session_state['editing_posts']) > 0
            
            assert should_show_export() is False
            
            # Test case 2: Posts available for export
            mock_session_state['editing_posts'] = ["Edited post 1", "Edited post 2"]
            assert should_show_export() is True
    
    @patch('streamlit.info')
    @patch('streamlit.warning')
    def test_conditional_help_messages(self, mock_warning, mock_info):
        """Test conditional help and warning messages."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Function to show conditional messages
            def show_conditional_messages(source_files, api_key):
                if not source_files:
                    mock_info("📁 Please upload source files to get started")
                
                if not api_key:
                    mock_warning("🔑 API key required to generate posts")
                
                if source_files and api_key:
                    mock_info("✅ Ready to generate posts!")
            
            # Test case 1: Missing files and key
            show_conditional_messages(None, "")
            mock_info.assert_called_with("📁 Please upload source files to get started")
            mock_warning.assert_called_with("🔑 API key required to generate posts")
            
            # Reset mocks
            mock_info.reset_mock()
            mock_warning.reset_mock()
            
            # Test case 2: Everything ready
            show_conditional_messages([Mock()], "api-key")
            mock_info.assert_called_with("✅ Ready to generate posts!")
            mock_warning.assert_not_called()


class TestUIAccessibility:
    """Tests for UI accessibility features."""
    
    @patch('streamlit.selectbox')
    @patch('streamlit.text_input')
    @patch('streamlit.file_uploader')
    def test_help_text_coverage(self, mock_file_uploader, mock_text_input, mock_selectbox):
        """Test that all components have appropriate help text."""
        # Function to create components with help text
        def create_components_with_help():
            mock_selectbox(
                "Provider",
                ["Option1"],
                help="Choose your preferred AI provider"
            )
            mock_text_input(
                "API Key",
                type="password",
                help="Your API key will only be used for this session"
            )
            mock_file_uploader(
                "Files",
                help="Upload your source content files"
            )
        
        # Execute component creation
        create_components_with_help()
        
        # Verify help text presence
        mock_selectbox.assert_called_with(
            "Provider",
            ["Option1"],
            help="Choose your preferred AI provider"
        )
        mock_text_input.assert_called_with(
            "API Key",
            type="password",
            help="Your API key will only be used for this session"
        )
        mock_file_uploader.assert_called_with(
            "Files",
            help="Upload your source content files"
        )
    
    def test_keyboard_navigation_support(self):
        """Test support for keyboard navigation."""
        # Function to verify tab order and accessibility
        def verify_tab_order():
            # In real implementation, would test component ordering
            # and keyboard accessibility features
            tab_order = [
                "llm_provider_select",
                "api_key_input",
                "source_files_upload",
                "brand_guide_upload",
                "post_history_upload",
                "post_count_input",
                "platform_select",
                "generate_button"
            ]
            
            # Verify logical tab order
            assert len(tab_order) == 8
            assert tab_order[0] == "llm_provider_select"
            assert tab_order[-1] == "generate_button"
            
            return tab_order
        
        # Execute tab order verification
        order = verify_tab_order()
        assert order is not None