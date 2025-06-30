import pandas as pd
import re
from datetime import datetime
from typing import List, Tuple


def create_csv_export(posts: List[str], platform: str, include_metadata: bool = False) -> Tuple[str, str]:
    """
    Create CSV export of generated posts.
    
    Args:
        posts: List of final edited posts
        platform: Target platform name
        include_metadata: Whether to include additional metadata columns
        
    Returns:
        tuple[str, str]: (csv_string, filename)
    """
    # Generate timestamp for export
    export_timestamp = datetime.now().isoformat()
    
    # Sanitize and validate posts
    sanitized_posts = _sanitize_posts(posts)
    
    # Create base DataFrame with required columns
    data = {
        'post_text': sanitized_posts,
        'generation_timestamp': [export_timestamp] * len(sanitized_posts)
    }
    
    # Add optional metadata columns
    if include_metadata:
        data.update({
            'platform': [platform] * len(sanitized_posts),
            'post_number': list(range(1, len(sanitized_posts) + 1)),
            'character_count': [len(post) for post in sanitized_posts]
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Convert to CSV string with proper encoding
    csv_string = df.to_csv(index=False, encoding='utf-8')
    
    # Generate dynamic filename
    filename = _generate_filename(platform, export_timestamp)
    
    return csv_string, filename


def _sanitize_posts(posts: List[str]) -> List[str]:
    """
    Sanitize posts for CSV export safety.
    
    Args:
        posts: List of raw posts
        
    Returns:
        List of sanitized posts
    """
    sanitized = []
    
    for post in posts:
        if not isinstance(post, str):
            post = str(post)
        
        # Remove or escape potentially dangerous content
        sanitized_post = _sanitize_csv_content(post)
        
        # Only include non-empty posts
        if sanitized_post.strip():
            sanitized.append(sanitized_post)
    
    return sanitized


def _sanitize_csv_content(content: str) -> str:
    """
    Sanitize content for CSV safety with Unicode text sanitization.
    
    Phase 10.4: Enhanced with Unicode sanitization to ensure character encoding
    safety in exported CSV files, preventing corruption in Excel and other tools.
    
    Args:
        content: Raw content string
        
    Returns:
        Sanitized content string
    """
    import logging
    
    # Configure logger for this module
    logger = logging.getLogger(__name__)
    
    try:
        # Phase 10.4: Unicode sanitization FIRST to fix encoding issues in export
        # Import here to avoid circular imports and lazy loading
        from utils.text_sanitizer import get_text_sanitizer
        
        sanitizer = get_text_sanitizer()
        content = sanitizer.sanitize_text(content)
        logger.debug(f"Applied Unicode sanitization to export content: {len(content)} characters")
        
    except Exception as e:
        # Log the error but continue with original content for backward compatibility
        logger.warning(f"Unicode sanitization failed during export, continuing with original content: {str(e)}")
        pass
    
    # Remove null bytes and control characters (except newlines, tabs, carriage returns)
    content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
    
    # Handle potential CSV injection
    if content.strip().startswith(('=', '+', '-', '@')):
        # Prefix with apostrophe to prevent formula execution
        content = "'" + content
    
    # Normalize whitespace while preserving intentional formatting
    content = re.sub(r'\r\n', '\n', content)  # Normalize line endings
    content = re.sub(r'\r', '\n', content)    # Convert old Mac line endings
    
    return content


def _generate_filename(platform: str, timestamp: str) -> str:
    """
    Generate dynamic filename following the convention.
    
    Args:
        platform: Target platform name
        timestamp: ISO timestamp string
        
    Returns:
        Sanitized filename string
    """
    # Sanitize platform name for filename
    safe_platform = _sanitize_platform_name(platform)
    
    # Format timestamp for filename (remove colons and microseconds)
    safe_timestamp = timestamp.split('.')[0].replace(':', '-')
    
    return f"posts_for_{safe_platform}_{safe_timestamp}.csv"


def _sanitize_platform_name(platform: str) -> str:
    """
    Sanitize platform name for safe filename usage.
    
    Args:
        platform: Raw platform name
        
    Returns:
        Sanitized platform name
    """
    # Replace invalid filename characters with underscores
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ']
    sanitized = platform
    
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove any remaining problematic characters
    sanitized = re.sub(r'[^\w\-_.]', '_', sanitized)
    
    # Ensure it's not empty and doesn't start with a dot
    if not sanitized or sanitized.startswith('.'):
        sanitized = 'Platform'
    
    return sanitized


def validate_export_data(posts: List[str], platform: str) -> Tuple[bool, List[str]]:
    """
    Validate data before export.
    
    Args:
        posts: List of posts to validate
        platform: Target platform name
        
    Returns:
        tuple[bool, List[str]]: (is_valid, list_of_issues)
    """
    issues = []
    
    # Check for empty posts list
    if not posts:
        issues.append("No posts provided for export")
        return False, issues
    
    # Check for valid posts content
    valid_posts = [post for post in posts if post and post.strip()]
    if not valid_posts:
        issues.append("All posts are empty")
        return False, issues
    
    # Check platform name
    if not platform or not platform.strip():
        issues.append("Platform name is required")
        return False, issues
    
    # Platform-specific validation
    platform_issues = _validate_platform_compliance(valid_posts, platform)
    issues.extend(platform_issues)
    
    # CSV safety validation
    safety_issues = _validate_csv_safety(valid_posts)
    issues.extend(safety_issues)
    
    # Warning for empty posts (but don't fail validation)
    empty_count = len(posts) - len(valid_posts)
    if empty_count > 0:
        issues.append(f"Warning: {empty_count} empty post(s) will be excluded from export")
    
    # Consider validation successful if we have valid posts and no critical issues
    critical_issues = [issue for issue in issues if not issue.startswith("Warning:")]
    return len(critical_issues) == 0, issues


def _validate_platform_compliance(posts: List[str], platform: str) -> List[str]:
    """
    Validate posts against platform-specific requirements.
    
    Args:
        posts: List of posts to validate
        platform: Target platform name
        
    Returns:
        List of compliance issues
    """
    issues = []
    
    # Platform character limits
    platform_limits = {
        "X": 280,
        "LinkedIn": 3000,
        "Facebook": 63206,
        "Instagram": 2200
    }
    
    if platform in platform_limits:
        limit = platform_limits[platform]
        for i, post in enumerate(posts, 1):
            if len(post) > limit:
                excess = len(post) - limit
                issues.append(f"Warning: Post {i} exceeds {platform} character limit by {excess} characters")
    
    return issues


def _validate_csv_safety(posts: List[str]) -> List[str]:
    """
    Validate posts for CSV injection and safety concerns.
    
    Args:
        posts: List of posts to validate
        
    Returns:
        List of safety issues
    """
    issues = []
    
    dangerous_patterns = ['=', '+cmd', '-cmd', '@SUM', '@EXEC']
    
    for i, post in enumerate(posts, 1):
        # Check for potential CSV injection
        post_start = post.strip()
        if post_start.startswith(('=', '+', '-', '@')):
            # Check for dangerous function patterns
            upper_post = post.upper()
            if any(pattern.upper() in upper_post for pattern in ['SUM(', 'CMD', 'EXEC', 'SYSTEM', 'SHELL']):
                issues.append(f"Warning: Post {i} contains potential CSV injection patterns")
    
    return issues


def get_export_statistics(posts: List[str]) -> dict:
    """
    Get statistics about the export data.
    
    Args:
        posts: List of posts to analyze
        
    Returns:
        Dictionary with export statistics
    """
    valid_posts = [post for post in posts if post and post.strip()]
    
    if not valid_posts:
        return {
            'total_posts': len(posts),
            'valid_posts': 0,
            'empty_posts': len(posts),
            'total_characters': 0,
            'average_length': 0,
            'estimated_file_size_kb': 0
        }
    
    total_chars = sum(len(post) for post in valid_posts)
    avg_length = total_chars / len(valid_posts) if valid_posts else 0
    
    # Estimate file size (rough calculation)
    # CSV overhead: headers, commas, quotes, newlines, timestamps
    estimated_size_bytes = total_chars * 1.5 + len(valid_posts) * 50  # rough estimate
    estimated_size_kb = estimated_size_bytes / 1024
    
    return {
        'total_posts': len(posts),
        'valid_posts': len(valid_posts),
        'empty_posts': len(posts) - len(valid_posts),
        'total_characters': total_chars,
        'average_length': int(avg_length),
        'estimated_file_size_kb': round(estimated_size_kb, 2)
    }