import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime
import io


class TestExportValidation:
    """Tests for CSV export validation functionality."""
    
    def test_minimum_post_count_validation(self):
        """Test validation of minimum post count for export."""
        # Function to validate minimum post count
        def validate_minimum_posts(posts, min_count=1):
            valid_posts = [post for post in posts if post.strip()]
            if len(valid_posts) < min_count:
                return False, f"At least {min_count} valid post(s) required for export"
            return True, f"Ready to export {len(valid_posts)} posts"
        
        # Test cases
        test_cases = [
            ([], 1, False, "At least 1 valid post(s) required for export"),
            ([""], 1, False, "At least 1 valid post(s) required for export"),
            (["   ", "\n", "\t"], 1, False, "At least 1 valid post(s) required for export"),
            (["Valid post"], 1, True, "Ready to export 1 posts"),
            (["Post 1", "Post 2"], 2, True, "Ready to export 2 posts"),
            (["Post 1"], 2, False, "At least 2 valid post(s) required for export"),
            (["Valid", "", "Also valid"], 2, True, "Ready to export 2 posts")
        ]
        
        for posts, min_count, expected_valid, expected_message in test_cases:
            is_valid, message = validate_minimum_posts(posts, min_count)
            assert is_valid == expected_valid
            assert message == expected_message
    
    def test_post_content_validation(self):
        """Test validation of post content quality."""
        # Function to validate post content
        def validate_post_content(posts):
            issues = []
            warnings = []
            
            for i, post in enumerate(posts, 1):
                # Check for empty posts
                if not post.strip():
                    issues.append(f"Post {i} is empty")
                    continue
                
                # Check for very short posts
                if len(post.strip()) < 10:
                    warnings.append(f"Post {i} is very short ({len(post.strip())} characters)")
                
                # Check for very long posts
                if len(post) > 2000:
                    warnings.append(f"Post {i} is very long ({len(post)} characters)")
                
                # Check for suspicious content patterns
                if post.count('\n') > 10:
                    warnings.append(f"Post {i} has many line breaks")
                
                if post.count('http') > 3:
                    warnings.append(f"Post {i} has multiple URLs")
            
            return issues, warnings
        
        # Test different content scenarios
        test_posts = [
            "",  # Empty
            "Hi",  # Too short
            "This is a reasonable length post with good content",  # Good
            "A" * 2500,  # Too long
            "Post\nwith\nmany\nline\nbreaks\nhere\nthat\nmight\ncause\nissues\nwith\nformatting\nin\nCSV",  # Many line breaks
            "Check out http://link1.com and http://link2.com and http://link3.com and http://link4.com"  # Multiple URLs
        ]
        
        issues, warnings = validate_post_content(test_posts)
        
        # Verify issues detected
        assert len(issues) == 1
        assert "Post 1 is empty" in issues
        
        # Verify warnings detected
        assert len(warnings) >= 4  # Short, long, line breaks, URLs
        assert any("very short" in warning for warning in warnings)
        assert any("very long" in warning for warning in warnings)
        assert any("line breaks" in warning for warning in warnings)
        assert any("multiple URLs" in warning for warning in warnings)
    
    def test_platform_specific_validation(self):
        """Test platform-specific content validation."""
        # Platform limits and rules
        platform_rules = {
            "X": {
                "max_length": 280,
                "hashtag_limit": 2,
                "url_limit": 1
            },
            "LinkedIn": {
                "max_length": 3000,
                "hashtag_limit": 5,
                "url_limit": 3
            },
            "Facebook": {
                "max_length": 63206,
                "hashtag_limit": 10,
                "url_limit": 5
            },
            "Instagram": {
                "max_length": 2200,
                "hashtag_limit": 30,
                "url_limit": 1
            }
        }
        
        # Function to validate against platform rules
        def validate_platform_compliance(posts, platform):
            if platform not in platform_rules:
                return True, []
            
            rules = platform_rules[platform]
            violations = []
            
            for i, post in enumerate(posts, 1):
                # Length check
                if len(post) > rules["max_length"]:
                    excess = len(post) - rules["max_length"]
                    violations.append(f"Post {i} exceeds {platform} character limit by {excess} characters")
                
                # Hashtag check
                hashtag_count = post.count('#')
                if hashtag_count > rules["hashtag_limit"]:
                    violations.append(f"Post {i} has {hashtag_count} hashtags (limit: {rules['hashtag_limit']})")
                
                # URL check
                url_count = post.count('http')
                if url_count > rules["url_limit"]:
                    violations.append(f"Post {i} has {url_count} URLs (limit: {rules['url_limit']})")
            
            return len(violations) == 0, violations
        
        # Test posts with platform violations
        test_posts = [
            "A" * 300,  # Too long for X
            "Post with #too #many #hashtags #for #twitter #platform #rules",  # Too many hashtags for X
            "Check http://link1.com and http://link2.com for more info",  # Too many URLs for X/Instagram
            "Valid post for most platforms"  # Should be fine for all
        ]
        
        # Test X platform (most restrictive)
        is_valid, violations = validate_platform_compliance(test_posts, "X")
        assert is_valid is False
        assert len(violations) >= 3  # Length, hashtags, URLs
        assert any("character limit" in v for v in violations)
        assert any("hashtags" in v for v in violations)
        assert any("URLs" in v for v in violations)
        
        # Test LinkedIn platform (more lenient)
        is_valid, violations = validate_platform_compliance(test_posts, "LinkedIn")
        assert len(violations) < 3  # Should have fewer violations
    
    def test_csv_format_validation(self):
        """Test CSV format validation and safety."""
        # Function to validate CSV safety
        def validate_csv_safety(posts):
            dangerous_patterns = [
                "=",  # Formula injection
                "+",  # Formula injection
                "-",  # Formula injection
                "@",  # Formula injection
                "\x00",  # Null bytes
                "\x01",  # Control characters
                '"""',  # Multiple quotes
            ]
            
            safety_issues = []
            
            for i, post in enumerate(posts, 1):
                # Check for dangerous patterns at start of post
                if post.strip().startswith(('=', '+', '-', '@')):
                    safety_issues.append(f"Post {i} starts with potentially dangerous character: {post.strip()[0]}")
                
                # Check for null bytes and control characters
                if '\x00' in post or any(ord(c) < 32 and c not in '\n\r\t' for c in post):
                    safety_issues.append(f"Post {i} contains control characters")
                
                # Check for CSV injection patterns
                if post.strip().startswith('=') and any(func in post.upper() for func in ['SUM', 'CMD', 'EXEC', 'SYSTEM']):
                    safety_issues.append(f"Post {i} contains potential CSV injection")
                
                # Check for excessive quotes
                if post.count('"') > 10:
                    safety_issues.append(f"Post {i} has excessive quote characters")
            
            return len(safety_issues) == 0, safety_issues
        
        # Test potentially dangerous content
        dangerous_posts = [
            "=SUM(A1:A10)",  # Formula injection
            "+cmd|' /C calc'!A0",  # Command injection
            "=HYPERLINK(\"http://evil.com\", \"Click me\")",  # Hyperlink injection
            "Post with \x00 null byte",  # Null byte
            "Post with 'many \"quotes\" and \"more quotes\" and \"even more\"'",  # Many quotes
            "Normal safe post content"  # Safe content
        ]
        
        is_safe, issues = validate_csv_safety(dangerous_posts)
        assert is_safe is False
        assert len(issues) >= 3  # Should detect multiple safety issues
        assert any("dangerous character" in issue for issue in issues)
        assert any("injection" in issue for issue in issues)
    
    def test_export_data_integrity(self):
        """Test data integrity during export process."""
        # Function to verify data integrity
        def verify_export_integrity(original_posts, exported_csv):
            # Parse the exported CSV
            df = pd.read_csv(io.StringIO(exported_csv))
            
            integrity_checks = {
                'post_count_matches': len(df) == len(original_posts),
                'all_posts_present': True,
                'no_data_corruption': True,
                'timestamps_valid': True,
                'encoding_preserved': True
            }
            
            # Check if all posts are present
            for i, original_post in enumerate(original_posts):
                if i < len(df):
                    exported_post = df.iloc[i]['post_text']
                    if original_post != exported_post:
                        integrity_checks['all_posts_present'] = False
                        break
                else:
                    integrity_checks['all_posts_present'] = False
                    break
            
            # Check for data corruption (basic checks)
            for _, row in df.iterrows():
                post_text = row['post_text']
                if pd.isna(post_text) or not isinstance(post_text, str):
                    integrity_checks['no_data_corruption'] = False
                    break
            
            # Check timestamp validity
            for _, row in df.iterrows():
                timestamp = row['generation_timestamp']
                try:
                    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    integrity_checks['timestamps_valid'] = False
                    break
            
            # Check encoding preservation (Unicode characters)
            for original_post in original_posts:
                if any(ord(c) > 127 for c in original_post):  # Contains non-ASCII
                    found_in_export = any(original_post in str(row['post_text']) for _, row in df.iterrows())
                    if not found_in_export:
                        integrity_checks['encoding_preserved'] = False
                        break
            
            return integrity_checks
        
        # Test with diverse content
        test_posts = [
            "Simple ASCII post",
            "Post with émojis 🚀💡🎉",
            "Post with Chinese: 你好世界",
            "Post with quotes \"and\" commas, semicolons;",
            "Post with\nnewlines\nand\ttabs",
            "Post with special chars: @#$%^&*()"
        ]
        
        # Simulate CSV export
        csv_content = "post_text,generation_timestamp\n"
        for post in test_posts:
            # Simple CSV formatting (in real implementation, use proper CSV escaping)
            escaped_post = post.replace('"', '""')  # Basic quote escaping
            csv_content += f'"{escaped_post}",2024-01-15T10:30:00\n'
        
        # Verify integrity
        integrity = verify_export_integrity(test_posts, csv_content)
        
        # All integrity checks should pass
        for check_name, passed in integrity.items():
            assert passed, f"Integrity check failed: {check_name}"
    
    def test_filename_security_validation(self):
        """Test filename security and validity."""
        # Function to validate filename security
        def validate_filename_security(filename):
            security_issues = []
            
            # Check for path traversal
            if '..' in filename:
                security_issues.append("Filename contains path traversal sequences")
            
            # Check for absolute paths
            if filename.startswith('/') or (len(filename) > 2 and filename[1] == ':'):
                security_issues.append("Filename appears to be an absolute path")
            
            # Check for invalid characters
            invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\x00']
            for char in invalid_chars:
                if char in filename:
                    security_issues.append(f"Filename contains invalid character: {char}")
            
            # Check length
            if len(filename) > 255:
                security_issues.append("Filename is too long")
            
            # Check for reserved names (Windows)
            reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
            base_name = filename.split('.')[0].upper()
            if base_name in reserved_names:
                security_issues.append(f"Filename uses reserved name: {base_name}")
            
            return len(security_issues) == 0, security_issues
        
        # Test various filename scenarios
        test_filenames = [
            "posts_for_LinkedIn_2024-01-15T10:30:00.csv",  # Valid
            "../../../etc/passwd",  # Path traversal
            "/absolute/path/file.csv",  # Absolute path  
            "C:\\Windows\\file.csv",  # Windows absolute path
            "file<with>invalid:chars.csv",  # Invalid characters
            "CON.csv",  # Reserved name
            "a" * 300 + ".csv",  # Too long
            "posts_for_X_2024-01-15T10:30:00.csv",  # Valid
            "posts_for_Platform\x00WithNull.csv"  # Null byte
        ]
        
        results = []
        for filename in test_filenames:
            is_safe, issues = validate_filename_security(filename)
            results.append((filename, is_safe, issues))
        
        # First filename should be valid
        assert results[0][1] is True
        assert len(results[0][2]) == 0
        
        # Path traversal should be detected
        assert results[1][1] is False
        assert any("path traversal" in issue for issue in results[1][2])
        
        # Absolute paths should be detected
        assert results[2][1] is False
        assert any("absolute path" in issue for issue in results[2][2])
        
        # Invalid characters should be detected
        assert results[4][1] is False
        assert any("invalid character" in issue for issue in results[4][2])
        
        # Reserved names should be detected
        assert results[5][1] is False
        assert any("reserved name" in issue for issue in results[5][2])
        
        # Long filenames should be detected
        assert results[6][1] is False
        assert any("too long" in issue for issue in results[6][2])
    
    def test_export_performance_validation(self):
        """Test export performance considerations."""
        # Function to estimate export performance
        def estimate_export_performance(posts, include_metadata=False):
            # Calculate estimated processing time and memory usage
            total_chars = sum(len(post) for post in posts)
            post_count = len(posts)
            
            # Rough estimates (in practice, these would be based on actual benchmarks)
            estimated_time_ms = (total_chars * 0.001) + (post_count * 0.1)  # Simple linear estimate
            estimated_memory_mb = (total_chars * 2) / (1024 * 1024)  # UTF-8 overhead
            
            if include_metadata:
                estimated_time_ms *= 1.2  # 20% overhead for metadata
                estimated_memory_mb *= 1.3  # 30% overhead for additional columns
            
            # Performance warnings
            warnings = []
            if estimated_time_ms > 1000:  # > 1 second
                warnings.append(f"Export may take {estimated_time_ms/1000:.1f} seconds")
            
            if estimated_memory_mb > 10:  # > 10MB
                warnings.append(f"Export may use {estimated_memory_mb:.1f}MB memory")
            
            if post_count > 1000:
                warnings.append(f"Large dataset: {post_count} posts")
            
            return {
                'estimated_time_ms': estimated_time_ms,
                'estimated_memory_mb': estimated_memory_mb,
                'warnings': warnings,
                'is_large_export': estimated_time_ms > 1000 or estimated_memory_mb > 10
            }
        
        # Test different dataset sizes
        test_scenarios = [
            (["Short post"] * 10, False),  # Small dataset
            (["Medium length post with reasonable content"] * 100, False),  # Medium dataset
            (["Very long post with extensive content " * 50] * 500, True),  # Large dataset
            (["Huge post content " * 100] * 1000, True)  # Very large dataset
        ]
        
        for posts, include_metadata in test_scenarios:
            performance = estimate_export_performance(posts, include_metadata)
            
            # Verify performance metrics are reasonable
            assert performance['estimated_time_ms'] >= 0
            assert performance['estimated_memory_mb'] >= 0
            assert isinstance(performance['warnings'], list)
            assert isinstance(performance['is_large_export'], bool)
            
            # Large datasets should be flagged
            if len(posts) > 500:
                assert performance['is_large_export'] is True
                assert len(performance['warnings']) > 0