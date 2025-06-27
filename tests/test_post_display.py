import pytest
from unittest.mock import Mock, patch, MagicMock, call
import streamlit as st


class TestDynamicPostDisplay:
    """Tests for dynamic post display based on generated content."""
    
    @patch('streamlit.subheader')
    @patch('streamlit.text_area')
    def test_display_posts_dynamic_generation(self, mock_text_area, mock_subheader):
        """Test dynamic UI generation based on post count."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Setup posts
            posts = [
                "Post 1: Exciting news about our product launch!",
                "Post 2: Here's how our technology works behind the scenes",
                "Post 3: Join us for our upcoming webinar next week"
            ]
            mock_session_state['generated_posts'] = posts
            mock_session_state['editing_posts'] = posts.copy()
            
            # Mock text area returns
            mock_text_area.side_effect = posts
            
            # Function to display posts dynamically
            def display_posts():
                if mock_session_state['generated_posts']:
                    mock_subheader("Generated Posts - Edit as needed:")
                    
                    for i, post in enumerate(mock_session_state['editing_posts']):
                        # Create numbered section header
                        mock_subheader(f"Post {i + 1}")
                        
                        # Create text area with unique key
                        key = f"post_{i}"
                        edited_post = mock_text_area(
                            label=f"Post {i + 1} Content",
                            value=post,
                            key=key,
                            height=100
                        )
                        
                        # Update session state
                        mock_session_state['editing_posts'][i] = edited_post
            
            # Execute display function
            display_posts()
            
            # Verify dynamic generation
            assert mock_subheader.call_count == 4  # 1 main header + 3 post headers
            assert mock_text_area.call_count == 3  # 3 text areas
            
            # Verify calls
            mock_subheader.assert_any_call("Generated Posts - Edit as needed:")
            mock_subheader.assert_any_call("Post 1")
            mock_subheader.assert_any_call("Post 2")
            mock_subheader.assert_any_call("Post 3")
    
    @patch('streamlit.text_area')
    @patch('streamlit.columns')
    def test_post_text_area_configuration(self, mock_columns, mock_text_area):
        """Test text area configuration for post editing."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = ["Sample post content"]
            
            # Mock columns for layout
            mock_col1, mock_col2 = Mock(), Mock()
            mock_columns.return_value = [mock_col1, mock_col2]
            
            # Configure text area
            def create_post_text_area(index, post_content):
                return mock_text_area(
                    label=f"Post {index + 1} Content",
                    value=post_content,
                    key=f"post_{index}",
                    height=100,
                    max_chars=3000,
                    help="Edit your post content. Changes are automatically saved."
                )
            
            # Create text area
            result = create_post_text_area(0, mock_session_state['editing_posts'][0])
            
            # Verify configuration
            mock_text_area.assert_called_once_with(
                label="Post 1 Content",
                value="Sample post content",
                key="post_0",
                height=100,
                max_chars=3000,
                help="Edit your post content. Changes are automatically saved."
            )
    
    def test_post_display_empty_state(self):
        """Test display when no posts are generated."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['generated_posts'] = []
            mock_session_state['editing_posts'] = []
            
            with patch('streamlit.info') as mock_info:
                # Function to handle empty state
                def display_posts_or_empty():
                    if not mock_session_state['generated_posts']:
                        mock_info("No posts generated yet. Use the 'Generate Posts' button above to create posts.")
                        return False
                    return True
                
                # Execute function
                result = display_posts_or_empty()
                
                # Verify empty state handling
                assert result is False
                mock_info.assert_called_once_with("No posts generated yet. Use the 'Generate Posts' button above to create posts.")
    
    @patch('streamlit.text_area')
    def test_real_time_editing_updates(self, mock_text_area):
        """Test real-time editing with automatic state updates."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Initial posts
            original_posts = ["Original post 1", "Original post 2"]
            mock_session_state['generated_posts'] = original_posts.copy()
            mock_session_state['editing_posts'] = original_posts.copy()
            
            # Simulate user editing first post
            mock_text_area.side_effect = [
                "Edited post 1 with changes",  # User edited first post
                "Original post 2"              # Second post unchanged
            ]
            
            # Function to handle real-time updates
            def update_posts_from_text_areas():
                for i in range(len(mock_session_state['editing_posts'])):
                    key = f"post_{i}"
                    current_value = mock_session_state['editing_posts'][i]
                    
                    # Simulate text area widget
                    new_value = mock_text_area(
                        label=f"Post {i + 1}",
                        value=current_value,
                        key=key
                    )
                    
                    # Update session state if changed
                    if new_value != current_value:
                        mock_session_state['editing_posts'][i] = new_value
            
            # Execute update
            update_posts_from_text_areas()
            
            # Verify updates
            assert mock_session_state['editing_posts'][0] == "Edited post 1 with changes"
            assert mock_session_state['editing_posts'][1] == "Original post 2"
            assert mock_session_state['generated_posts'][0] == "Original post 1"  # Original unchanged


class TestPostManagementFeatures:
    """Tests for post management features like deletion, reordering, copying."""
    
    @patch('streamlit.button')
    def test_individual_post_deletion(self, mock_button):
        """Test individual post deletion buttons."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = ["Post 1", "Post 2", "Post 3"]
            
            # Mock button clicks - only second delete button clicked
            mock_button.side_effect = [False, True, False]  # Delete post 2
            
            # Function to create delete buttons
            def create_delete_buttons():
                for i in range(len(mock_session_state['editing_posts'])):
                    if mock_button(f"🗑️ Delete", key=f"delete_{i}"):
                        # Delete post at index i
                        mock_session_state['editing_posts'].pop(i)
                        break  # Prevent index errors
            
            # Execute deletion
            create_delete_buttons()
            
            # Verify deletion
            assert len(mock_session_state['editing_posts']) == 2
            assert mock_session_state['editing_posts'] == ["Post 1", "Post 3"]
            assert mock_button.call_count == 3
    
    @patch('streamlit.button')
    def test_post_reordering_functionality(self, mock_button):
        """Test post reordering functionality."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = ["Post A", "Post B", "Post C"]
            
            # Mock up/down button clicks
            mock_button.side_effect = [False, True, False, False, False, False]  # Move Post B up
            
            # Function to create reorder buttons
            def create_reorder_buttons():
                for i in range(len(mock_session_state['editing_posts'])):
                    # Up button (except for first post)
                    if i > 0:
                        if mock_button("↑", key=f"up_{i}"):
                            posts = mock_session_state['editing_posts']
                            posts[i], posts[i-1] = posts[i-1], posts[i]
                            break
                    
                    # Down button (except for last post)
                    if i < len(mock_session_state['editing_posts']) - 1:
                        if mock_button("↓", key=f"down_{i}"):
                            posts = mock_session_state['editing_posts']
                            posts[i], posts[i+1] = posts[i+1], posts[i]
                            break
            
            # Execute reordering
            create_reorder_buttons()
            
            # Verify reordering (Post B moved up)
            assert mock_session_state['editing_posts'] == ["Post B", "Post A", "Post C"]
    
    @patch('streamlit.button')
    @patch('streamlit.code')
    def test_copy_to_clipboard_functionality(self, mock_code, mock_button):
        """Test copy post to clipboard functionality."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = ["Post to copy"]
            
            # Mock button click
            mock_button.return_value = True
            
            # Function to create copy button
            def create_copy_button(index):
                post_content = mock_session_state['editing_posts'][index]
                
                if mock_button(f"📋 Copy", key=f"copy_{index}"):
                    # Display copyable content
                    mock_code(post_content, language="text")
                    return True
                return False
            
            # Execute copy
            copied = create_copy_button(0)
            
            # Verify copy functionality
            assert copied is True
            mock_button.assert_called_once()
            mock_code.assert_called_once_with("Post to copy", language="text")
    
    @patch('streamlit.caption')
    def test_character_count_display(self, mock_caption):
        """Test character count display per post."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = [
                "Short post",
                "This is a much longer post with more characters to test the counting functionality"
            ]
            mock_session_state['target_platform'] = "X"
            
            # Platform limits
            platform_limits = {"X": 280, "LinkedIn": 3000, "Facebook": 63206, "Instagram": 2200}
            
            # Function to display character counts
            def display_character_counts():
                platform = mock_session_state['target_platform']
                limit = platform_limits.get(platform, 1000)
                
                for i, post in enumerate(mock_session_state['editing_posts']):
                    char_count = len(post)
                    status = "✅" if char_count <= limit else "⚠️"
                    mock_caption(f"{status} {char_count}/{limit} characters")
            
            # Execute character count display
            display_character_counts()
            
            # Verify character count calls
            assert mock_caption.call_count == 2
            calls = mock_caption.call_args_list
            assert "✅ 10/280 characters" in str(calls[0])
            assert "⚠️ 85/280 characters" in str(calls[1])


class TestPostValidation:
    """Tests for post validation and warnings for platform limits."""
    
    def test_platform_character_limit_validation(self):
        """Test validation against platform character limits."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Setup posts with different lengths
            mock_session_state['editing_posts'] = [
                "Short post",  # 10 chars
                "A" * 300,     # 300 chars - exceeds Twitter limit
                "B" * 50       # 50 chars
            ]
            mock_session_state['target_platform'] = "X"
            
            # Validation function
            def validate_platform_limits():
                platform_limits = {
                    "X": 280,
                    "LinkedIn": 3000,
                    "Facebook": 63206,
                    "Instagram": 2200
                }
                
                platform = mock_session_state['target_platform']
                limit = platform_limits.get(platform, 1000)
                violations = []
                
                for i, post in enumerate(mock_session_state['editing_posts']):
                    if len(post) > limit:
                        violations.append({
                            'index': i,
                            'length': len(post),
                            'limit': limit,
                            'excess': len(post) - limit
                        })
                
                return violations
            
            # Execute validation
            violations = validate_platform_limits()
            
            # Verify validation results
            assert len(violations) == 1
            assert violations[0]['index'] == 1
            assert violations[0]['length'] == 300
            assert violations[0]['limit'] == 280
            assert violations[0]['excess'] == 20
    
    @patch('streamlit.warning')
    def test_display_validation_warnings(self, mock_warning):
        """Test display of validation warnings."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = ["A" * 300]
            mock_session_state['target_platform'] = "X"
            
            # Function to display warnings
            def display_validation_warnings():
                platform_limit = 280
                for i, post in enumerate(mock_session_state['editing_posts']):
                    if len(post) > platform_limit:
                        excess = len(post) - platform_limit
                        mock_warning(f"Post {i + 1} exceeds {mock_session_state['target_platform']} character limit by {excess} characters")
            
            # Execute warning display
            display_validation_warnings()
            
            # Verify warning display
            mock_warning.assert_called_once_with("Post 1 exceeds X character limit by 20 characters")
    
    def test_empty_post_validation(self):
        """Test validation for empty posts."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = ["Valid post", "", "   ", "Another valid post"]
            
            # Validation function
            def validate_empty_posts():
                empty_indices = []
                for i, post in enumerate(mock_session_state['editing_posts']):
                    if not post.strip():
                        empty_indices.append(i)
                return empty_indices
            
            # Execute validation
            empty_indices = validate_empty_posts()
            
            # Verify empty post detection
            assert empty_indices == [1, 2]
    
    @patch('streamlit.error')
    def test_display_empty_post_errors(self, mock_error):
        """Test display of empty post errors."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = ["Valid post", "", "Another valid"]
            
            # Function to display empty post errors
            def display_empty_post_errors():
                for i, post in enumerate(mock_session_state['editing_posts']):
                    if not post.strip():
                        mock_error(f"Post {i + 1} is empty. Please add content or delete this post.")
            
            # Execute error display
            display_empty_post_errors()
            
            # Verify error display
            mock_error.assert_called_once_with("Post 2 is empty. Please add content or delete this post.")


class TestPostDisplayIntegration:
    """Tests for integration between post display and other components."""
    
    @patch('streamlit.columns')
    @patch('streamlit.button')
    @patch('streamlit.text_area')
    def test_integrated_post_editor_layout(self, mock_text_area, mock_button, mock_columns):
        """Test integrated layout with text area, buttons, and metadata."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = ["Sample post content"]
            mock_session_state['target_platform'] = "LinkedIn"
            
            # Mock columns for layout
            mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
            mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
            
            # Function to create integrated editor
            def create_integrated_post_editor(index):
                post = mock_session_state['editing_posts'][index]
                
                # Text area for editing
                mock_text_area(value=post, key=f"post_{index}")
                
                # Columns for buttons and metadata
                mock_columns(3)
                
                # Buttons in columns
                with mock_col1:
                    mock_button("🗑️ Delete", key=f"delete_{index}")
                with mock_col2:
                    mock_button("📋 Copy", key=f"copy_{index}")
                with mock_col3:
                    char_count = len(post)
                    # Would display character count here
            
            # Execute integrated editor
            create_integrated_post_editor(0)
            
            # Verify integration
            mock_text_area.assert_called_once()
            mock_columns.assert_called_once_with(3)
            assert mock_button.call_count == 2
    
    def test_post_numbering_consistency(self):
        """Test consistent post numbering across UI elements."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = ["Post A", "Post B", "Post C"]
            
            # Function to verify numbering consistency
            def verify_post_numbering():
                numbering_elements = []
                
                for i, post in enumerate(mock_session_state['editing_posts']):
                    # Collect all numbering references
                    header_number = i + 1
                    key_number = i
                    display_number = i + 1
                    
                    numbering_elements.append({
                        'header': f"Post {header_number}",
                        'key': f"post_{key_number}",
                        'display': f"Post {display_number} Content"
                    })
                
                return numbering_elements
            
            # Execute numbering check
            elements = verify_post_numbering()
            
            # Verify consistency
            assert len(elements) == 3
            assert elements[0]['header'] == "Post 1"
            assert elements[0]['key'] == "post_0"
            assert elements[0]['display'] == "Post 1 Content"
            assert elements[2]['header'] == "Post 3"
            assert elements[2]['key'] == "post_2"