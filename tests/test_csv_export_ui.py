import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
import pandas as pd
from datetime import datetime


class TestCSVExportUIIntegration:
    """Tests for CSV export UI integration with Streamlit."""
    
    @patch('streamlit.download_button')
    def test_download_button_configuration(self, mock_download_button):
        """Test download button configuration for CSV export."""
        # Mock return value
        mock_download_button.return_value = True
        
        # Sample data for export
        posts = ["Post 1", "Post 2", "Post 3"]
        platform = "LinkedIn"
        csv_data = "post_text,generation_timestamp\nPost 1,2024-01-15T10:30:00\nPost 2,2024-01-15T10:30:00\nPost 3,2024-01-15T10:30:00"
        filename = "posts_for_LinkedIn_2024-01-15T10:30:00.csv"
        
        # Function to create download button
        def create_csv_download_button():
            return mock_download_button(
                label="📄 Export to CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                help="Download your edited posts as a CSV file for easy sharing and analysis"
            )
        
        # Execute download button creation
        result = create_csv_download_button()
        
        # Verify download button configuration
        mock_download_button.assert_called_once_with(
            label="📄 Export to CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv", 
            help="Download your edited posts as a CSV file for easy sharing and analysis"
        )
        assert result is True
    
    def test_conditional_export_section_display(self):
        """Test conditional display of export section."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Test case 1: No posts generated - should not show export
            mock_session_state['generated_posts'] = []
            mock_session_state['editing_posts'] = []
            
            def should_show_export_section():
                return len(mock_session_state.get('generated_posts', [])) > 0
            
            assert should_show_export_section() is False
            
            # Test case 2: Posts generated - should show export
            mock_session_state['generated_posts'] = ["Post 1", "Post 2"]
            mock_session_state['editing_posts'] = ["Edited Post 1", "Edited Post 2"]
            
            assert should_show_export_section() is True
    
    @patch('streamlit.info')
    @patch('streamlit.warning')
    @patch('streamlit.success')
    def test_export_validation_feedback(self, mock_success, mock_warning, mock_info):
        """Test export validation and user feedback."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Function to validate and provide feedback for export
            def validate_export_readiness():
                posts = mock_session_state.get('editing_posts', [])
                
                if not posts:
                    mock_info("📝 No posts to export. Generate posts first.")
                    return False
                
                empty_posts = sum(1 for post in posts if not post.strip())
                if empty_posts > 0:
                    mock_warning(f"⚠️ {empty_posts} post(s) are empty and will be excluded from export")
                
                valid_posts = [post for post in posts if post.strip()]
                if valid_posts:
                    mock_success(f"✅ Ready to export {len(valid_posts)} posts!")
                    return True
                
                return False
            
            # Test case 1: No posts
            mock_session_state['editing_posts'] = []
            result = validate_export_readiness()
            assert result is False
            mock_info.assert_called_with("📝 No posts to export. Generate posts first.")
            
            # Reset mocks
            mock_info.reset_mock()
            mock_warning.reset_mock()
            mock_success.reset_mock()
            
            # Test case 2: Posts with some empty
            mock_session_state['editing_posts'] = ["Valid post", "", "Another valid post", "   "]
            result = validate_export_readiness()
            assert result is True
            mock_warning.assert_called_with("⚠️ 2 post(s) are empty and will be excluded from export")
            mock_success.assert_called_with("✅ Ready to export 2 posts!")
            
            # Reset mocks
            mock_warning.reset_mock()
            mock_success.reset_mock()
            
            # Test case 3: All valid posts
            mock_session_state['editing_posts'] = ["Post 1", "Post 2", "Post 3"]
            result = validate_export_readiness()
            assert result is True
            mock_warning.assert_not_called()
            mock_success.assert_called_with("✅ Ready to export 3 posts!")
    
    @patch('streamlit.expander')
    @patch('streamlit.dataframe')
    def test_export_preview_functionality(self, mock_dataframe, mock_expander):
        """Test CSV export preview functionality."""
        # Mock expander context manager
        mock_expander_context = Mock()
        mock_expander.return_value.__enter__ = Mock(return_value=mock_expander_context)
        mock_expander.return_value.__exit__ = Mock(return_value=None)
        
        # Sample export data
        posts = ["Post 1", "Post 2", "Post 3"]
        platform = "LinkedIn"
        
        # Function to show export preview
        def show_export_preview():
            with mock_expander("🔍 Preview Export Data", expanded=False):
                # Create preview DataFrame
                preview_data = {
                    'post_text': posts,
                    'generation_timestamp': ['2024-01-15T10:30:00'] * len(posts),
                    'platform': [platform] * len(posts),
                    'post_number': list(range(1, len(posts) + 1)),
                    'character_count': [len(post) for post in posts]
                }
                preview_df = pd.DataFrame(preview_data)
                
                mock_dataframe(preview_df)
                
                return preview_df
        
        # Execute preview
        result_df = show_export_preview()
        
        # Verify preview components
        mock_expander.assert_called_once_with("🔍 Preview Export Data", expanded=False)
        mock_dataframe.assert_called_once()
        
        # Verify preview data structure
        assert len(result_df) == 3
        assert list(result_df.columns) == ['post_text', 'generation_timestamp', 'platform', 'post_number', 'character_count']
        assert result_df.iloc[0]['post_text'] == "Post 1"
        assert result_df.iloc[0]['platform'] == "LinkedIn"
        assert result_df.iloc[0]['post_number'] == 1
        assert result_df.iloc[0]['character_count'] == 6  # len("Post 1")
    
    @patch('streamlit.columns')
    @patch('streamlit.metric')
    def test_export_statistics_display(self, mock_metric, mock_columns):
        """Test display of export statistics."""
        # Mock columns
        mock_col1, mock_col2, mock_col3, mock_col4 = Mock(), Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3, mock_col4]
        
        posts = ["Short", "Medium length post", "Very long post with lots of content here"]
        platform = "LinkedIn"
        
        # Function to display export statistics
        def display_export_statistics():
            col1, col2, col3, col4 = mock_columns(4)
            
            with col1:
                mock_metric("Total Posts", len(posts))
            
            with col2:
                total_chars = sum(len(post) for post in posts)
                mock_metric("Total Characters", total_chars)
            
            with col3:
                avg_length = int(sum(len(post) for post in posts) / len(posts))
                mock_metric("Avg Length", avg_length)
            
            with col4:
                file_size_kb = round(sum(len(post.encode('utf-8')) for post in posts) / 1024, 2)
                mock_metric("Est. File Size", f"{file_size_kb} KB")
        
        # Execute statistics display
        display_export_statistics()
        
        # Verify statistics
        mock_columns.assert_called_once_with(4)
        assert mock_metric.call_count == 4
        
        # Verify specific metrics
        calls = mock_metric.call_args_list
        assert calls[0][0] == ("Total Posts", 3)
        assert calls[1][0] == ("Total Characters", 58)  # Sum of post lengths
        assert calls[2][0] == ("Avg Length", 19)  # Average length
        assert "KB" in str(calls[3][0][1])  # File size with KB unit
    
    @patch('streamlit.selectbox')
    @patch('streamlit.checkbox')
    def test_export_options_configuration(self, mock_checkbox, mock_selectbox):
        """Test export options and configuration."""
        # Mock return values
        mock_selectbox.side_effect = ["UTF-8", "ISO 8601"]
        mock_checkbox.side_effect = [True, False, True, False]
        
        # Function to create export options
        def create_export_options():
            # Encoding selection
            encoding = mock_selectbox(
                "File Encoding",
                ["UTF-8", "ISO-8859-1", "Windows-1252"],
                index=0,
                help="Choose character encoding for the CSV file"
            )
            
            # Timestamp format
            timestamp_format = mock_selectbox(
                "Timestamp Format", 
                ["ISO 8601", "RFC 3339", "Custom"],
                index=0,
                help="Select timestamp format for the export"
            )
            
            # Optional columns
            include_platform = mock_checkbox("Include Platform Column", value=True)
            include_post_number = mock_checkbox("Include Post Number", value=False)
            include_char_count = mock_checkbox("Include Character Count", value=True)
            include_metadata = mock_checkbox("Include Generation Metadata", value=False)
            
            return {
                'encoding': encoding,
                'timestamp_format': timestamp_format,
                'include_platform': include_platform,
                'include_post_number': include_post_number,
                'include_char_count': include_char_count,
                'include_metadata': include_metadata
            }
        
        # Execute options creation
        options = create_export_options()
        
        # Verify options
        assert mock_selectbox.call_count == 2
        assert mock_checkbox.call_count == 4
        
        # Verify option values
        assert options['encoding'] == "UTF-8"
        assert options['timestamp_format'] == "ISO 8601"
        assert options['include_platform'] is True
        assert options['include_post_number'] is False
        assert options['include_char_count'] is True
        assert options['include_metadata'] is False
    
    @patch('streamlit.error')
    def test_export_error_handling(self, mock_error):
        """Test error handling in export UI."""
        with patch('streamlit.session_state', {}) as mock_session_state:
            # Function to handle export with error scenarios
            def handle_export_with_errors():
                posts = mock_session_state.get('editing_posts', [])
                platform = mock_session_state.get('target_platform')
                
                # Error case 1: No platform selected
                if not platform:
                    mock_error("❌ No target platform selected. Please generate posts first.")
                    return False
                
                # Error case 2: No valid posts
                valid_posts = [post for post in posts if post.strip()]
                if not valid_posts:
                    mock_error("❌ No valid posts to export. Please edit your posts first.")
                    return False
                
                # Error case 3: Platform name contains invalid characters
                invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
                if any(char in platform for char in invalid_chars):
                    mock_error(f"❌ Platform name '{platform}' contains invalid characters for filename.")
                    return False
                
                return True
            
            # Test case 1: No platform
            mock_session_state['editing_posts'] = ["Valid post"]
            mock_session_state['target_platform'] = None
            
            result = handle_export_with_errors()
            assert result is False
            mock_error.assert_called_with("❌ No target platform selected. Please generate posts first.")
            
            # Reset mock
            mock_error.reset_mock()
            
            # Test case 2: No valid posts
            mock_session_state['editing_posts'] = ["", "   ", "\n"]
            mock_session_state['target_platform'] = "LinkedIn"
            
            result = handle_export_with_errors()
            assert result is False
            mock_error.assert_called_with("❌ No valid posts to export. Please edit your posts first.")
            
            # Reset mock
            mock_error.reset_mock()
            
            # Test case 3: Invalid platform name
            mock_session_state['editing_posts'] = ["Valid post"]
            mock_session_state['target_platform'] = "Platform/With:Invalid*Chars"
            
            result = handle_export_with_errors()
            assert result is False
            mock_error.assert_called_with("❌ Platform name 'Platform/With:Invalid*Chars' contains invalid characters for filename.")
            
            # Reset mock
            mock_error.reset_mock()
            
            # Test case 4: Valid scenario
            mock_session_state['editing_posts'] = ["Valid post"]
            mock_session_state['target_platform'] = "LinkedIn"
            
            result = handle_export_with_errors()
            assert result is True
            mock_error.assert_not_called()


class TestCSVExportFeatures:
    """Tests for advanced CSV export features."""
    
    def test_export_with_metadata_columns(self):
        """Test export with optional metadata columns."""
        posts = ["Post 1", "Post 2", "Post 3"]
        platform = "LinkedIn"
        
        # Function to create export with metadata
        def create_export_with_metadata(include_metadata=True):
            data = {
                'post_text': posts,
                'generation_timestamp': ['2024-01-15T10:30:00'] * len(posts)
            }
            
            if include_metadata:
                data.update({
                    'platform': [platform] * len(posts),
                    'post_number': list(range(1, len(posts) + 1)),
                    'character_count': [len(post) for post in posts]
                })
            
            return pd.DataFrame(data)
        
        # Test with metadata
        df_with_metadata = create_export_with_metadata(True)
        expected_columns = ['post_text', 'generation_timestamp', 'platform', 'post_number', 'character_count']
        assert list(df_with_metadata.columns) == expected_columns
        assert len(df_with_metadata) == 3
        assert df_with_metadata.iloc[0]['platform'] == "LinkedIn"
        assert df_with_metadata.iloc[0]['post_number'] == 1
        assert df_with_metadata.iloc[0]['character_count'] == 6
        
        # Test without metadata
        df_without_metadata = create_export_with_metadata(False)
        expected_columns = ['post_text', 'generation_timestamp']
        assert list(df_without_metadata.columns) == expected_columns
        assert len(df_without_metadata) == 3
    
    def test_export_filename_sanitization(self):
        """Test filename sanitization for different platforms."""
        # Function to sanitize platform name for filename
        def sanitize_platform_name(platform):
            # Replace invalid filename characters
            invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ']
            sanitized = platform
            for char in invalid_chars:
                sanitized = sanitized.replace(char, '_')
            return sanitized
        
        test_cases = [
            ("LinkedIn", "LinkedIn"),
            ("X (Twitter)", "X_(Twitter)"),
            ("Facebook Stories", "Facebook_Stories"),
            ("Instagram/Reels", "Instagram_Reels"),
            ("TikTok: Business", "TikTok__Business"),
            ("Platform*With?Special<Chars>", "Platform_With_Special_Chars_")
        ]
        
        for original, expected in test_cases:
            result = sanitize_platform_name(original)
            assert result == expected
    
    def test_export_file_size_estimation(self):
        """Test file size estimation for export."""
        posts = [
            "Short post",
            "Medium length post with more content",
            "Very long post with lots of content, emojis 🚀💡🎉, and special characters @#$%^&*()"
        ]
        
        # Function to estimate file size
        def estimate_file_size(posts, include_metadata=False):
            # Base CSV structure
            headers = ['post_text', 'generation_timestamp']
            if include_metadata:
                headers.extend(['platform', 'post_number', 'character_count'])
            
            # Calculate size
            header_size = len(','.join(headers)) + 1  # +1 for newline
            
            # Data rows
            data_size = 0
            for post in posts:
                # Post text + timestamp + metadata if included
                row_size = len(post.encode('utf-8'))  # Post content
                row_size += 25  # Timestamp (ISO format)
                if include_metadata:
                    row_size += 20  # Platform name
                    row_size += 5   # Post number
                    row_size += 5   # Character count
                row_size += len(headers) - 1  # Commas
                row_size += 1  # Newline
                data_size += row_size
            
            total_size = header_size + data_size
            return total_size
        
        # Test file size estimation
        size_without_metadata = estimate_file_size(posts, False)
        size_with_metadata = estimate_file_size(posts, True)
        
        assert size_without_metadata > 0
        assert size_with_metadata > size_without_metadata
        assert size_with_metadata > 200  # Should be reasonable size for 3 posts
        assert size_with_metadata < 1000  # Should not be too large
    
    def test_export_encoding_options(self):
        """Test different encoding options for CSV export."""
        posts = ["Post with émojis 🚀", "Post with ñañá and café", "Post with 中文 characters"]
        
        # Function to test encoding compatibility
        def test_encoding_compatibility(posts, encoding):
            try:
                # Simulate CSV creation with specific encoding
                csv_content = "post_text,generation_timestamp\n"
                for post in posts:
                    csv_content += f'"{post}",2024-01-15T10:30:00\n'
                
                # Test encoding
                encoded_content = csv_content.encode(encoding)
                decoded_content = encoded_content.decode(encoding)
                
                return True, len(encoded_content)
            except UnicodeEncodeError:
                return False, 0
        
        # Test different encodings
        encodings = ['utf-8', 'utf-16', 'iso-8859-1', 'windows-1252']
        results = {}
        
        for encoding in encodings:
            success, size = test_encoding_compatibility(posts, encoding)
            results[encoding] = {'success': success, 'size': size}
        
        # UTF-8 should always work
        assert results['utf-8']['success'] is True
        assert results['utf-8']['size'] > 0
        
        # UTF-16 should work but be larger
        assert results['utf-16']['success'] is True
        assert results['utf-16']['size'] > results['utf-8']['size']
    
    @patch('streamlit.download_button')
    def test_large_file_export_warning(self, mock_download_button):
        """Test warning for large file exports."""
        # Create large dataset
        large_posts = [f"Post number {i} with substantial content " * 50 for i in range(1000)]
        platform = "LinkedIn"
        
        mock_download_button.return_value = True
        
        # Function to handle large file export
        def handle_large_file_export():
            # Estimate file size
            total_chars = sum(len(post) for post in large_posts)
            estimated_size_mb = (total_chars * 1.2) / (1024 * 1024)  # Rough estimate with overhead
            
            # Create download with size warning
            if estimated_size_mb > 1:  # Warn for files > 1MB
                label = f"📄 Export to CSV (⚠️ ~{estimated_size_mb:.1f}MB)"
                help_text = f"Large file warning: This export will be approximately {estimated_size_mb:.1f}MB"
            else:
                label = "📄 Export to CSV"
                help_text = "Download your posts as a CSV file"
            
            return mock_download_button(
                label=label,
                data="mock_csv_content",
                file_name=f"posts_for_{platform}_large.csv",
                mime="text/csv",
                help=help_text
            )
        
        # Execute large file export
        result = handle_large_file_export()
        
        # Verify warning in button label and help text
        call_args = mock_download_button.call_args
        assert "⚠️" in call_args[1]['label']
        assert "MB" in call_args[1]['label']
        assert "Large file warning" in call_args[1]['help']
        assert result is True