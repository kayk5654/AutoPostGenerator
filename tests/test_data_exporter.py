import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
from utils.data_exporter import create_csv_export


class TestCreateCSVExport:
    """Tests for create_csv_export function."""
    
    def test_create_csv_export_basic_functionality(self):
        """Test basic CSV export functionality."""
        posts = [
            "First post content here",
            "Second post with emojis 🚀", 
            "Third post with hashtags #innovation #tech"
        ]
        platform = "LinkedIn"
        
        csv_string, filename = create_csv_export(posts, platform)
        
        # Parse CSV to verify content
        import io
        df = pd.read_csv(io.StringIO(csv_string))
        
        # Verify DataFrame structure
        assert len(df) == 3
        assert list(df.columns) == ["post_text", "generation_timestamp"]
        
        # Verify post content
        assert df.iloc[0]["post_text"] == "First post content here"
        assert df.iloc[1]["post_text"] == "Second post with emojis 🚀"
        assert df.iloc[2]["post_text"] == "Third post with hashtags #innovation #tech"
        
        # Verify timestamps are present and valid ISO format
        for timestamp in df["generation_timestamp"]:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        # Verify filename format
        assert filename.startswith("posts_for_LinkedIn_")
        assert filename.endswith(".csv")
        assert len(filename.split("_")) >= 4  # posts_for_Platform_timestamp.csv
    
    def test_create_csv_export_different_platforms(self):
        """Test CSV export with different platforms."""
        posts = ["Test post"]
        platforms = ["X", "Facebook", "LinkedIn", "Instagram"]
        
        for platform in platforms:
            csv_string, filename = create_csv_export(posts, platform)
            
            # Verify platform in filename
            assert f"posts_for_{platform}_" in filename
            assert filename.endswith(".csv")
            
            # Verify CSV content
            import io
            df = pd.read_csv(io.StringIO(csv_string))
            assert len(df) == 1
            assert df.iloc[0]["post_text"] == "Test post"
    
    def test_create_csv_export_special_characters(self):
        """Test handling of special characters in posts."""
        posts = [
            "Post with émojis: 🚀🎉💡",
            "Post with quotes: \"Hello World\"",
            "Post with newlines:\nLine 1\nLine 2",
            "Post with commas, semicolons; and other: special chars @#$%"
        ]
        platform = "X"
        
        csv_string, filename = create_csv_export(posts, platform)
        
        # Parse CSV and verify special characters preserved
        import io
        df = pd.read_csv(io.StringIO(csv_string))
        
        assert len(df) == 4
        assert "🚀🎉💡" in df.iloc[0]["post_text"]
        assert "\"Hello World\"" in df.iloc[1]["post_text"]
        assert "\n" in df.iloc[2]["post_text"]
        assert "@#$%" in df.iloc[3]["post_text"]
    
    def test_create_csv_export_empty_posts_list(self):
        """Test handling of empty posts list."""
        posts = []
        platform = "LinkedIn"
        
        csv_string, filename = create_csv_export(posts, platform)
        
        # Should create empty DataFrame with correct columns
        import io
        df = pd.read_csv(io.StringIO(csv_string))
        
        assert len(df) == 0
        assert list(df.columns) == ["post_text", "generation_timestamp"]
        assert filename.startswith("posts_for_LinkedIn_")
    
    def test_create_csv_export_posts_with_whitespace(self):
        """Test cleaning and formatting of posts with extra whitespace."""
        posts = [
            "   Post with leading spaces",
            "Post with trailing spaces   ",
            "  Post with both  ",
            "\tPost with tabs\t",
            "Post\nwith\nmultiple\nlines"
        ]
        platform = "Facebook"
        
        csv_string, filename = create_csv_export(posts, platform)
        
        import io
        df = pd.read_csv(io.StringIO(csv_string))
        
        # Verify whitespace handling (should preserve intentional whitespace)
        assert len(df) == 5
        # Check that content is preserved (exact behavior depends on implementation)
        for i, post in enumerate(posts):
            assert df.iloc[i]["post_text"] is not None
            assert len(df.iloc[i]["post_text"].strip()) > 0
    
    def test_create_csv_export_very_long_posts(self):
        """Test handling of very long posts."""
        long_post = "A" * 5000  # Very long post
        posts = [long_post, "Short post"]
        platform = "LinkedIn"
        
        csv_string, filename = create_csv_export(posts, platform)
        
        import io
        df = pd.read_csv(io.StringIO(csv_string))
        
        assert len(df) == 2
        assert df.iloc[0]["post_text"] == long_post
        assert df.iloc[1]["post_text"] == "Short post"
    
    def test_create_csv_export_unicode_handling(self):
        """Test proper Unicode character handling."""
        posts = [
            "Post with Chinese: 你好世界",
            "Post with Arabic: مرحبا بالعالم", 
            "Post with Russian: Привет мир",
            "Post with French: Café résumé naïve",
            "Post with math symbols: α β γ δ ∑ ∏"
        ]
        platform = "Instagram"
        
        csv_string, filename = create_csv_export(posts, platform)
        
        import io
        df = pd.read_csv(io.StringIO(csv_string))
        
        assert len(df) == 5
        assert "你好世界" in df.iloc[0]["post_text"]
        assert "مرحبا بالعالم" in df.iloc[1]["post_text"]
        assert "Привет мир" in df.iloc[2]["post_text"]
        assert "Café résumé naïve" in df.iloc[3]["post_text"]
        assert "α β γ δ ∑ ∏" in df.iloc[4]["post_text"]
    
    @patch('utils.data_exporter.datetime')
    def test_create_csv_export_timestamp_format(self, mock_datetime):
        """Test that timestamps are in correct ISO format."""
        # Mock datetime to return predictable timestamp
        mock_now = MagicMock()
        mock_now.isoformat.return_value = "2024-01-15T10:30:45.123456"
        mock_datetime.now.return_value = mock_now
        
        posts = ["Test post"]
        platform = "X"
        
        csv_string, filename = create_csv_export(posts, platform)
        
        import io
        df = pd.read_csv(io.StringIO(csv_string))
        
        # Verify timestamp format
        timestamp = df.iloc[0]["generation_timestamp"]
        assert timestamp == "2024-01-15T10:30:45.123456"
        
        # Verify filename includes timestamp
        assert "2024-01-15T10:30:45.123456" in filename
    
    def test_create_csv_export_filename_generation(self):
        """Test dynamic filename generation."""
        posts = ["Test post"]
        
        # Test different platforms
        platforms = ["X", "Facebook", "LinkedIn", "Instagram"]
        
        for platform in platforms:
            csv_string, filename = create_csv_export(posts, platform)
            
            # Verify filename pattern: posts_for_{platform}_{timestamp}.csv
            parts = filename.split("_")
            assert parts[0] == "posts"
            assert parts[1] == "for"
            assert parts[2] == platform
            assert len(parts) >= 4  # At least posts_for_platform_timestamp
            assert filename.endswith(".csv")
    
    def test_create_csv_export_csv_format_validation(self):
        """Test that generated CSV follows proper format."""
        posts = [
            "Post 1",
            "Post 2", 
            "Post 3"
        ]
        platform = "LinkedIn"
        
        csv_string, filename = create_csv_export(posts, platform)
        
        # Verify CSV format
        lines = csv_string.strip().split('\n')
        
        # Check header
        assert lines[0] == "post_text,generation_timestamp"
        
        # Check data rows
        assert len(lines) == 4  # Header + 3 data rows
        
        # Each data row should have 2 columns
        for i in range(1, 4):
            parts = lines[i].split(',', 1)  # Split on first comma only
            assert len(parts) == 2
            assert f"Post {i}" in parts[0]
    
    def test_create_csv_export_posts_with_only_whitespace(self):
        """Test handling of posts that contain only whitespace."""
        posts = [
            "Valid post",
            "   ",  # Only spaces
            "\t\t",  # Only tabs  
            "\n\n",  # Only newlines
            "",  # Empty string
            "Another valid post"
        ]
        platform = "X"
        
        csv_string, filename = create_csv_export(posts, platform)
        
        import io
        df = pd.read_csv(io.StringIO(csv_string))
        
        # Verify handling (implementation should decide whether to filter or keep)
        assert len(df) >= 2  # At least the valid posts
        # First and last should be valid posts
        valid_posts = df[df["post_text"].str.strip() != ""]
        assert len(valid_posts) >= 2
    
    def test_create_csv_export_large_dataset(self):
        """Test performance with large number of posts."""
        # Create large dataset
        posts = [f"Post number {i} with content" for i in range(100)]
        platform = "LinkedIn"
        
        csv_string, filename = create_csv_export(posts, platform)
        
        import io
        df = pd.read_csv(io.StringIO(csv_string))
        
        assert len(df) == 100
        assert df.iloc[0]["post_text"] == "Post number 0 with content"
        assert df.iloc[99]["post_text"] == "Post number 99 with content"
        
        # Verify all have timestamps
        assert df["generation_timestamp"].notna().all()
    
    def test_create_csv_export_return_types(self):
        """Test that function returns correct types."""
        posts = ["Test post"]
        platform = "X"
        
        result = create_csv_export(posts, platform)
        
        # Should return tuple
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        csv_string, filename = result
        
        # Both should be strings
        assert isinstance(csv_string, str)
        assert isinstance(filename, str)
        
        # CSV string should be valid CSV
        assert "post_text,generation_timestamp" in csv_string
        
        # Filename should be valid filename
        assert filename.endswith(".csv")
        assert not filename.startswith(".")  # Not hidden file
        assert "/" not in filename  # No path separators
        assert "\\" not in filename  # No Windows path separators
    
    def test_create_csv_export_data_sanitization(self):
        """Test data sanitization for CSV safety."""
        posts = [
            'Post with "quotes" and commas, here',
            "Post with 'single quotes' and semicolons; here",
            "Post with equals = and pipes | here",
            "Post with formula =SUM(A1:A10) attempt"
        ]
        platform = "LinkedIn"
        
        csv_string, filename = create_csv_export(posts, platform)
        
        import io
        df = pd.read_csv(io.StringIO(csv_string))
        
        # Verify all posts preserved safely
        assert len(df) == 4
        
        # Check that potentially dangerous content is handled
        for i, post in enumerate(posts):
            post_text = df.iloc[i]["post_text"]
            assert isinstance(post_text, str)
            # Content should be preserved but made safe for CSV
            if "quotes" in post:
                assert "quotes" in post_text
            if "formula" in post:
                assert "SUM" in post_text  # Content preserved
    
    def test_create_csv_export_edge_case_platform_names(self):
        """Test with edge case platform names."""
        posts = ["Test post"]
        
        # Test with various platform name formats
        platforms = [
            "X",
            "facebook",  # lowercase
            "LINKEDIN",  # uppercase
            "Instagram Stories",  # with space
            "TikTok-Business"  # with hyphen
        ]
        
        for platform in platforms:
            csv_string, filename = create_csv_export(posts, platform)
            
            # Should handle all platform names
            assert platform.replace(" ", "_").replace("-", "_") in filename or platform in filename
            assert filename.endswith(".csv")
            
            # CSV should be valid regardless
            import io
            df = pd.read_csv(io.StringIO(csv_string))
            assert len(df) == 1
            assert df.iloc[0]["post_text"] == "Test post"


class TestCSVExportIntegration:
    """Integration tests for CSV export functionality."""
    
    def test_export_with_realistic_social_media_posts(self):
        """Test export with realistic social media post content."""
        posts = [
            "🚀 Excited to announce our new AI-powered feature! This game-changing update will revolutionize how you work. #Innovation #AI #TechNews",
            "💡 Pro tip: Did you know you can boost productivity by 40% with our latest integration? Here's how: [link] #ProductivityHack #Business",
            "🎉 Thank you to our amazing community! We've reached 10,000+ users and couldn't be more grateful. What feature should we build next? 🤔",
            "📊 Market research shows that 85% of businesses struggle with data analysis. Our new dashboard makes it simple. Try it free: [link] #DataAnalytics",
            "🔥 Weekend motivation: \"Success is not final, failure is not fatal: it is the courage to continue that counts.\" - Winston Churchill #MondayMotivation"
        ]
        platform = "LinkedIn"
        
        csv_string, filename = create_csv_export(posts, platform)
        
        # Parse and verify realistic content
        import io
        df = pd.read_csv(io.StringIO(csv_string))
        
        assert len(df) == 5
        
        # Verify emojis preserved
        assert "🚀" in df.iloc[0]["post_text"]
        assert "💡" in df.iloc[1]["post_text"]
        assert "🎉" in df.iloc[2]["post_text"]
        
        # Verify hashtags preserved
        assert "#Innovation" in df.iloc[0]["post_text"]
        assert "#ProductivityHack" in df.iloc[1]["post_text"]
        assert "#DataAnalytics" in df.iloc[3]["post_text"]
        
        # Verify special characters and punctuation
        assert "85%" in df.iloc[3]["post_text"]
        assert "10,000+" in df.iloc[2]["post_text"]
        assert '"Success is not final' in df.iloc[4]["post_text"]
        
        # Verify filename
        assert "posts_for_LinkedIn_" in filename
        assert filename.endswith(".csv")
    
    def test_export_workflow_end_to_end(self):
        """Test complete export workflow from generation to file creation."""
        # Simulate posts generated from different platforms
        test_scenarios = [
            {
                "platform": "X",
                "posts": [
                    "Short and punchy update! 💪 #Progress",
                    "Question for the community: What's your biggest challenge? 🤔",
                    "Quick tip thread 🧵 1/3: Start with the basics..."
                ]
            },
            {
                "platform": "LinkedIn", 
                "posts": [
                    "Professional insight: The future of remote work is hybrid. Here's what leaders need to know about building inclusive teams...",
                    "Industry analysis: Q3 showed remarkable growth in AI adoption across enterprise sectors. Key trends include...",
                    "Career advice: 5 essential skills for the modern workplace. Which ones are you developing? #CareerGrowth #Skills"
                ]
            },
            {
                "platform": "Instagram",
                "posts": [
                    "Behind the scenes ✨ Creating magic one pixel at a time 🎨 #BehindTheScenes #CreativeProcess",
                    "Mood: Productive Monday vibes 💻☕ What's inspiring you today? #MondayMotivation #Workspace",
                    "Tutorial Tuesday: How to create stunning visuals with basic tools 📸 Swipe for step-by-step guide ➡️"
                ]
            }
        ]
        
        for scenario in test_scenarios:
            platform = scenario["platform"]
            posts = scenario["posts"]
            
            csv_string, filename = create_csv_export(posts, platform)
            
            # Verify platform-specific filename
            assert f"posts_for_{platform}_" in filename
            
            # Parse and verify content
            import io
            df = pd.read_csv(io.StringIO(csv_string))
            
            assert len(df) == len(posts)
            
            # Verify all posts present and formatted correctly
            for i, expected_post in enumerate(posts):
                actual_post = df.iloc[i]["post_text"]
                assert expected_post == actual_post
                
                # Verify timestamp present
                timestamp = df.iloc[i]["generation_timestamp"]
                assert timestamp is not None
                assert len(timestamp) > 0
    
    def test_export_error_handling_and_recovery(self):
        """Test error handling in various export scenarios."""
        # Test with problematic content that might break CSV
        problematic_posts = [
            'Post with "nested quotes" and \'mixed quotes\'',
            "Post with line breaks\nand multiple\nlines of\ncontent",
            "Post with CSV injection attempt: =SUM(A1:A10),+cmd|' /C calc'!A0",
            "Post with NULL\x00characters and \x01control chars",
            "Post with extreme Unicode: 👨‍💻👩‍💻🧑‍💻 and 𝓯𝓪𝓷𝓬𝔂 𝓾𝓷𝓲𝓬𝓸𝓭𝓮"
        ]
        
        platform = "X"
        
        # Should not raise exceptions
        csv_string, filename = create_csv_export(problematic_posts, platform)
        
        # Should produce valid CSV
        import io
        df = pd.read_csv(io.StringIO(csv_string))
        
        # Should contain all posts (possibly sanitized)
        assert len(df) == len(problematic_posts)
        
        # Verify basic integrity
        assert list(df.columns) == ["post_text", "generation_timestamp"]
        
        # All rows should have data
        assert df["post_text"].notna().all()
        assert df["generation_timestamp"].notna().all()