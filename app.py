import streamlit as st
import pandas as pd
from datetime import datetime
from config import LLM_PROVIDERS, TARGET_PLATFORMS, SUPPORTED_TEXT_FORMATS, SUPPORTED_HISTORY_FORMATS
from services.post_service import generate_posts_workflow

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

# Initialize session state
initialize_session_state()

st.markdown("---")
st.subheader("Step 1: Configure LLM Provider")

col1, col2 = st.columns(2)
with col1:
    selected_provider = st.selectbox(
        "Select LLM Provider",
        LLM_PROVIDERS,
        help="Choose your preferred AI provider"
    )

with col2:
    api_key = st.text_input(
        "Enter Your API Key",
        type="password",
        help="Your API key will only be used for this session and not stored"
    )

st.markdown("---")
st.subheader("Step 2: Provide Inputs")

st.markdown("**1. Upload Information Source Files**")
source_files = st.file_uploader(
    "Choose source files",
    type=['txt', 'docx', 'pdf', 'md'],
    accept_multiple_files=True,
    help=f"Supported formats: {', '.join(SUPPORTED_TEXT_FORMATS)}"
)

st.markdown("**2. Upload Brand Guide File**")
brand_guide = st.file_uploader(
    "Choose brand guide file",
    type=['txt', 'docx', 'pdf', 'md'],
    help=f"Supported formats: {', '.join(SUPPORTED_TEXT_FORMATS)}"
)

st.markdown("**3. Upload Previous Posts History**")
post_history = st.file_uploader(
    "Choose post history file",
    type=['xlsx'],
    help=f"Supported formats: {', '.join(SUPPORTED_HISTORY_FORMATS)}"
)

st.markdown("---")
st.subheader("Step 3: Define Generation Parameters")

col3, col4 = st.columns(2)
with col3:
    post_count = st.number_input(
        "4. Number of Posts to Generate",
        min_value=1,
        max_value=50,
        value=5,
        help="Number of social media posts to generate"
    )

with col4:
    target_platform = st.selectbox(
        "5. Select Target Platform",
        TARGET_PLATFORMS,
        help="Choose the social media platform for optimization"
    )

st.markdown("---")
st.subheader("Step 4: Generate")

# Generate Posts Button
if st.button(
    "🚀 Generate Posts", 
    type="primary", 
    use_container_width=True,
    disabled=st.session_state.generation_in_progress
):
    # Input validation
    if not api_key or not api_key.strip():
        st.error("🔑 Please enter your API key")
    elif not source_files:
        st.error("📁 Please upload at least one source file")
    elif not selected_provider:
        st.error("🤖 Please select an LLM provider")
    elif not target_platform:
        st.error("🎯 Please select a target platform")
    elif post_count < 1 or post_count > 50:
        st.error("📊 Post count must be between 1 and 50")
    else:
        # Set generation in progress
        st.session_state.generation_in_progress = True
        
        # Store generation settings
        st.session_state.last_generation_settings = {
            'provider': selected_provider,
            'platform': target_platform,
            'count': post_count,
            'timestamp': datetime.now().isoformat()
        }
        
        with st.spinner("🚀 Generating posts... This may take a moment."):
            try:
                # Call the workflow orchestration
                generated_posts = generate_posts_workflow(
                    source_files=source_files,
                    brand_guide=brand_guide,
                    history_file=post_history,
                    provider=selected_provider,
                    api_key=api_key,
                    platform=target_platform,
                    count=post_count
                )
                
                # Update session state with generated posts
                st.session_state.generated_posts = generated_posts
                st.session_state.editing_posts = generated_posts.copy()
                st.session_state.generation_timestamp = datetime.now().isoformat()
                st.session_state.target_platform = target_platform
                st.session_state.generation_in_progress = False
                
                st.success(f"🎉 Successfully generated {len(generated_posts)} posts for {target_platform}!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error generating posts: {str(e)}")
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
    
    # Validation before export
    can_export = True
    export_warnings = []
    
    if empty_posts > 0:
        export_warnings.append(f"⚠️ {empty_posts} post(s) are empty")
        can_export = False
    
    if over_limit > 0:
        export_warnings.append(f"⚠️ {over_limit} post(s) exceed platform character limits")
    
    if export_warnings:
        for warning in export_warnings:
            st.warning(warning)
    
    if can_export:
        st.success("✅ All posts are ready for export!")
    
    # Export buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export to CSV", type="secondary", disabled=not can_export):
            st.success("CSV export functionality will be implemented in Phase 5")
            st.info(f"Will export {len(st.session_state.editing_posts)} edited posts for {st.session_state.target_platform}")
    
    with col2:
        if st.button("📋 Copy All Posts", disabled=not can_export):
            all_posts_text = "\n\n---\n\n".join([f"Post {i+1}:\n{post}" for i, post in enumerate(st.session_state.editing_posts) if post.strip()])
            st.code(all_posts_text, language="text")
            st.success("All posts displayed above - you can copy them manually")

else:
    # Empty state when no posts are generated
    st.info("📝 No posts generated yet. Use the 'Generate Posts' button above to create posts based on your inputs.")

st.markdown("---")
st.caption("Auto Post Generator MVP - Phase 4: Display, Edit, and State Management")