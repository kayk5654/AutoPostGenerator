import streamlit as st
import pandas as pd
import re
from datetime import datetime
from config import LLM_PROVIDERS, TARGET_PLATFORMS, SUPPORTED_TEXT_FORMATS, SUPPORTED_HISTORY_FORMATS
from services.post_service import generate_posts_workflow
from utils.data_exporter import create_csv_export, validate_export_data, get_export_statistics
from utils.logging_config import setup_logging, get_logger

# Initialize logging for the application
setup_logging(
    log_level="INFO",
    log_file="logs/app.log",
    json_format=False,
    console_output=False  # Disable console output for Streamlit
)

# Get logger for this module
logger = get_logger(__name__)

st.set_page_config(
    page_title="Auto Post Generator",
    page_icon="📝",
    layout="wide"
)

st.title("Auto Post Generator")

# Enhanced session state initialization
def initialize_session_state():
    """Initialize all required session state variables."""
    if 'generated_posts' not in st.session_state:
        st.session_state.generated_posts = []
    if 'editing_posts' not in st.session_state:
        st.session_state.editing_posts = []
    if 'generation_timestamp' not in st.session_state:
        st.session_state.generation_timestamp = None
    if 'target_platform' not in st.session_state:
        st.session_state.target_platform = None
    if 'generation_in_progress' not in st.session_state:
        st.session_state.generation_in_progress = False
    if 'last_generation_settings' not in st.session_state:
        st.session_state.last_generation_settings = {}
    # Phase 8.1: Custom instructions session state
    if 'custom_instructions' not in st.session_state:
        st.session_state.custom_instructions = ''

def reset_generation_state():
    """Reset state for new post generation."""
    st.session_state.generated_posts = []
    st.session_state.editing_posts = []
    st.session_state.generation_timestamp = None
    st.session_state.target_platform = None
    st.session_state.generation_in_progress = False
    st.session_state.last_generation_settings = {}

def get_platform_character_limit(platform):
    """Get character limit for specific platform."""
    limits = {
        "X": 280,
        "LinkedIn": 3000,
        "Facebook": 63206,
        "Instagram": 2200
    }
    return limits.get(platform, 1000)


# Phase 8.1: Custom Instructions Helper Functions

def validate_custom_instructions(instructions):
    """
    Validate custom instructions input.
    
    Args:
        instructions (str): Custom instructions text
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not instructions:
        return True, ""  # Empty is valid (will be ignored)
    
    # Check for whitespace-only content
    if instructions.isspace():
        return False, "⚠️ Instructions cannot contain only whitespace"
    
    # Check character limit
    MAX_INSTRUCTION_LENGTH = 500
    if len(instructions) > MAX_INSTRUCTION_LENGTH:
        return False, f"⚠️ Instructions must be {MAX_INSTRUCTION_LENGTH} characters or less (currently {len(instructions)})"
    
    # Basic security checks - remove potentially malicious content
    dangerous_patterns = ['<script>', '</script>', 'javascript:', 'data:', 'vbscript:']
    lower_instructions = instructions.lower()
    for pattern in dangerous_patterns:
        if pattern in lower_instructions:
            return False, "⚠️ Instructions contain potentially unsafe content"
    
    return True, ""


def sanitize_custom_instructions(instructions):
    """
    Sanitize custom instructions to remove potentially harmful content.
    
    Args:
        instructions (str): Raw custom instructions
        
    Returns:
        str: Sanitized instructions
    """
    if not instructions:
        return ""
    
    # Remove dangerous patterns
    dangerous_patterns = [
        '<script>', '</script>', 'javascript:', 'data:', 'vbscript:',
        '<iframe>', '</iframe>', '<object>', '</object>', '<embed>', '</embed>'
    ]
    
    sanitized = instructions
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern, '')
    
    # Clean up extra whitespace
    sanitized = ' '.join(sanitized.split())
    
    return sanitized.strip()


def reset_custom_instructions():
    """Reset custom instructions to empty state."""
    st.session_state.custom_instructions = ''


# Phase 6.1: User Experience Enhancement Functions

def validate_api_key_format(api_key, provider):
    """
    Validate API key format for specific provider.
    
    Args:
        api_key (str): The API key to validate
        provider (str): The LLM provider name
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not api_key or not api_key.strip():
        return False, "🔑 API key is required"
    
    api_key = api_key.strip()
    
    # Provider-specific validation patterns
    validation_patterns = {
        "OpenAI": {"prefix": "sk-", "min_length": 20},
        "Google Gemini": {"prefix": "AI", "min_length": 10},
        "Anthropic": {"prefix": "sk-ant", "min_length": 15}
    }
    
    if provider in validation_patterns:
        pattern = validation_patterns[provider]
        
        if not api_key.startswith(pattern["prefix"]):
            return False, f"🔑 {provider} API key should start with '{pattern['prefix']}'"
        
        if len(api_key) < pattern["min_length"]:
            return False, f"🔑 {provider} API key appears to be too short"
    
    # Check for obvious test/fake keys
    fake_patterns = ['test', 'fake', 'demo', 'example', '1234', 'abcd']
    if any(pattern in api_key.lower() for pattern in fake_patterns):
        return False, "🔑 API key appears to be a test/fake key"
    
    return True, "Valid API key format"


def validate_file_uploads(source_files, brand_guide, post_history):
    """
    Validate uploaded files for format and content.
    
    Args:
        source_files: List of uploaded source files
        brand_guide: Uploaded brand guide file
        post_history: Uploaded post history file
        
    Returns:
        tuple[bool, list]: (is_valid, list_of_issues)
    """
    issues = []
    
    # Validate source files
    if not source_files:
        issues.append("📁 Please upload at least one source file")
    else:
        for file in source_files:
            if hasattr(file, 'size') and file.size > 10 * 1024 * 1024:  # 10MB
                issues.append(f"📁 File '{file.name}' is too large (max 10MB)")
            
            file_ext = file.name.lower().split('.')[-1] if '.' in file.name else ''
            if f".{file_ext}" not in SUPPORTED_TEXT_FORMATS:
                issues.append(f"📁 File '{file.name}' has unsupported format")
    
    # Validate brand guide (optional but validate if provided)
    if brand_guide:
        if hasattr(brand_guide, 'size') and brand_guide.size > 10 * 1024 * 1024:
            issues.append(f"📁 Brand guide '{brand_guide.name}' is too large (max 10MB)")
        
        file_ext = brand_guide.name.lower().split('.')[-1] if '.' in brand_guide.name else ''
        if f".{file_ext}" not in SUPPORTED_TEXT_FORMATS:
            issues.append(f"📁 Brand guide '{brand_guide.name}' has unsupported format")
    
    # Validate post history (optional but validate if provided)
    if post_history:
        if hasattr(post_history, 'size') and post_history.size > 10 * 1024 * 1024:
            issues.append(f"📁 Post history '{post_history.name}' is too large (max 10MB)")
        
        if not post_history.name.lower().endswith('.xlsx'):
            issues.append(f"📁 Post history must be an Excel file (.xlsx)")
    
    return len(issues) == 0, issues


def get_current_workflow_step(api_key, provider, source_files, platform, posts_generated):
    """
    Determine current workflow step for progress indication.
    
    Args:
        api_key (str): User's API key
        provider (str): Selected LLM provider
        source_files: Uploaded source files
        platform (str): Selected target platform
        posts_generated (bool): Whether posts have been generated
        
    Returns:
        tuple[int, str]: (current_step, next_action)
    """
    if not api_key or not provider:
        return 1, "👆 Select your LLM provider and enter your API key"
    
    if not source_files:
        return 2, "📁 Upload your source files to continue"
    
    if not platform:
        return 3, "🎯 Choose your target platform and post count"
    
    if not posts_generated:
        return 4, "🚀 Click 'Generate Posts' to create your content"
    
    return 5, "✏️ Review and edit your posts, then export when ready"


def show_workflow_progress():
    """Display workflow progress indicator."""
    steps = [
        "🤖 Configure LLM",
        "📁 Upload Files", 
        "⚙️ Set Parameters",
        "🚀 Generate Posts",
        "✏️ Edit & Export"
    ]
    
    # Determine current step
    current_step, next_action = get_current_workflow_step(
        st.session_state.get('current_api_key', ''),
        st.session_state.get('current_provider', ''),
        st.session_state.get('current_source_files', []),
        st.session_state.get('current_platform', ''),
        len(st.session_state.generated_posts) > 0
    )
    
    # Display progress
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps), 1):
        with col:
            if i < current_step:
                st.markdown(f"✅ **{step}**")
            elif i == current_step:
                st.markdown(f"🔄 **{step}**")
            else:
                st.markdown(f"⏳ {step}")
    
    # Show next action
    st.info(f"**Next:** {next_action}")


def show_help_tips():
    """Display helpful tips and guidance."""
    with st.expander("💡 Tips for Better Results", expanded=False):
        st.markdown("""
        **📝 Source Files:**
        - Upload clear, well-structured content
        - Include key information you want to highlight
        - Multiple files will be combined for richer content
        
        **🎨 Brand Guide:**
        - Include your brand voice and tone guidelines
        - Specify any messaging do's and don'ts
        - Add examples of your preferred style
        
        **📊 Post History:**
        - Upload Excel file with columns: 'Post Text', 'Platform', 'Date'
        - Include your best-performing posts
        - Helps AI understand your successful patterns
        
        **🎯 Platform Optimization:**
        - **X (Twitter)**: Keep posts under 280 characters, use hashtags
        - **LinkedIn**: Professional tone, longer content (up to 3000 chars)
        - **Facebook**: Engaging, community-focused content
        - **Instagram**: Visual storytelling, use emojis and hashtags
        """)


def show_advanced_options():
    """Display advanced configuration options."""
    with st.expander("🔧 Advanced Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Generation Settings:**")
            creativity_level = st.select_slider(
                "Creativity Level",
                options=["Conservative", "Balanced", "Creative", "Innovative"],
                value="Balanced",
                help="Controls how creative vs. safe the generated content will be"
            )
            
            include_hashtags = st.checkbox(
                "Include Hashtags",
                value=True,
                help="Automatically include relevant hashtags in posts"
            )
            
            include_emojis = st.checkbox(
                "Include Emojis",
                value=True,
                help="Add appropriate emojis to enhance engagement"
            )
        
        with col2:
            st.markdown("**Content Preferences:**")
            content_tone = st.selectbox(
                "Preferred Tone",
                ["Professional", "Casual", "Friendly", "Authoritative", "Inspirational"],
                help="Overall tone for the generated content"
            )
            
            call_to_action = st.checkbox(
                "Include Call-to-Action",
                value=True,
                help="Add calls-to-action to encourage engagement"
            )
            
            avoid_controversy = st.checkbox(
                "Avoid Controversial Topics",
                value=True,
                help="Ensure content stays away from sensitive subjects"
            )
        
        # Phase 8.1: Custom Instructions Section
        st.markdown("---")
        st.markdown("**🎯 Custom Instructions** *(Phase 8 Feature)*")
        
        # Custom instructions input with real-time validation
        placeholder_text = """Add specific instructions to customize the generated posts...

Examples:
• Make the posts more engaging with questions and statistics
• Include industry-specific terminology and data points
• Use a professional but friendly tone throughout
• Add call-to-action at the end of each post
• Focus on actionable insights and practical tips
• Include relevant hashtags for maximum reach"""
        
        # Create columns for instructions and controls
        inst_col1, inst_col2 = st.columns([3, 1])
        
        with inst_col1:
            custom_instructions = st.text_area(
                "Additional Instructions",
                value=st.session_state.custom_instructions,
                placeholder=placeholder_text,
                height=120,
                key="custom_instructions_input",
                help="Provide specific instructions to customize how posts are generated. These will be applied in addition to the standard settings above.",
                max_chars=500
            )
            
            # Real-time validation
            if custom_instructions != st.session_state.custom_instructions:
                # Validate and sanitize the input
                is_valid, error_msg = validate_custom_instructions(custom_instructions)
                if is_valid:
                    sanitized_instructions = sanitize_custom_instructions(custom_instructions)
                    st.session_state.custom_instructions = sanitized_instructions
                    if custom_instructions != sanitized_instructions:
                        st.info("ℹ️ Instructions have been automatically cleaned for safety")
                else:
                    st.error(error_msg)
                    custom_instructions = st.session_state.custom_instructions
        
        with inst_col2:
            st.markdown("**Quick Actions:**")
            
            # Character counter
            char_count = len(st.session_state.custom_instructions)
            char_limit = 500
            if char_count > char_limit * 0.8:
                color = "red" if char_count > char_limit else "orange"
                st.markdown(f"<span style='color: {color}'>{char_count}/{char_limit}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"{char_count}/{char_limit}")
            
            # Clear button
            if st.button("🗑️ Clear", help="Clear all custom instructions"):
                reset_custom_instructions()
                st.rerun()
            
            # Example presets
            if st.button("💡 Examples", help="Show example instructions"):
                st.session_state.show_examples = not getattr(st.session_state, 'show_examples', False)
        
        # Show examples if requested
        if getattr(st.session_state, 'show_examples', False):
            with st.expander("📚 Example Instructions", expanded=True):
                st.markdown("""
                **Professional LinkedIn Posts:**
                ```
                Use industry statistics and data points. Include actionable insights. 
                End with a thought-provoking question to encourage engagement.
                ```
                
                **Engaging X/Twitter Posts:**
                ```
                Keep it concise and punchy. Use relevant hashtags. 
                Include emojis for visual appeal. Ask questions to spark conversation.
                ```
                
                **Educational Content:**
                ```
                Break down complex topics into easy-to-understand points. 
                Use bullet points and numbered lists. Include practical examples.
                ```
                
                **Brand Awareness:**
                ```
                Highlight unique value propositions. Use brand voice consistently. 
                Include subtle call-to-actions. Focus on customer benefits.
                ```
                """)
            
            if st.button("❌ Hide Examples"):
                st.session_state.show_examples = False
                st.rerun()
        
        return {
            'creativity_level': creativity_level,
            'include_hashtags': include_hashtags,
            'include_emojis': include_emojis,
            'content_tone': content_tone,
            'call_to_action': call_to_action,
            'avoid_controversy': avoid_controversy,
            'custom_instructions': st.session_state.custom_instructions
        }

# Initialize session state
initialize_session_state()

# Phase 6.1: Enhanced User Interface with Progress and Feedback

# Show workflow progress
show_workflow_progress()

# Show help tips
show_help_tips()

st.markdown("---")
st.subheader("Step 1: Configure LLM Provider")

col1, col2 = st.columns(2)
with col1:
    selected_provider = st.selectbox(
        "Select LLM Provider",
        LLM_PROVIDERS,
        help="Choose your preferred AI provider for content generation"
    )
    
    # Store in session state for progress tracking
    st.session_state.current_provider = selected_provider

with col2:
    api_key = st.text_input(
        "Enter Your API Key",
        type="password",
        help="Your API key will only be used for this session and not stored permanently"
    )
    
    # Store in session state for progress tracking
    st.session_state.current_api_key = api_key
    
    # Real-time API key validation
    if api_key:
        is_valid, message = validate_api_key_format(api_key, selected_provider)
        if is_valid:
            st.success("✅ API key format appears valid")
        else:
            st.error(message)

st.markdown("---")
st.subheader("Step 2: Provide Inputs")

st.markdown("**1. Upload Information Source Files** 📝")
st.caption("Upload content files that contain the information you want to share")
source_files = st.file_uploader(
    "Choose source files",
    type=['txt', 'docx', 'pdf', 'md'],
    accept_multiple_files=True,
    help=f"Supported formats: {', '.join(SUPPORTED_TEXT_FORMATS)}. Example: product announcements, blog posts, press releases"
)

# Store in session state for progress tracking
st.session_state.current_source_files = source_files

st.markdown("**2. Upload Brand Guide File** 🎨 *(Optional)*")
st.caption("Upload your brand guidelines to ensure consistent voice and tone")
brand_guide = st.file_uploader(
    "Choose brand guide file",
    type=['txt', 'docx', 'pdf', 'md'],
    help=f"Supported formats: {', '.join(SUPPORTED_TEXT_FORMATS)}. Example: brand voice guidelines, tone of voice document"
)

st.markdown("**3. Upload Previous Posts History** 📊 *(Optional)*")
st.caption("Upload examples of your successful posts to help AI learn your style")
post_history = st.file_uploader(
    "Choose post history file",
    type=['xlsx'],
    help=f"Required Excel format with columns: 'Post Text', 'Platform', 'Date'"
)

# Enhanced file validation with real-time feedback
if source_files or brand_guide or post_history:
    with st.spinner("🔍 Validating uploaded files..."):
        is_valid, issues = validate_file_uploads(source_files, brand_guide, post_history)
        
        if is_valid:
            file_count = len(source_files) if source_files else 0
            optional_count = (1 if brand_guide else 0) + (1 if post_history else 0)
            st.success(f"✅ Files validated successfully! ({file_count} source files + {optional_count} optional files)")
        else:
            for issue in issues:
                st.error(issue)

st.markdown("---")
st.subheader("Step 3: Define Generation Parameters")

col3, col4 = st.columns(2)
with col3:
    post_count = st.number_input(
        "4. Number of Posts to Generate",
        min_value=1,
        max_value=50,
        value=5,
        help="Number of social media posts to generate (1-50)"
    )
    
    # Post count validation
    if post_count < 1 or post_count > 50:
        st.error("📊 Post count must be between 1 and 50")
    elif post_count > 20:
        st.warning("⚠️ Generating many posts may take longer and consume more API credits")

with col4:
    target_platform = st.selectbox(
        "5. Select Target Platform",
        TARGET_PLATFORMS,
        help="Choose the social media platform for optimization"
    )
    
    # Store in session state for progress tracking
    st.session_state.current_platform = target_platform
    
    # Platform-specific guidance
    if target_platform:
        char_limit = get_platform_character_limit(target_platform)
        st.info(f"ℹ️ {target_platform} character limit: {char_limit} characters")

# Show advanced options
advanced_settings = show_advanced_options()

st.markdown("---")
st.subheader("Step 4: Generate")

# Pre-generation validation summary
validation_errors = []
validation_warnings = []

# Comprehensive validation
if not api_key or not api_key.strip():
    validation_errors.append("🔑 API key is required")
elif selected_provider:
    is_valid_key, key_message = validate_api_key_format(api_key, selected_provider)
    if not is_valid_key:
        validation_errors.append(key_message)

if not source_files:
    validation_errors.append("📁 At least one source file is required")
else:
    file_valid, file_issues = validate_file_uploads(source_files, brand_guide, post_history)
    if not file_valid:
        validation_errors.extend(file_issues)

if not selected_provider:
    validation_errors.append("🤖 LLM provider selection is required")

if not target_platform:
    validation_errors.append("🎯 Target platform selection is required")

if post_count < 1 or post_count > 50:
    validation_errors.append("📊 Post count must be between 1 and 50")

# Warnings
if post_count > 20:
    validation_warnings.append("⚠️ Large post count may take longer and use more API credits")

if not brand_guide:
    validation_warnings.append("💡 Consider uploading a brand guide for more consistent voice")

# Display validation status
if validation_errors:
    st.error("❌ **Please fix the following issues before generating:**")
    for error in validation_errors:
        st.error(error)

if validation_warnings:
    for warning in validation_warnings:
        st.warning(warning)

# Generation readiness check
generation_ready = len(validation_errors) == 0

if generation_ready:
    st.success("✅ **Ready to generate!** All requirements are met.")

# Generate Posts Button
button_label = "🚀 Generate Posts" if generation_ready else "⚠️ Fix Issues Above"
button_disabled = st.session_state.generation_in_progress or not generation_ready

if st.button(
    button_label,
    type="primary" if generation_ready else "secondary",
    use_container_width=True,
    disabled=button_disabled,
    help="Generate AI-powered social media posts based on your inputs"
):
    if generation_ready:
        # Set generation in progress
        st.session_state.generation_in_progress = True
        
        # Store generation settings including advanced options
        st.session_state.last_generation_settings = {
            'provider': selected_provider,
            'platform': target_platform,
            'count': post_count,
            'timestamp': datetime.now().isoformat(),
            'advanced_settings': advanced_settings
        }
        
        # Enhanced progress messages
        progress_messages = [
            "📄 Processing uploaded files...",
            "🧠 Initializing AI model...",
            "✍️ Generating creative content...",
            "🎯 Optimizing for platform...",
            "✨ Finalizing posts..."
        ]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            logger.info(f"Starting post generation workflow: {post_count} posts for {target_platform} using {selected_provider}")
            
            for i, message in enumerate(progress_messages):
                status_text.text(message)
                progress_bar.progress((i + 1) / len(progress_messages))
                
                if i == len(progress_messages) - 1:
                    # Call the workflow orchestration
                    logger.info("Invoking generate_posts_workflow")
                    generated_posts = generate_posts_workflow(
                        source_files=source_files,
                        brand_guide=brand_guide,
                        history_file=post_history,
                        provider=selected_provider,
                        api_key=api_key,
                        platform=target_platform,
                        count=post_count,
                        advanced_settings=advanced_settings
                    )
                    logger.info(f"Workflow completed successfully: generated {len(generated_posts)} posts")
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Update session state with generated posts
            st.session_state.generated_posts = generated_posts
            st.session_state.editing_posts = generated_posts.copy()
            st.session_state.generation_timestamp = datetime.now().isoformat()
            st.session_state.target_platform = target_platform
            st.session_state.generation_in_progress = False
            
            # Success feedback with details
            success_msg = f"🎉 Successfully generated {len(generated_posts)} posts for {target_platform}!"
            if brand_guide:
                success_msg += " Brand guidelines applied."
            if post_history:
                success_msg += " Style learned from post history."
            
            st.success(success_msg)
            st.balloons()
            
        except Exception as e:
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Log the error for debugging
            logger.error(f"Post generation failed: {str(e)}", exc_info=True)
            
            # Enhanced error handling with specific error types
            error_message = str(e).lower()
            
            if "authentication" in error_message or "api key" in error_message:
                logger.warning(f"Authentication error during generation: {str(e)}")
                st.error("🔑 **Authentication Error:** Please check your API key and try again.")
                st.info("💡 Make sure your API key is valid and has sufficient credits.")
            elif "rate limit" in error_message or "quota" in error_message:
                logger.warning(f"Rate limit exceeded during generation: {str(e)}")
                st.error("⏰ **Rate Limit Exceeded:** Please wait a moment before trying again.")
                st.info("💡 Consider reducing the number of posts or trying again later.")
            elif "network" in error_message or "connection" in error_message:
                logger.warning(f"Network error during generation: {str(e)}")
                st.error("🌐 **Network Error:** Please check your internet connection and try again.")
            elif "timeout" in error_message:
                logger.warning(f"Timeout error during generation: {str(e)}")
                st.error("⏱️ **Request Timeout:** The request took too long. Try reducing the number of posts.")
            else:
                logger.error(f"Unexpected error during generation: {str(e)}")
                st.error(f"❌ **Generation Error:** {str(e)}")
                st.info("💡 Please check your inputs and try again. If the problem persists, try a different LLM provider.")
            
            st.session_state.generation_in_progress = False
        
        st.rerun()

# Generate New Posts Button (only show if posts exist)
if st.session_state.generated_posts:
    if st.button("🔄 Generate New Posts", use_container_width=True):
        reset_generation_state()
        st.rerun()

# Dynamic Post Display and Editing Section
if st.session_state.generated_posts:
    st.markdown("---")
    st.subheader("Step 5: Review, Edit, and Manage Posts")
    
    # Generation metadata display
    if st.session_state.generation_timestamp and st.session_state.target_platform:
        timestamp = st.session_state.generation_timestamp.replace('T', ' at ').split('.')[0]
        st.info(f"📅 Generated {len(st.session_state.generated_posts)} posts for {st.session_state.target_platform} on {timestamp}")
    
    # Dynamic post editing interface
    for i, post in enumerate(st.session_state.generated_posts):
        st.markdown(f"### Post {i + 1}")
        
        # Post editing text area
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Get current post content
            current_post = st.session_state.editing_posts[i] if i < len(st.session_state.editing_posts) else post
            
            edited_post = st.text_area(
                f"Post {i + 1} Content",
                value=current_post,
                height=120,
                key=f"post_{i}",
                max_chars=3000,
                help="Edit your post content. Changes are saved automatically.",
                label_visibility="collapsed"
            )
            
            # Update editing posts in real-time
            if i < len(st.session_state.editing_posts):
                st.session_state.editing_posts[i] = edited_post
            else:
                st.session_state.editing_posts.append(edited_post)
        
        with col2:
            # Post management buttons
            st.markdown("**Actions**")
            
            # Delete button
            if st.button(f"🗑️ Delete", key=f"delete_{i}", help="Delete this post"):
                if len(st.session_state.editing_posts) > 1:
                    st.session_state.generated_posts.pop(i)
                    st.session_state.editing_posts.pop(i)
                    st.rerun()
                else:
                    st.warning("Cannot delete the last remaining post")
            
            # Move up button (except for first post)
            if i > 0 and st.button(f"↑ Up", key=f"up_{i}", help="Move post up"):
                # Swap with previous post
                st.session_state.generated_posts[i], st.session_state.generated_posts[i-1] = \
                    st.session_state.generated_posts[i-1], st.session_state.generated_posts[i]
                st.session_state.editing_posts[i], st.session_state.editing_posts[i-1] = \
                    st.session_state.editing_posts[i-1], st.session_state.editing_posts[i]
                st.rerun()
                
            # Move down button (except for last post)
            if i < len(st.session_state.generated_posts) - 1 and st.button(f"↓ Down", key=f"down_{i}", help="Move post down"):
                # Swap with next post
                st.session_state.generated_posts[i], st.session_state.generated_posts[i+1] = \
                    st.session_state.generated_posts[i+1], st.session_state.generated_posts[i]
                st.session_state.editing_posts[i], st.session_state.editing_posts[i+1] = \
                    st.session_state.editing_posts[i+1], st.session_state.editing_posts[i]
                st.rerun()
            
            # Copy button
            if st.button(f"📋 Copy", key=f"copy_{i}", help="Copy post to clipboard"):
                st.code(edited_post, language="text")
                st.success("Post content displayed above - you can copy it manually")
        
        # Character count and platform validation
        char_count = len(edited_post)
        platform_limit = get_platform_character_limit(st.session_state.target_platform or "LinkedIn")
        
        if char_count > platform_limit:
            excess = char_count - platform_limit
            st.warning(f"⚠️ Post {i + 1} exceeds {st.session_state.target_platform} character limit by {excess} characters ({char_count}/{platform_limit})")
        else:
            st.caption(f"✅ {char_count}/{platform_limit} characters")
        
        # Check for empty posts
        if not edited_post.strip():
            st.error(f"❌ Post {i + 1} is empty. Please add content or delete this post.")
        
        st.markdown("---")
    
    # Post management summary
    st.subheader("Post Management Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Posts", len(st.session_state.editing_posts))
    
    with col2:
        empty_posts = sum(1 for post in st.session_state.editing_posts if not post.strip())
        st.metric("Empty Posts", empty_posts)
    
    with col3:
        platform_limit = get_platform_character_limit(st.session_state.target_platform or "LinkedIn")
        over_limit = sum(1 for post in st.session_state.editing_posts if len(post) > platform_limit)
        st.metric("Over Limit", over_limit)
    
    # Export section
    st.markdown("---")
    st.subheader("Step 6: Export Posts")
    
    # Get export statistics
    stats = get_export_statistics(st.session_state.editing_posts)
    
    # Display export statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Posts", stats['total_posts'])
    with col2:
        st.metric("Valid Posts", stats['valid_posts'])
    with col3:
        st.metric("Avg Length", f"{stats['average_length']} chars")
    with col4:
        size_display = f"{stats['estimated_file_size_kb']} KB"
        if stats['estimated_file_size_kb'] > 1000:
            size_display = f"{stats['estimated_file_size_kb']/1024:.1f} MB"
        st.metric("Est. File Size", size_display)
    
    # Validate export data
    is_valid, validation_issues = validate_export_data(
        st.session_state.editing_posts, 
        st.session_state.target_platform
    )
    
    # Display validation results
    warnings = [issue for issue in validation_issues if issue.startswith("Warning:")]
    errors = [issue for issue in validation_issues if not issue.startswith("Warning:")]
    
    for error in errors:
        st.error(f"❌ {error}")
    
    for warning in warnings:
        st.warning(f"⚠️ {warning}")
    
    if is_valid and stats['valid_posts'] > 0:
        st.success(f"✅ Ready to export {stats['valid_posts']} posts!")
        
        # Export options
        with st.expander("🔧 Export Options", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                include_metadata = st.checkbox(
                    "Include Metadata Columns",
                    value=False,
                    help="Add platform, post_number, and character_count columns"
                )
                
                show_preview = st.checkbox(
                    "Show Export Preview",
                    value=False,
                    help="Preview the export data before download"
                )
            
            with col2:
                encoding_option = st.selectbox(
                    "File Encoding",
                    ["UTF-8", "UTF-16", "ISO-8859-1"],
                    index=0,
                    help="Choose character encoding for the CSV file"
                )
                
                timestamp_format = st.selectbox(
                    "Timestamp Format",
                    ["ISO 8601", "RFC 3339", "Human Readable"],
                    index=0,
                    help="Select timestamp format for export"
                )
        
        # Generate CSV data for export
        try:
            csv_string, filename = create_csv_export(
                st.session_state.editing_posts,
                st.session_state.target_platform,
                include_metadata=include_metadata
            )
            
            # Show preview if requested
            if show_preview:
                st.markdown("### 📋 Export Preview")
                
                # Parse CSV to show preview
                import io
                preview_df = pd.read_csv(io.StringIO(csv_string))
                
                # Show first few rows
                st.dataframe(preview_df.head(min(5, len(preview_df))), use_container_width=True)
                
                if len(preview_df) > 5:
                    st.caption(f"Showing first 5 rows of {len(preview_df)} total rows")
            
            # Export buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Main CSV export button
                file_size_warning = ""
                if stats['estimated_file_size_kb'] > 1000:  # > 1MB
                    file_size_warning = f" (⚠️ ~{stats['estimated_file_size_kb']/1024:.1f}MB)"
                
                download_label = f"📄 Export to CSV{file_size_warning}"
                download_help = "Download your edited posts as a CSV file"
                if file_size_warning:
                    download_help += f". Large file warning: ~{stats['estimated_file_size_kb']/1024:.1f}MB"
                
                st.download_button(
                    label=download_label,
                    data=csv_string,
                    file_name=filename,
                    mime="text/csv",
                    help=download_help,
                    use_container_width=True
                )
            
            with col2:
                # Copy all posts button
                if st.button("📋 Copy All Posts", use_container_width=True):
                    valid_posts = [post for post in st.session_state.editing_posts if post.strip()]
                    all_posts_text = "\n\n---\n\n".join([f"Post {i+1}:\n{post}" for i, post in enumerate(valid_posts)])
                    st.code(all_posts_text, language="text")
                    st.success("All posts displayed above - you can copy them manually")
            
            with col3:
                # Export with metadata button (if not already selected)
                if not include_metadata:
                    try:
                        csv_with_metadata, filename_metadata = create_csv_export(
                            st.session_state.editing_posts,
                            st.session_state.target_platform,
                            include_metadata=True
                        )
                        
                        st.download_button(
                            label="📊 Export with Metadata",
                            data=csv_with_metadata,
                            file_name=filename_metadata.replace('.csv', '_metadata.csv'),
                            mime="text/csv",
                            help="Export with additional columns: platform, post_number, character_count",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error creating metadata export: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error preparing export: {str(e)}")
            st.info("Please check your posts and try again")
    
    elif stats['valid_posts'] == 0:
        st.info("📝 No valid posts to export. Please add content to your posts first.")
    else:
        st.error("❌ Export validation failed. Please fix the issues above before exporting.")

else:
    # Empty state when no posts are generated
    st.info("📝 No posts generated yet. Use the 'Generate Posts' button above to create posts based on your inputs.")

st.markdown("---")
st.caption("Auto Post Generator MVP - Phase 5: CSV Export Functionality")