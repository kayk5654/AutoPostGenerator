import streamlit as st
import pandas as pd
from config import LLM_PROVIDERS, TARGET_PLATFORMS, SUPPORTED_TEXT_FORMATS, SUPPORTED_HISTORY_FORMATS

st.set_page_config(
    page_title="Auto Post Generator",
    page_icon="📝",
    layout="wide"
)

st.title("Auto Post Generator")

if 'generated_posts' not in st.session_state:
    st.session_state.generated_posts = []
if 'editing_posts' not in st.session_state:
    st.session_state.editing_posts = []
if 'generation_timestamp' not in st.session_state:
    st.session_state.generation_timestamp = None
if 'target_platform' not in st.session_state:
    st.session_state.target_platform = None

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

if st.button("Generate Posts", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your API key")
    elif not source_files:
        st.error("Please upload at least one source file")
    else:
        with st.spinner("Generating posts... This may take a moment."):
            st.success(f"Ready to generate {post_count} posts for {target_platform} using {selected_provider}")
            st.info("LLM integration will be implemented in Phase 3")
            
            st.session_state.generated_posts = [
                f"Sample post {i+1} for {target_platform} - This is a placeholder post that will be replaced with AI-generated content in Phase 3."
                for i in range(post_count)
            ]
            st.session_state.editing_posts = st.session_state.generated_posts.copy()
            st.session_state.target_platform = target_platform
            
            st.rerun()

if st.session_state.generated_posts:
    st.markdown("---")
    st.subheader("Step 5: Preview, Edit, and Export")
    
    st.success(f"Generated {len(st.session_state.generated_posts)} posts!")
    
    for i, post in enumerate(st.session_state.generated_posts):
        st.markdown(f"**Post {i+1}**")
        edited_post = st.text_area(
            f"Edit Post {i+1}",
            value=post,
            height=100,
            key=f"post_{i}",
            label_visibility="collapsed"
        )
        if f"post_{i}" in st.session_state:
            st.session_state.editing_posts[i] = st.session_state[f"post_{i}"]
    
    st.markdown("**Export Options**")
    if st.button("Export to CSV", type="secondary"):
        st.success("CSV export functionality will be implemented in Phase 5")
        st.info(f"Will export {len(st.session_state.editing_posts)} edited posts for {st.session_state.target_platform}")

st.markdown("---")
st.caption("Auto Post Generator MVP - Phase 1: Project Setup & UI Foundation")