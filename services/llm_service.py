def build_master_prompt(
    source_text: str, 
    brand_guide_text: str, 
    post_history: list, 
    platform: str, 
    count: int,
    advanced_settings: dict = None
) -> str:
    """
    Build comprehensive prompt for LLM generation with advanced settings support.
    
    This function creates a detailed, structured prompt that incorporates brand guidelines,
    post history, platform requirements, and advanced user preferences.
    
    Args:
        source_text (str): Combined text from source files containing content to share
        brand_guide_text (str): Brand guide content for voice/tone consistency
        post_history (list): List of previous posts for style learning
        platform (str): Target social media platform ('X', 'LinkedIn', etc.)
        count (int): Number of posts to generate
        advanced_settings (dict, optional): Advanced generation preferences including:
            - creativity_level: 'Conservative', 'Balanced', 'Creative', 'Innovative'
            - include_hashtags: bool
            - include_emojis: bool
            - content_tone: 'Professional', 'Casual', 'Friendly', etc.
            - call_to_action: bool
            - avoid_controversy: bool
        
    Returns:
        str: Formatted prompt for LLM with all requirements and guidelines
        
    Example:
        >>> prompt = build_master_prompt(
        ...     source_text="Product launch announcement...",
        ...     brand_guide_text="Professional tone, innovative...",
        ...     post_history=["Previous post 1", "Previous post 2"],
        ...     platform="LinkedIn",
        ...     count=3,
        ...     advanced_settings={'creativity_level': 'Creative', 'include_hashtags': True}
        ... )
    """
    # Platform-specific formatting rules
    platform_rules = {
        "X": "- Keep posts under 280 characters\n- Use 1-2 relevant hashtags\n- Write concisely and engagingly\n- Consider using emojis sparingly",
        "LinkedIn": "- Professional tone and language\n- Can be longer form (up to 3000 characters)\n- Include industry insights\n- Use professional hashtags\n- Consider tagging relevant companies/people",
        "Facebook": "- Conversational and engaging tone\n- Can include questions to drive engagement\n- Use emojis to add personality\n- Keep paragraphs short for readability",
        "Instagram": "- Visual-first mindset (assume images will accompany)\n- Use relevant hashtags (5-10 recommended)\n- Engaging and lifestyle-focused tone\n- Include call-to-action for engagement"
    }
    
    # Build comprehensive prompt
    prompt = f"""You are an expert social media content creator specializing in {platform} posts. Your task is to create {count} high-quality, engaging social media posts based on the provided information.

## ROLE DEFINITION
You are a professional social media content creator with expertise in:
- Crafting engaging, platform-specific content
- Understanding audience psychology and engagement drivers
- Following brand voice and guidelines consistently
- Creating posts that drive meaningful interaction

## BRAND VOICE AND GUIDELINES
{brand_guide_text if brand_guide_text.strip() else "No specific brand guidelines provided. Use a professional yet approachable tone."}

## SOURCE MATERIAL TO POST ABOUT
Use this information as the foundation for your posts:
{source_text if source_text.strip() else "No specific source material provided. Create general engaging content."}

## POST HISTORY FOR STYLE REFERENCE
Here are examples of previous posts to understand the preferred style and tone:
"""
    
    if post_history:
        for i, post in enumerate(post_history, 1):
            prompt += f"\nExample {i}: {post}"
    else:
        prompt += "\nNo previous post examples provided. Create content that aligns with the brand guidelines above."
    
    # Parse advanced settings with defaults
    if advanced_settings is None:
        advanced_settings = {}
    
    creativity_level = advanced_settings.get('creativity_level', 'Balanced')
    include_hashtags = advanced_settings.get('include_hashtags', True)
    include_emojis = advanced_settings.get('include_emojis', True)
    content_tone = advanced_settings.get('content_tone', 'Professional')
    call_to_action = advanced_settings.get('call_to_action', True)
    avoid_controversy = advanced_settings.get('avoid_controversy', True)
    
    prompt += f"""

## PLATFORM-SPECIFIC REQUIREMENTS FOR {platform.upper()}
{platform_rules.get(platform, "Follow general social media best practices.")}

## ADVANCED GENERATION PREFERENCES
- Creativity Level: {creativity_level} (adjust innovation vs. safety accordingly)
- Content Tone: {content_tone}
- Include Hashtags: {"Yes" if include_hashtags else "No"}
- Include Emojis: {"Yes, use appropriately" if include_emojis else "No emojis"}
- Call-to-Action: {"Include where relevant" if call_to_action else "Avoid direct CTAs"}
- Content Safety: {"Avoid controversial topics" if avoid_controversy else "Normal content guidelines"}

## GENERATION INSTRUCTIONS
Please generate exactly {count} {'post' if count == 1 else 'posts'} that:
1. Incorporate the source material naturally and engagingly
2. Follow the brand voice and guidelines provided
3. Match the style and tone of previous posts
4. Adhere to {platform} platform requirements and character limits
5. Are unique and distinct from each other
6. Follow the advanced preferences specified above
7. {"Include relevant hashtags" if include_hashtags else "Avoid hashtags"}
8. {"Use emojis appropriately" if include_emojis else "Do not use emojis"}
9. {"Include calls-to-action where relevant" if call_to_action else "Focus on informational content"}

## OUTPUT FORMAT
Format your response exactly as follows, separating each post with "---":

POST 1: [Your first post content here]
---
POST 2: [Your second post content here]
---
POST 3: [Your third post content here]

Continue this pattern for all {count} posts. Each post should be complete and ready to publish on {platform}."""

    return prompt


def call_llm(provider: str, api_key: str, prompt: str) -> str:
    """
    Factory function to call appropriate LLM provider.
    
    Args:
        provider: LLM provider name
        api_key: API key for authentication
        prompt: Formatted prompt string
        
    Returns:
        str: Raw response from LLM
    """
    # Input validation
    if not provider:
        raise ValueError("Provider cannot be empty")
    if not api_key:
        raise ValueError("API key cannot be empty")
    if not prompt:
        raise ValueError("Prompt cannot be empty")
    
    # Route to appropriate provider
    if provider == "Google Gemini":
        return _call_gemini(api_key, prompt)
    elif provider == "OpenAI":
        return _call_openai(api_key, prompt)
    elif provider == "Anthropic":
        return _call_anthropic(api_key, prompt)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def parse_llm_response(response: str) -> list[str]:
    """
    Parse LLM response into individual posts.
    
    Args:
        response: Raw LLM response
        
    Returns:
        list[str]: List of individual post strings
    """
    import re
    
    if not response:
        return []
    
    # Try different parsing strategies in order of preference
    
    # Strategy 1: Parse "POST N:" format with "---" separators (most specific)
    if "---" in response and "POST" in response.upper():
        post_pattern = r'POST\s+\d+:\s*(.*?)(?=---|\Z)'
        matches = re.findall(post_pattern, response, re.DOTALL | re.IGNORECASE)
        if matches:
            posts = [_clean_post_content(match) for match in matches]
            return [post for post in posts if post.strip()]
    
    # Strategy 2: Parse "POST N:" without separators (including with newlines)
    post_lines_pattern = r'POST\s+\d+:\s*(.*?)(?=\s*POST\s+\d+:|\Z)'
    matches = re.findall(post_lines_pattern, response, re.DOTALL | re.IGNORECASE)
    if len(matches) > 1:  # Only use this if we found multiple posts
        posts = [_clean_post_content(match) for match in matches]
        return [post for post in posts if post.strip()]
    
    # Strategy 3: Parse numbered format "1. 2. 3." 
    numbered_pattern = r'^\d+\.\s*(.*?)(?=^\d+\.|\Z)'
    matches = re.findall(numbered_pattern, response, re.MULTILINE | re.DOTALL)
    if matches:
        posts = [_clean_post_content(match) for match in matches]
        return [post for post in posts if post.strip()]
    
    # Strategy 4: Split by "---" separators
    if "---" in response:
        parts = response.split("---")
        posts = [_clean_post_content(part) for part in parts]
        return [post for post in posts if post.strip()]
    
    # Strategy 5: Split by double newlines (paragraph breaks)
    if '\n\n' in response:
        parts = response.split('\n\n')
        posts = [_clean_post_content(part) for part in parts]
        # Filter out very short parts (likely not posts)
        posts = [post for post in posts if post.strip() and len(post.strip()) > 20]
        if posts:
            return posts
    
    # Strategy 6: Return as single post if no pattern matches
    cleaned = _clean_post_content(response)
    return [cleaned] if cleaned.strip() else []


def _clean_post_content(content: str) -> str:
    """
    Clean and format post content.
    
    Args:
        content: Raw post content
        
    Returns:
        str: Cleaned post content
    """
    import re
    
    if not content:
        return ""
    
    # Remove common prefixes
    content = re.sub(r'^(POST\s+\d+:\s*|Here\s+(are|is)\s+(your|the)\s+posts?:?\s*)', '', content, flags=re.IGNORECASE)
    content = re.sub(r'^\d+\.\s*', '', content)
    
    # Remove markdown formatting artifacts
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Remove bold
    content = re.sub(r'\*(.*?)\*', r'\1', content)      # Remove italic
    
    # Clean up whitespace
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip empty lines and common separator patterns
        if line and line not in ['---', '***', '===', '...']:
            cleaned_lines.append(line)
    
    # Join lines back together
    result = '\n'.join(cleaned_lines)
    
    # Replace multiple newlines with single newlines
    result = re.sub(r'\n\s*\n', '\n', result)
    
    # Final trim
    return result.strip()


try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None


def _call_gemini(api_key: str, prompt: str) -> str:
    """Call Google Gemini API"""
    try:
        if genai is None:
            raise ImportError("google-generativeai not available")
        
        # Configure the API key
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Return the text response
        return response.text
    except Exception as e:
        # Handle various API errors
        error_msg = str(e).lower()
        if "api key" in error_msg or "authentication" in error_msg:
            raise Exception("Invalid API key or authentication failed")
        elif "quota" in error_msg or "limit" in error_msg:
            raise Exception("API quota exceeded or rate limit reached")
        elif "network" in error_msg or "connection" in error_msg:
            raise Exception("Network connection failed")
        else:
            raise Exception(f"Gemini API error: {str(e)}")


def _call_openai(api_key: str, prompt: str) -> str:
    """Call OpenAI API"""
    try:
        if OpenAI is None:
            raise ImportError("openai not available")
        
        # Initialize the client
        client = OpenAI(api_key=api_key)
        
        # Create chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Return the response content
        return response.choices[0].message.content
    except Exception as e:
        # Handle various API errors
        error_msg = str(e).lower()
        if "api key" in error_msg or "authentication" in error_msg or "invalid" in error_msg:
            raise Exception("Invalid API key or authentication failed")
        elif "quota" in error_msg or "limit" in error_msg or "rate" in error_msg:
            raise Exception("API quota exceeded or rate limit reached")
        elif "network" in error_msg or "connection" in error_msg:
            raise Exception("Network connection failed")
        else:
            raise Exception(f"OpenAI API error: {str(e)}")


def _call_anthropic(api_key: str, prompt: str) -> str:
    """Call Anthropic API"""
    try:
        if anthropic is None:
            raise ImportError("anthropic not available")
        
        # Initialize the client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Create message
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Return the response content
        return response.content[0].text
    except Exception as e:
        # Handle various API errors
        error_msg = str(e).lower()
        if "api key" in error_msg or "authentication" in error_msg or "invalid" in error_msg:
            raise Exception("Invalid API key or authentication failed")
        elif "quota" in error_msg or "limit" in error_msg or "rate" in error_msg:
            raise Exception("API quota exceeded or rate limit reached")
        elif "network" in error_msg or "connection" in error_msg:
            raise Exception("Network connection failed")
        else:
            raise Exception(f"Anthropic API error: {str(e)}")