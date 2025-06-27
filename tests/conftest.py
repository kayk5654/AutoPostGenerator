import pytest
import io
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pandas as pd


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