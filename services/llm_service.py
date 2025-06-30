def build_master_prompt(
    source_text: str, 
    brand_guide_text: str, 
    post_history: list, 
    platform: str, 
    count: int,
    advanced_settings: dict = None,
    custom_instructions: str = None
) -> str:
    """
    Build comprehensive prompt for LLM generation with advanced settings support.
    
    This function creates a detailed, structured prompt that incorporates brand guidelines,
    post history, platform requirements, advanced user preferences, and custom instructions.
    
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
            - custom_instructions: str (Phase 8 feature)
        custom_instructions (str, optional): Custom user instructions for post generation
        
    Returns:
        str: Formatted prompt for LLM with all requirements and guidelines
        
    Example:
        >>> prompt = build_master_prompt(
        ...     source_text="Product launch announcement...",
        ...     brand_guide_text="Professional tone, innovative...",
        ...     post_history=["Previous post 1", "Previous post 2"],
        ...     platform="LinkedIn",
        ...     count=3,
        ...     advanced_settings={'creativity_level': 'Creative', 'include_hashtags': True},
        ...     custom_instructions="Include industry statistics and end with questions"
        ... )
    """
    # Phase 8.2: Custom Instructions Processing
    def sanitize_custom_instructions(instructions):
        """Sanitize custom instructions for safe inclusion in prompts."""
        if not instructions or not instructions.strip():
            return ""
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            '<script>', '</script>', 'javascript:', 'data:', 'vbscript:',
            'alert(', 'system:', 'ignore previous', 'ignore all', 'override',
            '<iframe>', '</iframe>', '<object>', '</object>'
        ]
        
        sanitized = instructions
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, '')
        
        # Clean up extra whitespace
        sanitized = ' '.join(sanitized.split())
        return sanitized.strip()
    
    def validate_instruction_conflicts(instructions, platform, advanced_settings):
        """Check for potential conflicts between custom instructions and platform/settings."""
        if not instructions:
            return []
        
        conflicts = []
        lower_instructions = instructions.lower()
        
        # Check for platform conflicts
        if platform == "X" and ("long" in lower_instructions or "detailed" in lower_instructions):
            conflicts.append(f"Custom instruction suggests long content, but {platform} has 280 character limit")
        
        # Check for setting conflicts
        if advanced_settings:
            if not advanced_settings.get('include_hashtags', True) and 'hashtag' in lower_instructions:
                conflicts.append("Custom instruction requests hashtags, but hashtag setting is disabled")
            
            if not advanced_settings.get('include_emojis', True) and 'emoji' in lower_instructions:
                conflicts.append("Custom instruction requests emojis, but emoji setting is disabled")
        
        return conflicts
    
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
    
    # Phase 8.2: Process custom instructions
    # Get custom instructions from parameter or advanced_settings
    final_custom_instructions = custom_instructions or advanced_settings.get('custom_instructions', '')
    sanitized_instructions = sanitize_custom_instructions(final_custom_instructions)
    
    # Check for conflicts and log warnings (in production, these could be logged)
    conflicts = validate_instruction_conflicts(sanitized_instructions, platform, advanced_settings)
    # Note: In a production system, conflicts would be logged or handled appropriately
    
    prompt += f"""

## PLATFORM-SPECIFIC REQUIREMENTS FOR {platform.upper()}
{platform_rules.get(platform, "Follow general social media best practices.")}

## ADVANCED GENERATION PREFERENCES
- Creativity Level: {creativity_level} (adjust innovation vs. safety accordingly)
- Content Tone: {content_tone}
- Include Hashtags: {"Yes" if include_hashtags else "No"}
- Include Emojis: {"Yes, use appropriately" if include_emojis else "No emojis"}
- Call-to-Action: {"Include where relevant" if call_to_action else "Avoid direct CTAs"}
- Content Safety: {"Avoid controversial topics" if avoid_controversy else "Normal content guidelines"}"""

    # Phase 8.2: Add custom instructions section if provided
    if sanitized_instructions:
        prompt += f"""

## CUSTOM INSTRUCTIONS (High Priority)
The user has provided specific instructions that should be prioritized in the generation:

{sanitized_instructions}

IMPORTANT: These custom instructions should be followed closely while still adhering to the platform requirements and brand guidelines above. If there are any conflicts between custom instructions and platform limitations (like character limits), prioritize platform requirements but try to adapt the custom instructions accordingly."""
        
        # Add conflict warnings if any
        if conflicts:
            prompt += f"""

NOTE: The following potential conflicts were detected with your custom instructions:
{chr(10).join(f"- {conflict}" for conflict in conflicts)}
Please adapt the custom instructions to work within these constraints."""

    prompt += f"""

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
9. {"Include calls-to-action where relevant" if call_to_action else "Focus on informational content"}"""
    
    # Add custom instructions to generation requirements if provided
    if sanitized_instructions:
        prompt += f"""
10. **PRIORITY: Follow the custom instructions provided above while maintaining all other requirements**"""
    
    prompt += f"""

## OUTPUT FORMAT
Format your response exactly as follows, separating each post with "---":

POST 1: [Your first post content here]
---
POST 2: [Your second post content here]
---
POST 3: [Your third post content here]

Continue this pattern for all {count} posts. Each post should be complete and ready to publish on {platform}."""

    return prompt


def call_llm(provider: str, api_key: str, prompt: str, model: str = None, **kwargs) -> str:
    """
    Factory function to call appropriate LLM provider with dynamic model selection.
    
    Phase 9.4: Enhanced to support dynamic model selection and parameters.
    
    Args:
        provider: LLM provider name
        api_key: API key for authentication
        prompt: Formatted prompt string
        model: Optional model name (Phase 9 feature)
        **kwargs: Additional model parameters like temperature, max_tokens, etc.
        
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
    
    # Get internal provider name
    provider_mapping = {
        "Google Gemini": "google",
        "OpenAI": "openai", 
        "Anthropic": "anthropic"
    }
    
    internal_provider = provider_mapping.get(provider, provider.lower())
    
    # Route to appropriate provider with model parameter
    if provider == "Google Gemini" or internal_provider == "google":
        return _call_gemini(api_key, prompt, model=model, **kwargs)
    elif provider == "OpenAI" or internal_provider == "openai":
        return _call_openai(api_key, prompt, model=model, **kwargs)
    elif provider == "Anthropic" or internal_provider == "anthropic":
        return _call_anthropic(api_key, prompt, model=model, **kwargs)
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
    Clean and format post content with Unicode sanitization.
    
    Phase 10.2: Enhanced with Unicode text sanitization to fix character encoding issues
    like "窶覇" becoming "—" in all generated posts from any LLM provider.
    
    Args:
        content: Raw post content
        
    Returns:
        str: Cleaned and Unicode-sanitized post content
    """
    import re
    import logging
    
    # Configure logger for this module
    logger = logging.getLogger(__name__)
    
    if not content:
        return ""
    
    try:
        # Phase 10.2: Unicode sanitization FIRST to fix encoding issues
        # Import here to avoid circular imports and lazy loading
        from utils.text_sanitizer import get_text_sanitizer
        
        sanitizer = get_text_sanitizer()
        content = sanitizer.sanitize_text(content)
        logger.debug(f"Applied Unicode sanitization to content: {len(content)} characters")
        
    except Exception as e:
        # Log the error but continue with original content to maintain backward compatibility
        logger.warning(f"Unicode sanitization failed, continuing with original content: {str(e)}")
        pass
    
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


def _call_gemini(api_key: str, prompt: str, model: str = None, **kwargs) -> str:
    """
    Call Google Gemini API with dynamic model selection.
    
    Phase 9.4: Enhanced to support dynamic model selection and parameters.
    
    Args:
        api_key: Google API key
        prompt: Formatted prompt string
        model: Optional model name (defaults to gemini-pro)
        **kwargs: Additional parameters like temperature, max_tokens, etc.
    """
    try:
        if genai is None:
            raise ImportError("google-generativeai not available")
        
        # Configure the API key
        genai.configure(api_key=api_key)
        
        # Determine model to use
        model_name = model if model else 'gemini-pro'
        
        # Handle model name variations (remove 'models/' prefix if present)
        if model_name.startswith('models/'):
            model_name = model_name[7:]
        
        # Validate and adjust parameters for Gemini
        generation_config = {}
        
        # Map common parameters to Gemini format
        if 'temperature' in kwargs:
            generation_config['temperature'] = max(0.0, min(2.0, float(kwargs['temperature'])))
        
        if 'max_tokens' in kwargs:
            # Gemini uses maxOutputTokens
            generation_config['max_output_tokens'] = min(8192, max(1, int(kwargs['max_tokens'])))
        elif 'maxOutputTokens' in kwargs:
            generation_config['max_output_tokens'] = min(8192, max(1, int(kwargs['maxOutputTokens'])))
        
        if 'top_p' in kwargs:
            generation_config['top_p'] = max(0.0, min(1.0, float(kwargs['top_p'])))
        elif 'topP' in kwargs:
            generation_config['top_p'] = max(0.0, min(1.0, float(kwargs['topP'])))
        
        if 'top_k' in kwargs:
            generation_config['top_k'] = max(1, int(kwargs['top_k']))
        elif 'topK' in kwargs:
            generation_config['top_k'] = max(1, int(kwargs['topK']))
        
        # Initialize the model with generation config
        model_instance = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config if generation_config else None
        )
        
        # Generate content
        response = model_instance.generate_content(prompt)
        
        # Phase 10.2: Apply Unicode sanitization to provider response
        try:
            from utils.text_sanitizer import get_text_sanitizer
            sanitizer = get_text_sanitizer()
            clean_response = sanitizer.sanitize_text(response.text)
            return clean_response
        except Exception as e:
            # Fallback to original response if sanitization fails
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Gemini response sanitization failed: {str(e)}")
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
        elif "model" in error_msg and "not found" in error_msg:
            raise Exception(f"Model '{model_name}' not found or not accessible")
        else:
            raise Exception(f"Gemini API error: {str(e)}")


def _call_openai(api_key: str, prompt: str, model: str = None, **kwargs) -> str:
    """
    Call OpenAI API with dynamic model selection.
    
    Phase 9.4: Enhanced to support dynamic model selection and parameters.
    
    Args:
        api_key: OpenAI API key
        prompt: Formatted prompt string
        model: Optional model name (defaults to gpt-3.5-turbo)
        **kwargs: Additional parameters like temperature, max_tokens, etc.
    """
    try:
        if OpenAI is None:
            raise ImportError("openai not available")
        
        # Initialize the client
        client = OpenAI(api_key=api_key)
        
        # Determine model to use
        model_name = model if model else "gpt-3.5-turbo"
        
        # Prepare chat completion parameters
        completion_params = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Add optional parameters with validation
        if 'temperature' in kwargs:
            completion_params['temperature'] = max(0.0, min(2.0, float(kwargs['temperature'])))
        else:
            completion_params['temperature'] = 0.7  # Default
        
        if 'max_tokens' in kwargs:
            completion_params['max_tokens'] = min(4096, max(1, int(kwargs['max_tokens'])))
        else:
            completion_params['max_tokens'] = 2000  # Default
        
        if 'top_p' in kwargs:
            completion_params['top_p'] = max(0.0, min(1.0, float(kwargs['top_p'])))
        
        if 'frequency_penalty' in kwargs:
            completion_params['frequency_penalty'] = max(-2.0, min(2.0, float(kwargs['frequency_penalty'])))
        
        if 'presence_penalty' in kwargs:
            completion_params['presence_penalty'] = max(-2.0, min(2.0, float(kwargs['presence_penalty'])))
        
        if 'stop' in kwargs and kwargs['stop']:
            completion_params['stop'] = kwargs['stop']
        
        # Handle response format for JSON mode
        if 'response_format' in kwargs:
            completion_params['response_format'] = kwargs['response_format']
        
        # Create chat completion
        response = client.chat.completions.create(**completion_params)
        
        # Phase 10.2: Apply Unicode sanitization to provider response
        try:
            from utils.text_sanitizer import get_text_sanitizer
            sanitizer = get_text_sanitizer()
            clean_response = sanitizer.sanitize_text(response.choices[0].message.content)
            return clean_response
        except Exception as e:
            # Fallback to original response if sanitization fails
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"OpenAI response sanitization failed: {str(e)}")
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
        elif "model" in error_msg and ("not found" in error_msg or "does not exist" in error_msg):
            raise Exception(f"Model '{model_name}' not found or not accessible")
        else:
            raise Exception(f"OpenAI API error: {str(e)}")


def _call_anthropic(api_key: str, prompt: str, model: str = None, **kwargs) -> str:
    """
    Call Anthropic API with dynamic model selection.
    
    Phase 9.4: Enhanced to support dynamic model selection and parameters.
    
    Args:
        api_key: Anthropic API key
        prompt: Formatted prompt string
        model: Optional model name (defaults to claude-3-sonnet-20240229)
        **kwargs: Additional parameters like temperature, max_tokens, etc.
    """
    try:
        if anthropic is None:
            raise ImportError("anthropic not available")
        
        # Initialize the client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Determine model to use
        model_name = model if model else "claude-3-sonnet-20240229"
        
        # Prepare message parameters
        message_params = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Add optional parameters with validation
        if 'temperature' in kwargs:
            message_params['temperature'] = max(0.0, min(1.0, float(kwargs['temperature'])))
        else:
            message_params['temperature'] = 0.7  # Default
        
        if 'max_tokens' in kwargs:
            message_params['max_tokens'] = min(8192, max(1, int(kwargs['max_tokens'])))
        else:
            message_params['max_tokens'] = 2000  # Default
        
        if 'top_p' in kwargs:
            message_params['top_p'] = max(0.0, min(1.0, float(kwargs['top_p'])))
        
        # Handle stop sequences
        if 'stop' in kwargs and kwargs['stop']:
            message_params['stop_sequences'] = kwargs['stop'] if isinstance(kwargs['stop'], list) else [kwargs['stop']]
        elif 'stop_sequences' in kwargs and kwargs['stop_sequences']:
            message_params['stop_sequences'] = kwargs['stop_sequences']
        
        # Create message
        response = client.messages.create(**message_params)
        
        # Phase 10.2: Apply Unicode sanitization to provider response
        try:
            from utils.text_sanitizer import get_text_sanitizer
            sanitizer = get_text_sanitizer()
            clean_response = sanitizer.sanitize_text(response.content[0].text)
            return clean_response
        except Exception as e:
            # Fallback to original response if sanitization fails
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Anthropic response sanitization failed: {str(e)}")
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
        elif "model" in error_msg and ("not found" in error_msg or "does not exist" in error_msg):
            raise Exception(f"Model '{model_name}' not found or not accessible")
        else:
            raise Exception(f"Anthropic API error: {str(e)}")