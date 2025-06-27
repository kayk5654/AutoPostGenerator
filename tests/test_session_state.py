import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from datetime import datetime


class TestSessionStateInitialization:
    """Tests for session state initialization and management."""
    
    def test_session_state_initialization(self):
        """Test that all required session state variables are initialized."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Simulate app initialization
            if 'generated_posts' not in mock_session_state:
                mock_session_state['generated_posts'] = []
            if 'editing_posts' not in mock_session_state:
                mock_session_state['editing_posts'] = []
            if 'generation_timestamp' not in mock_session_state:
                mock_session_state['generation_timestamp'] = None
            if 'target_platform' not in mock_session_state:
                mock_session_state['target_platform'] = None
            
            # Verify initialization
            assert 'generated_posts' in mock_session_state
            assert 'editing_posts' in mock_session_state
            assert 'generation_timestamp' in mock_session_state
            assert 'target_platform' in mock_session_state
            
            # Verify default values
            assert mock_session_state['generated_posts'] == []
            assert mock_session_state['editing_posts'] == []
            assert mock_session_state['generation_timestamp'] is None
            assert mock_session_state['target_platform'] is None
    
    def test_session_state_persistence_across_reruns(self):
        """Test that session state persists across Streamlit reruns."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # First run - initialize state
            mock_session_state['generated_posts'] = ["Post 1", "Post 2"]
            mock_session_state['editing_posts'] = ["Edited Post 1", "Edited Post 2"]
            mock_session_state['generation_timestamp'] = "2024-01-15T10:30:00"
            mock_session_state['target_platform'] = "LinkedIn"
            
            # Simulate app rerun - values should persist
            assert mock_session_state['generated_posts'] == ["Post 1", "Post 2"]
            assert mock_session_state['editing_posts'] == ["Edited Post 1", "Edited Post 2"]
            assert mock_session_state['generation_timestamp'] == "2024-01-15T10:30:00"
            assert mock_session_state['target_platform'] == "LinkedIn"
    
    def test_session_state_reset_functionality(self):
        """Test session state reset for new generations."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Set up existing state
            mock_session_state['generated_posts'] = ["Old post 1", "Old post 2"]
            mock_session_state['editing_posts'] = ["Old edited 1", "Old edited 2"]
            mock_session_state['generation_timestamp'] = "2024-01-14T09:00:00"
            mock_session_state['target_platform'] = "X"
            
            # Function to reset state for new generation
            def reset_generation_state():
                mock_session_state['generated_posts'] = []
                mock_session_state['editing_posts'] = []
                mock_session_state['generation_timestamp'] = None
                mock_session_state['target_platform'] = None
            
            # Execute reset
            reset_generation_state()
            
            # Verify state is reset
            assert mock_session_state['generated_posts'] == []
            assert mock_session_state['editing_posts'] == []
            assert mock_session_state['generation_timestamp'] is None
            assert mock_session_state['target_platform'] is None


class TestSessionStateUpdates:
    """Tests for session state updates during post generation and editing."""
    
    def test_update_generated_posts(self):
        """Test updating generated_posts in session state."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            new_posts = [
                "Exciting news! Our AI assistant just got smarter 🚀",
                "Streamline your workflow with our latest features",
                "Join thousands of users transforming their productivity"
            ]
            
            # Simulate post generation update
            mock_session_state['generated_posts'] = new_posts
            mock_session_state['editing_posts'] = new_posts.copy()
            mock_session_state['generation_timestamp'] = datetime.now().isoformat()
            mock_session_state['target_platform'] = "LinkedIn"
            
            # Verify updates
            assert len(mock_session_state['generated_posts']) == 3
            assert mock_session_state['generated_posts'][0] == "Exciting news! Our AI assistant just got smarter 🚀"
            assert mock_session_state['editing_posts'] == mock_session_state['generated_posts']
            assert mock_session_state['generation_timestamp'] is not None
            assert mock_session_state['target_platform'] == "LinkedIn"
    
    def test_update_editing_posts_independently(self):
        """Test that editing_posts can be updated independently of generated_posts."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Initial state
            original_posts = ["Original post 1", "Original post 2"]
            mock_session_state['generated_posts'] = original_posts.copy()
            mock_session_state['editing_posts'] = original_posts.copy()
            
            # User edits first post
            mock_session_state['editing_posts'][0] = "Edited: Original post 1 with changes"
            
            # Verify editing_posts changed but generated_posts unchanged
            assert mock_session_state['generated_posts'][0] == "Original post 1"
            assert mock_session_state['editing_posts'][0] == "Edited: Original post 1 with changes"
            assert mock_session_state['generated_posts'][1] == mock_session_state['editing_posts'][1]
    
    def test_session_state_memory_management(self):
        """Test memory management for large session state data."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Simulate large number of posts
            large_posts_list = [f"Post {i} with substantial content " * 50 for i in range(100)]
            
            mock_session_state['generated_posts'] = large_posts_list
            mock_session_state['editing_posts'] = large_posts_list.copy()
            
            # Verify memory handling
            assert len(mock_session_state['generated_posts']) == 100
            assert len(mock_session_state['editing_posts']) == 100
            
            # Simulate cleanup for memory management
            if len(mock_session_state['generated_posts']) > 50:
                # Keep only recent posts
                mock_session_state['generated_posts'] = mock_session_state['generated_posts'][-50:]
                mock_session_state['editing_posts'] = mock_session_state['editing_posts'][-50:]
            
            assert len(mock_session_state['generated_posts']) == 50
            assert len(mock_session_state['editing_posts']) == 50


class TestSessionStateValidation:
    """Tests for session state validation and error handling."""
    
    def test_validate_session_state_types(self):
        """Test validation of session state variable types."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Set correct types
            mock_session_state['generated_posts'] = ["post1", "post2"]
            mock_session_state['editing_posts'] = ["edit1", "edit2"]
            mock_session_state['generation_timestamp'] = "2024-01-15T10:30:00"
            mock_session_state['target_platform'] = "LinkedIn"
            
            # Validation function
            def validate_session_state():
                assert isinstance(mock_session_state.get('generated_posts', []), list)
                assert isinstance(mock_session_state.get('editing_posts', []), list)
                assert isinstance(mock_session_state.get('generation_timestamp'), (str, type(None)))
                assert isinstance(mock_session_state.get('target_platform'), (str, type(None)))
                
                # Validate list contents
                for post in mock_session_state['generated_posts']:
                    assert isinstance(post, str)
                for post in mock_session_state['editing_posts']:
                    assert isinstance(post, str)
            
            # Should not raise any exceptions
            validate_session_state()
    
    def test_handle_corrupted_session_state(self):
        """Test handling of corrupted session state."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Simulate corrupted state
            mock_session_state['generated_posts'] = "invalid_type"
            mock_session_state['editing_posts'] = None
            mock_session_state['generation_timestamp'] = 12345
            mock_session_state['target_platform'] = []
            
            # Recovery function
            def recover_session_state():
                if not isinstance(mock_session_state.get('generated_posts'), list):
                    mock_session_state['generated_posts'] = []
                if not isinstance(mock_session_state.get('editing_posts'), list):
                    mock_session_state['editing_posts'] = []
                if not isinstance(mock_session_state.get('generation_timestamp'), (str, type(None))):
                    mock_session_state['generation_timestamp'] = None
                if not isinstance(mock_session_state.get('target_platform'), (str, type(None))):
                    mock_session_state['target_platform'] = None
            
            # Execute recovery
            recover_session_state()
            
            # Verify recovery
            assert mock_session_state['generated_posts'] == []
            assert mock_session_state['editing_posts'] == []
            assert mock_session_state['generation_timestamp'] is None
            assert mock_session_state['target_platform'] is None
    
    def test_session_state_synchronization(self):
        """Test synchronization between generated_posts and editing_posts."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Initial synchronization
            generated = ["Post A", "Post B", "Post C"]
            mock_session_state['generated_posts'] = generated
            mock_session_state['editing_posts'] = generated.copy()
            
            # Verify initial sync
            assert len(mock_session_state['generated_posts']) == len(mock_session_state['editing_posts'])
            
            # Test sync after post deletion
            mock_session_state['editing_posts'].pop(1)  # Remove second post
            
            # Sync function
            def sync_editing_posts():
                if len(mock_session_state['editing_posts']) != len(mock_session_state['generated_posts']):
                    # Re-sync from generated posts
                    mock_session_state['editing_posts'] = mock_session_state['generated_posts'].copy()
            
            sync_editing_posts()
            
            # Verify re-sync
            assert len(mock_session_state['generated_posts']) == len(mock_session_state['editing_posts'])
            assert mock_session_state['editing_posts'] == ["Post A", "Post B", "Post C"]


class TestSessionStateIntegration:
    """Tests for session state integration with UI components."""
    
    @patch('streamlit.text_area')
    def test_session_state_text_area_integration(self, mock_text_area):
        """Test integration between session state and text area components."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = ["Original post content"]
            
            # Mock text area return value (simulating user edit)
            mock_text_area.return_value = "Edited post content"
            
            # Simulate text area creation with session state key
            def create_text_area(index):
                key = f"post_{index}"
                value = mock_session_state['editing_posts'][index]
                return mock_text_area(
                    label=f"Post {index + 1}",
                    value=value,
                    key=key
                )
            
            # Create text area and get edited value
            edited_content = create_text_area(0)
            
            # Update session state with edited content
            mock_session_state['editing_posts'][0] = edited_content
            
            # Verify integration
            mock_text_area.assert_called_once()
            assert mock_session_state['editing_posts'][0] == "Edited post content"
    
    def test_session_state_callback_updates(self):
        """Test session state updates via Streamlit callbacks."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['editing_posts'] = ["Post 1", "Post 2", "Post 3"]
            
            # Simulate callback for post deletion
            def delete_post_callback(index):
                if 0 <= index < len(mock_session_state['editing_posts']):
                    mock_session_state['editing_posts'].pop(index)
            
            # Simulate callback for post reordering
            def reorder_posts_callback(from_index, to_index):
                posts = mock_session_state['editing_posts']
                if 0 <= from_index < len(posts) and 0 <= to_index < len(posts):
                    post = posts.pop(from_index)
                    posts.insert(to_index, post)
            
            # Test deletion
            delete_post_callback(1)
            assert len(mock_session_state['editing_posts']) == 2
            assert mock_session_state['editing_posts'] == ["Post 1", "Post 3"]
            
            # Test reordering
            reorder_posts_callback(0, 1)
            assert mock_session_state['editing_posts'] == ["Post 3", "Post 1"]
    
    def test_session_state_platform_specific_validation(self):
        """Test platform-specific validation using session state."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            mock_session_state['target_platform'] = "X"
            mock_session_state['editing_posts'] = [
                "Short post",
                "This is a very long post that exceeds Twitter's character limit and should trigger a validation warning for the user"
            ]
            
            # Platform limits
            platform_limits = {
                "X": 280,
                "LinkedIn": 3000,
                "Facebook": 63206,
                "Instagram": 2200
            }
            
            # Validation function
            def validate_posts_for_platform():
                platform = mock_session_state['target_platform']
                if platform not in platform_limits:
                    return []
                
                limit = platform_limits[platform]
                violations = []
                
                for i, post in enumerate(mock_session_state['editing_posts']):
                    if len(post) > limit:
                        violations.append({
                            'index': i,
                            'length': len(post),
                            'limit': limit,
                            'platform': platform
                        })
                
                return violations
            
            # Test validation
            violations = validate_posts_for_platform()
            
            assert len(violations) == 1
            assert violations[0]['index'] == 1
            assert violations[0]['length'] > 280
            assert violations[0]['limit'] == 280
            assert violations[0]['platform'] == "X"